from flask import Flask, render_template, send_from_directory, request, jsonify, Response
import json
import os
import sys
import csv
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.config_service import ConfigService
from services.database_service import DatabaseService, DatabaseQueryError
from services.schedule_service import ScheduleService
from services.analytics_service import AnalyticsService
from services.ai_service import AIService, AIServiceError
from services.conversation_service import ConversationService

app = Flask(__name__, 
            template_folder='../static',
            static_folder='../static')

# Initialize services
try:
    config = ConfigService()
    db_service = DatabaseService(config)
    schedule_service = ScheduleService()
    analytics_service = AnalyticsService(db_service)
    ai_service = AIService(config)
    conversation_service = ConversationService(db_service)
except Exception as e:
    print(f"Error initializing services: {e}")
    config = None
    db_service = None
    schedule_service = None
    analytics_service = None
    ai_service = None
    conversation_service = None


@app.route('/')
def index():
    """Serve the main HTML interface."""
    if schedule_service:
        schedules = schedule_service.get_all_schedules()
        return render_template('index.html', schedules=json.dumps(schedules))
    return "Configuration error", 500


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('../static', path)


@app.route('/api/save', methods=['POST'])
def save():
    """Save daily progress data."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['date', 'mode', 'checked', 'done', 'total', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Save to database
        db_service.save_daily_log(data)
        
        return jsonify({'status': 'ok'}), 200
    
    except DatabaseQueryError as e:
        return jsonify({'error': 'Database temporarily unavailable'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
@app.route('/api/log', methods=['GET'])
def get_log():
    """Retrieve daily log for a specific date."""
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({'error': 'Missing date parameter'}), 400

        log = db_service.get_daily_log(date)
        if log:
            return jsonify(log), 200
        else:
            return jsonify({}), 200

    except DatabaseQueryError as e:
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/streaks', methods=['GET'])
def streaks():
    """Get current streak data."""
    try:
        streaks_data = analytics_service.calculate_streaks()
        return jsonify(streaks_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to calculate streaks'}), 500


@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Retrieve conversation history for a specific date."""
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({'error': 'Missing date parameter'}), 400
        
        messages = conversation_service.get_conversation(date)
        return jsonify({'messages': messages}), 200
    
    except DatabaseQueryError as e:
        return jsonify({'error': 'Failed to load conversation'}), 500
    except Exception as e:
        return jsonify({'error': 'Failed to load conversation'}), 500


@app.route('/api/coach', methods=['POST'])
def coach():
    """Generate end-of-day coaching feedback."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['date', 'mode', 'checked', 'score', 'total', 'done']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate date is not in future
        from datetime import datetime
        selected_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        today = datetime.now().date()
        if selected_date > today:
            return jsonify({'error': 'Cannot create logs for future dates'}), 400
        
        # Get context data
        streaks_data = analytics_service.calculate_streaks()
        history = db_service.get_history(days=7)
        blocks = schedule_service.get_blocks_for_mode(data['mode'])
        
        # Generate coaching message
        message = ai_service.generate_end_of_day_coaching(
            date=data['date'],
            mode=data['mode'],
            checked=data['checked'],
            score=data['score'],
            total=data['total'],
            done=data['done'],
            note=data.get('note', ''),
            streaks=streaks_data,
            history=history,
            blocks=blocks
        )
        
        # Save the coaching message to database
        data['coach_msg'] = message
        db_service.save_daily_log(data)
        
        return jsonify({'message': message}), 200
    
    except AIServiceError as e:
        print(f"AI Service Error: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Unexpected Error in /api/coach: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle conversational AI chat queries with persistence."""
    try:
        data = request.json
        
        # Validate required fields
        if 'message' not in data:
            return jsonify({'error': 'Missing required field: message'}), 400
        if 'date' not in data:
            return jsonify({'error': 'Missing required field: date'}), 400
        
        user_message = data['message']
        date = data['date']
        
        # Validate date is not in future
        from datetime import datetime
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        today = datetime.now().date()
        if selected_date > today:
            return jsonify({'error': 'Cannot create logs for future dates'}), 400
        
        # Get context data
        history = db_service.get_history(days=14)
        streaks_data = analytics_service.calculate_streaks()
        
        # Generate chat response
        response = ai_service.generate_chat_response(
            user_message=user_message,
            history=history,
            streaks=streaks_data
        )
        
        # Save conversation
        conversation_service.save_message(date, 'user', user_message)
        conversation_service.save_message(date, 'coach', response)
        
        return jsonify({'response': response}), 200
    
    except AIServiceError as e:
        print(f"AI Service Error in chat: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Unexpected Error in /api/chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/export', methods=['GET'])
def export():
    """Export all daily logs to CSV."""
    try:
        logs = db_service.get_all_logs()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['date', 'mode', 'done', 'total', 'score_%', 'note', 'coach_message', 'saved_at'])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.get('date', ''),
                log.get('mode', ''),
                log.get('done', 0),
                log.get('total', 0),
                log.get('score', 0),
                log.get('note', ''),
                log.get('coach_msg', ''),
                log.get('created_at', '')
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=daily_log.csv'}
        )
    
    except Exception as e:
        return Response('Error exporting data', status=500)


# For Vercel
app = app

if __name__ == '__main__':
    port = config.get_port() if config else 5000
    app.run(debug=True, port=port)
