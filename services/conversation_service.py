from typing import List, Dict, Any
from datetime import datetime
from services.database_service import DatabaseService, DatabaseQueryError


class ConversationService:
    """Manages chat conversation persistence."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize with DatabaseService dependency.
        
        Args:
            db_service: DatabaseService instance for database operations
        """
        self.db_service = db_service
    
    def save_message(self, date: str, sender: str, text: str) -> None:
        """Save a single chat message to the conversations table.
        
        Args:
            date: The date this message is associated with (YYYY-MM-DD format)
            sender: Who sent the message ('user' or 'coach')
            text: The message content
            
        Raises:
            DatabaseQueryError: If the database insert fails
        """
        try:
            message_data = {
                'date': date,
                'sender': sender,
                'text': text,
                'timestamp': datetime.now().isoformat()
            }
            
            self.db_service.client.table('conversations').insert(message_data).execute()
        except Exception as e:
            raise DatabaseQueryError(f"Failed to save conversation message: {str(e)}")
    
    def get_conversation(self, date: str) -> List[Dict[str, Any]]:
        """Retrieve all messages for a specific date, ordered by timestamp.
        
        Args:
            date: The date to retrieve messages for (YYYY-MM-DD format)
            
        Returns:
            List of message dictionaries with keys: id, date, sender, text, timestamp, created_at
            Returns empty list if no messages exist for the date
            
        Raises:
            DatabaseQueryError: If the database query fails
        """
        try:
            response = self.db_service.client.table('conversations') \
                .select('*') \
                .eq('date', date) \
                .order('timestamp', desc=False) \
                .execute()
            
            return response.data or []
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve conversation: {str(e)}")
