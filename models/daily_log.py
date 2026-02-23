from datetime import datetime
from typing import Optional, Dict, Any


class DailyLog:
    """Represents a single day's tracking data."""
    
    def __init__(
        self,
        date: str,
        mode: str,
        checked: Dict[str, bool],
        done: int,
        total: int,
        score: int,
        note: str = "",
        coach_msg: str = "",
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.date = date
        self.mode = mode
        self.checked = checked or {}
        self.done = done
        self.total = total
        self.score = score
        self.note = note
        self.coach_msg = coach_msg
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'date': self.date,
            'mode': self.mode,
            'checked': self.checked,
            'done': self.done,
            'total': self.total,
            'score': self.score,
            'note': self.note,
            'coach_msg': self.coach_msg,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DailyLog':
        """Create instance from dictionary."""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = datetime.now()
        
        return DailyLog(
            id=data.get('id'),
            date=data.get('date', ''),
            mode=data.get('mode', ''),
            checked=data.get('checked', {}),
            done=data.get('done', 0),
            total=data.get('total', 0),
            score=data.get('score', 0),
            note=data.get('note', ''),
            coach_msg=data.get('coach_msg', ''),
            created_at=created_at
        )
    
    def validate(self) -> bool:
        """Validate data integrity."""
        if not self.date:
            return False
        if self.mode not in ['morning_gym', 'evening_gym', 'no_gym']:
            return False
        if self.done < 0 or self.total < 0:
            return False
        if self.score < 0 or self.score > 100:
            return False
        return True
