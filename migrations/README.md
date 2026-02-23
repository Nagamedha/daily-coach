# Database Migrations

This directory contains SQL migrations for setting up the Daily Coach database schema.

## Overview

The Daily Coach app uses two main tables:
1. **daily_log** - Automatically created on first use
2. **conversations** - Requires manual migration (one-time setup)

## Required Migration

### conversations table

This table stores chat messages between the user and coach, organized by date.

**File:** `create_conversations_table.sql`

**Schema:**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'coach')),
    text TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_date ON conversations(date);
CREATE INDEX idx_conversations_date_timestamp ON conversations(date, timestamp);
```

## How to Run Migration

### Step 1: Access Supabase SQL Editor

1. Go to your Supabase project dashboard
2. Click "SQL Editor" in the left sidebar
3. Click "New Query"

### Step 2: Execute Migration

1. Open `create_conversations_table.sql` in this directory
2. Copy the entire SQL content
3. Paste into the Supabase SQL Editor
4. Click "Run" or press `Ctrl+Enter`

### Step 3: Verify

You should see:
```
Success. No rows returned
```

Check that the table was created:
```sql
SELECT * FROM conversations LIMIT 1;
```

## Table Details

### conversations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| date | DATE | NOT NULL | Date the conversation is associated with |
| sender | VARCHAR(10) | NOT NULL, CHECK | Either 'user' or 'coach' |
| text | TEXT | NOT NULL | Message content |
| timestamp | TIMESTAMP | NOT NULL | When the message was sent |
| created_at | TIMESTAMP | DEFAULT NOW() | When the record was created |

**Indexes:**
- `idx_conversations_date` - Fast lookups by date
- `idx_conversations_date_timestamp` - Fast ordered retrieval

**Purpose:**
- Stores all chat messages between user and coach
- Organized by date for easy retrieval
- Maintains chronological order via timestamp
- Enables conversation persistence across sessions

### daily_log

This table is automatically created by the application on first use. No migration needed.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| date | DATE | Unique date (YYYY-MM-DD) |
| mode | VARCHAR | Schedule mode (morning_gym, evening_gym, no_gym) |
| checked | JSONB | Completed blocks as JSON |
| done | INTEGER | Number of tasks completed |
| total | INTEGER | Total number of tasks |
| score | INTEGER | Completion percentage (0-100) |
| note | TEXT | User's daily note |
| coach_msg | TEXT | AI coaching message |
| created_at | TIMESTAMP | Record creation time |

**Purpose:**
- Stores daily schedule completion data
- One entry per date (upsert on conflict)
- Tracks progress and coaching feedback

## Troubleshooting

### Error: "relation already exists"
**Cause:** Table was already created  
**Solution:** This is fine! The migration uses `CREATE TABLE IF NOT EXISTS`

### Error: "permission denied"
**Cause:** Insufficient database permissions  
**Solution:** Ensure you're using the correct Supabase credentials with admin access

### Error: "syntax error"
**Cause:** SQL not copied correctly  
**Solution:** Copy the entire contents of `create_conversations_table.sql` including all semicolons

## Verifying Migration Success

Run this query in Supabase SQL Editor:

```sql
-- Check table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'conversations';

-- Check indexes exist
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'conversations';

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversations'
ORDER BY ordinal_position;
```

Expected output:
- Table name: `conversations`
- Indexes: `idx_conversations_date`, `idx_conversations_date_timestamp`
- Columns: id, date, sender, text, timestamp, created_at

## Migration Files

### Included Files

- **create_conversations_table.sql** - Main migration (REQUIRED)
- **README.md** - This file

### Not Included (Development Only)

These helper scripts are excluded from the repository as they're not needed for deployment:
- `create_table_direct.py` - Python script for direct table creation
- `execute_migration.py` - Alternative migration runner
- `run_migration.py` - Migration verification script

## Post-Migration

After running the migration:

1. ✅ The conversations table is ready
2. ✅ Chat messages will persist across sessions
3. ✅ Conversation history loads when switching dates
4. ✅ No further database setup needed

## Rollback (if needed)

To remove the conversations table:

```sql
DROP TABLE IF EXISTS conversations CASCADE;
```

**Warning:** This will delete all chat history!

---

**Migration required:** One-time setup  
**Estimated time:** < 1 minute  
**Difficulty:** Easy (copy-paste SQL)
