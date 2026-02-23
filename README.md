# Daily Coach - AI-Powered Schedule Tracker

An intelligent personal productivity application that helps you track your daily schedule, maintain accountability, and achieve your goals through AI-powered coaching.

## 🎯 What is Daily Coach?

Daily Coach is a web application that combines schedule tracking with an AI coach that provides personalized, reality-based feedback. Unlike generic productivity apps, Daily Coach acts as a strict but supportive personal trainer who:

- Tracks your daily task completion across different schedule modes
- Provides honest, consequence-based feedback when you slip
- Celebrates your wins with genuine appreciation
- Maintains conversation history for continuous accountability
- Uses only actual data (no hallucinations or made-up information)

## ✨ Key Features

### 1. **Daily Schedule Tracking**
- Three schedule modes: Morning Gym, Evening Gym, No Gym/Weekend
- Track completion of time-blocked tasks
- Add personal notes for each day
- Date picker restricted to today and past dates only

### 2. **AI Coach with Strict Trainer Personality**
- **Low Performance (< 50%):** Shows real consequences (delayed job search, slower fitness progress)
- **Medium Performance (50-79%):** Balanced feedback with improvement strategies
- **High Performance (≥ 80%):** Genuine appreciation and confidence boost
- Rejects off-topic questions professionally
- Only references actual database data

### 3. **Conversation Persistence**
- Chat with your coach about progress and get data-driven insights
- Conversations save per date and persist across sessions
- Switch between dates to review past coaching discussions

### 4. **Streak Tracking**
- Monitor gym days, study days, and job application days
- Visual streak display for motivation
- Historical data analysis

### 5. **Data Export**
- Export all logs to CSV for external analysis
- Complete history with scores, notes, and coaching messages

## 🏗️ Architecture

### Tech Stack
- **Backend:** Python 3.8+, Flask
- **Database:** Supabase (PostgreSQL)
- **AI:** OpenAI API (gpt-4o-mini)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Deployment:** Vercel (serverless)

### Project Structure
```
daily-coach/
├── api/                    # Flask API endpoints
│   ├── __init__.py
│   └── index.py           # Main application routes
├── services/              # Business logic layer
│   ├── ai_service.py      # OpenAI integration
│   ├── analytics_service.py  # Streak calculations
│   ├── config_service.py  # Environment configuration
│   ├── conversation_service.py  # Chat persistence
│   ├── database_service.py  # Supabase operations
│   └── schedule_service.py  # Schedule management
├── models/                # Data models
│   ├── daily_log.py       # Daily log model
│   └── schedule.py        # Schedule definitions
├── static/                # Frontend assets
│   ├── index.html         # Main UI
│   └── styles.css         # Styling
├── migrations/            # Database migrations
│   ├── create_conversations_table.sql
│   └── README.md
├── tests/                 # Test suite
│   └── README.md          # Testing documentation
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Supabase account (free tier works)
- OpenAI API key with credits

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/daily-coach.git
   cd daily-coach
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   
   # OpenAI Configuration
   CLAUDE_API_KEY=your-openai-api-key
   CLAUDE_MODEL=gpt-4o-mini
   ```

5. **Set up database**
   
   Run the SQL migration in your Supabase SQL Editor:
   ```bash
   # Copy contents of migrations/create_conversations_table.sql
   # Paste and run in Supabase SQL Editor
   ```
   
   The `daily_log` table is created automatically on first use.

