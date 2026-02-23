from typing import Dict, List
from services.database_service import DatabaseService


class AnalyticsService:
    """Calculate streaks and provide analytics data."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize with database service."""
        self.db_service = db_service
    
    def calculate_streaks(self) -> Dict[str, int]:
        """Returns {gym_days, study_days, job_days}."""
        try:
            checked_data = self.db_service.get_checked_data()
            
            gym_days = 0
            study_days = 0
            job_days = 0
            
            for log in checked_data:
                checked = log.get('checked', {})
                
                # Handle case where checked might be a string (shouldn't happen but be safe)
                if isinstance(checked, str):
                    try:
                        import json
                        checked = json.loads(checked)
                    except:
                        checked = {}
                
                # Count gym days
                if checked.get('gym', False):
                    gym_days += 1
                
                # Count study days (any of study0, study1, study2)
                if any(checked.get(f'study{i}', False) for i in ['0', '1', '2']):
                    study_days += 1
                
                # Count job application days
                if checked.get('jobs', False):
                    job_days += 1
            
            return {
                'gym_days': gym_days,
                'study_days': study_days,
                'job_days': job_days
            }
        except Exception as e:
            # Return zeros on error
            return {
                'gym_days': 0,
                'study_days': 0,
                'job_days': 0
            }
    
    def get_completion_rate(self, days: int = 7) -> float:
        """Calculate average completion rate over period."""
        try:
            history = self.db_service.get_history(days)
            if not history:
                return 0.0
            
            total_score = sum(log.get('score', 0) for log in history)
            return total_score / len(history)
        except:
            return 0.0
    
    def identify_weak_blocks(self) -> List[str]:
        """Identify most frequently missed blocks."""
        try:
            all_logs = self.db_service.get_all_logs()
            block_misses = {}
            
            for log in all_logs:
                checked = log.get('checked', {})
                
                # Handle case where checked might be a string
                if isinstance(checked, str):
                    try:
                        import json
                        checked = json.loads(checked)
                    except:
                        checked = {}
                
                # Count misses for each block
                for block_id, is_checked in checked.items():
                    if not is_checked:
                        block_misses[block_id] = block_misses.get(block_id, 0) + 1
            
            # Sort by miss count and return top 3
            sorted_blocks = sorted(block_misses.items(), key=lambda x: x[1], reverse=True)
            return [block_id for block_id, _ in sorted_blocks[:3]]
        except:
            return []
