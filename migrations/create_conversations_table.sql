-- Migration: Create conversations table for storing chat history
-- Date: 2024
-- Requirements: 6.1

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'coach')),
    text TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_conversations_date ON conversations(date);
CREATE INDEX IF NOT EXISTS idx_conversations_date_timestamp ON conversations(date, timestamp);

-- Add comment to table
COMMENT ON TABLE conversations IS 'Stores chat conversation history between user and coach, organized by date';
COMMENT ON COLUMN conversations.date IS 'The date this conversation is associated with';
COMMENT ON COLUMN conversations.sender IS 'Who sent the message: user or coach';
COMMENT ON COLUMN conversations.text IS 'The message content';
COMMENT ON COLUMN conversations.timestamp IS 'When the message was sent';