6. **Run the application**
   ```bash
   python api/index.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Your Supabase project URL | Yes | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/public key | Yes | `eyJhbGc...` |
| `CLAUDE_API_KEY` | OpenAI API key | Yes | `sk-proj-...` |
| `CLAUDE_MODEL` | OpenAI model to use | Yes | `gpt-4o-mini` |
| `PORT` | Server port | No | `5000` (default) |
| `DEBUG_MODE` | Enable debug mode | No | `false` (default) |

**⚠️ Security Note:** Never commit your `.env` file to Git! It's already in `.gitignore`.

### Database Schema

#### `daily_log` table
Stores daily schedule completion data.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| date | DATE | Unique date (YYYY-MM-DD) |
| mode | VARCHAR | Schedule mode |
| checked | JSONB | Completed blocks |
| done | INTEGER | Tasks completed |
| total | INTEGER | Total tasks |
| score | INTEGER | Completion percentage |
| note | TEXT | User's daily note |
| coach_msg | TEXT | AI coaching message |
| created_at | TIMESTAMP | Record creation time |

#### `conversations` table
Stores chat messages between user and coach.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| date | DATE | Associated date |
| sender | VARCHAR | 'user' or 'coach' |
| text | TEXT | Message content |
| timestamp | TIMESTAMP | Message time |
| created_at | TIMESTAMP | Record creation time |

## 💡 How It Works

### Workflow

1. **Select Date** → Choose today or a past date
2. **Choose Schedule Mode** → Morning Gym, Evening Gym, or No Gym
3. **Track Progress** → Check off completed tasks throughout the day
4. **Add Notes** → Optional personal reflections
5. **Get Coaching** → Click "How did I do today?" for AI feedback
6. **Chat Anytime** → Ask questions about your progress
7. **Review History** → Switch dates to see past performance

### AI Coach Behavior

The coach uses a **strict but supportive trainer** approach:

**For Low Scores (< 50%):**
> "You struggled today, completing only 2 out of 8 blocks. Missing your workouts means you're slowing down your fitness journey, and skipping study time is pushing your job applications further away. Remember why you started this - you want that job, you want to be fit. Tomorrow, commit to at least 5 blocks. No excuses."

**For High Scores (≥ 80%):**
> "You crushed it today! Completing 7 out of 8 blocks shows real discipline and commitment. This is exactly the kind of consistency that will get you that job and keep you fit. Your gym streak is at 5 days now - that's momentum. Keep this energy going tomorrow!"

**For Off-Topic Questions:**
> "That's not my role. I'm your healthy lifestyle coach here to help you follow your daily schedule, get a job, be fit, and have a healthy lifestyle."

## 🎨 Features in Detail

### Date Restrictions
- Frontend: Date picker `max` attribute set to today
- Backend: API validates dates and rejects future dates with 400 error
- Allows updating historical data anytime

### Conversation Persistence
- Each date has its own conversation thread
- Messages stored with timestamps for chronological order
- Switching dates loads the correct conversation
- Conversations persist across browser sessions

### Data Accuracy
- AI only references actual database records
- No hallucinations or made-up statistics
- Specific dates and numbers in all responses
- If data is missing, coach acknowledges it

## 🧪 Testing

See [tests/README.md](tests/README.md) for comprehensive testing documentation.

**Quick test:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_integration_end_to_end.py -v
```

## 🚢 Deployment

### Deploy to Vercel

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Framework Preset: **Other**

3. **Add Environment Variables**
   
   In Vercel project settings, add all 4 environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `CLAUDE_API_KEY`
   - `CLAUDE_MODEL`
   
   Enable for: Production, Preview, Development

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app will be live at `https://your-project.vercel.app`

5. **Auto-Deploy**
   - Every push to `main` branch triggers automatic deployment
   - No manual steps needed for updates

## 🔮 Future Enhancements

### Planned Features
- [ ] Sleep/wake time tracking with streaks
- [ ] Weekly and monthly progress reports
- [ ] Conversation summarization for long histories
- [ ] Mobile-responsive design improvements
- [ ] Dark mode support
- [ ] Multiple schedule templates
- [ ] Goal setting and milestone tracking
- [ ] Data visualization (charts/graphs)
- [ ] Email/SMS reminders
- [ ] Multi-user support with authentication

### Potential Integrations
- Google Calendar sync
- Notion integration
- Habit tracking apps
- Fitness tracker APIs
- Job board integrations

## 🐛 Challenges & Solutions

### Challenge 1: "How did I do today?" showing undefined
**Problem:** Frontend wasn't handling API response structure correctly  
**Solution:** Added proper response parsing with fallbacks for both `message` and `error` fields

### Challenge 2: AI hallucinating gym/study days
**Problem:** AI was making up statistics not in the database  
**Solution:** Rewrote prompts to explicitly label "ACTUAL DATA (from database)" and instruct AI to never invent numbers

### Challenge 3: Conversation not persisting
**Problem:** Chat messages weren't being saved to database  
**Solution:** Created ConversationService and integrated save operations into chat flow

### Challenge 4: Users creating logs for future dates
**Problem:** No validation on date selection  
**Solution:** Added frontend `max` attribute and backend date validation with clear error messages

### Challenge 5: Database upsert conflicts
**Problem:** Duplicate key errors when saving same date twice  
**Solution:** Added `on_conflict='date'` parameter to upsert operation

## 🤝 Contributing

This is a personal project, but contributions are welcome! Feel free to:
- Fork the repository
- Create a feature branch
- Submit a pull request

## 📄 License

MIT License - feel free to use and modify for your own needs.

## 🙏 Acknowledgments

- OpenAI for the GPT-4o-mini API
- Supabase for the database platform
- Vercel for serverless deployment

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the [tests/README.md](tests/README.md) for testing guidance
- Review [migrations/README.md](migrations/README.md) for database setup

---

**Built with ❤️ to help maintain discipline and achieve goals.**

*Last updated: February 2026*
