import json
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from services.config_service import ConfigService
from models.daily_log import DailyLog


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class DatabaseQueryError(Exception):
    """Raised when database query fails."""
    pass


class DatabaseService:
    """Abstraction layer for Supabase PostgreSQL operations."""
    
    def __init__(self, config: ConfigService):
        """Initialize Supabase client."""
        self.config = config
        try:
            self.client: Client = create_client(
                config.get_supabase_url(),
                config.get_supabase_key()
            )
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to Supabase: {str(e)}")
    
    def init_schema(self) -> None:
        """Create tables if not exist."""
        # Supabase tables should be created via Supabase dashboard or migrations
        # This method is a placeholder for schema validation
        try:
            # Test connection by attempting a simple query
            self.client.table('daily_log').select('id').limit(1).execute()
        except Exception as e:
            raise DatabaseConnectionError(f"Database schema not initialized: {str(e)}")
    
    def save_daily_log(self, log_data: Dict[str, Any]) -> None:
        """Upsert daily log entry."""
        try:
            # Convert checked dict to JSON string for storage
            data_to_save = {
                'date': log_data.get('date'),
                'mode': log_data.get('mode'),
                'checked': json.dumps(log_data.get('checked', {})),
                'done': log_data.get('done', 0),
                'total': log_data.get('total', 0),
                'score': log_data.get('score', 0),
                'note': log_data.get('note', ''),
                'coach_msg': log_data.get('coach_msg', '')
            }
            
            # Upsert: insert or update on conflict with date as the unique key
            self.client.table('daily_log').upsert(data_to_save, on_conflict='date').execute()
        except Exception as e:
            raise DatabaseQueryError(f"Failed to save daily log: {str(e)}")
    
    def get_daily_log(self, date: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific day's log."""
        try:
            response = self.client.table('daily_log').select('*').eq('date', date).execute()
            if response.data and len(response.data) > 0:
                log = response.data[0]
                # Parse checked JSON string back to dict
                try:
                    log['checked'] = json.loads(log.get('checked', '{}'))
                except:
                    log['checked'] = {}
                return log
            return None
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve daily log: {str(e)}")
    
    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent history for AI context."""
        try:
            response = self.client.table('daily_log').select('*').order('date', desc=True).limit(days).execute()
            logs = response.data or []
            
            # Parse checked JSON for each log
            for log in logs:
                try:
                    log['checked'] = json.loads(log.get('checked', '{}'))
                except:
                    log['checked'] = {}
            
            return logs
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve history: {str(e)}")
    
    def get_all_logs(self) -> List[Dict[str, Any]]:
        """Get all logs for export."""
        try:
            response = self.client.table('daily_log').select('*').order('date', desc=False).execute()
            logs = response.data or []
            
            # Parse checked JSON for each log
            for log in logs:
                try:
                    log['checked'] = json.loads(log.get('checked', '{}'))
                except:
                    log['checked'] = {}
            
            return logs
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve all logs: {str(e)}")
    
    def get_checked_data(self) -> List[Dict[str, Any]]:
        """Get all checked data for streak calculation."""
        try:
            response = self.client.table('daily_log').select('date, checked').execute()
            logs = response.data or []
            
            # Parse checked JSON for each log
            for log in logs:
                try:
                    log['checked'] = json.loads(log.get('checked', '{}'))
                except:
                    log['checked'] = {}
            
            return logs
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve checked data: {str(e)}")
