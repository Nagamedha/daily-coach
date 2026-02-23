from typing import Dict, List, Any, Optional
from models.schedule import Schedule, Block


class ScheduleService:
    """Manage schedule definitions and validation."""
    
    def __init__(self):
        """Initialize with schedule definitions."""
        self.schedules = self._load_schedules()
    
    def _load_schedules(self) -> Dict[str, Schedule]:
        """Load schedule definitions."""
        schedules_data = {
            "morning_gym": {
                "label": "Morning Gym",
                "blocks": [
                    {"id": "wakeup", "time": "7:00-8:00", "label": "Wake up, freshen up, eat a little, prep breakfast"},
                    {"id": "gym", "time": "8:00-9:00", "label": "Gym + relax"},
                    {"id": "morning", "time": "9:00-11:00", "label": "Breakfast, cook, wash dishes, check mails, bath"},
                    {"id": "parents1", "time": "11:00-11:30", "label": "Talk to parents"},
                    {"id": "study1", "time": "11:30-2:30", "label": "Study — 3 hrs"},
                    {"id": "lunch", "time": "2:30-3:30", "label": "Lunch + break"},
                    {"id": "study2", "time": "3:30-7:30", "label": "Study — 4 hrs"},
                    {"id": "dinner_prep", "time": "7:30-8:00", "label": "Dinner prep, relax, next day meal prep"},
                    {"id": "jobs", "time": "8:00-9:00", "label": "Apply to jobs"},
                    {"id": "dinner", "time": "9:00-10:00", "label": "Dinner + social media"},
                    {"id": "parents2", "time": "10:00-11:00", "label": "Talk to parents, tech news"},
                    {"id": "together", "time": "11:00-12:00", "label": "Wind down, spend time together"},
                    {"id": "sleep", "time": "12:00-7:00", "label": "Sleep"},
                ]
            },
            "evening_gym": {
                "label": "Evening Gym",
                "blocks": [
                    {"id": "wakeup", "time": "7:00-8:00", "label": "Wake up, freshen up"},
                    {"id": "study0", "time": "8:00-10:00", "label": "Study — 2 hrs"},
                    {"id": "morning", "time": "10:00-11:00", "label": "Breakfast, attend interviews, check mails"},
                    {"id": "parents1", "time": "11:00-11:30", "label": "Talk to parents"},
                    {"id": "study1", "time": "11:30-2:30", "label": "Study — 3 hrs"},
                    {"id": "lunch", "time": "2:30-3:30", "label": "Lunch + break"},
                    {"id": "dinner_prep", "time": "3:30-5:30", "label": "Dinner prep"},
                    {"id": "gym", "time": "5:30-6:30", "label": "Gym + bath"},
                    {"id": "jobs", "time": "6:30-8:30", "label": "Apply to jobs"},
                    {"id": "meal_prep", "time": "8:30-9:00", "label": "Next day meal prep"},
                    {"id": "dinner", "time": "9:00-10:00", "label": "Dinner, wash dishes, watch TV"},
                    {"id": "parents2", "time": "10:00-11:00", "label": "Talk to parents, social media, tech news"},
                    {"id": "together", "time": "11:00-12:00", "label": "Wind down, spend time together"},
                    {"id": "sleep", "time": "12:00-7:00", "label": "Sleep"},
                ]
            },
            "no_gym": {
                "label": "No Gym / Weekend",
                "blocks": [
                    {"id": "wakeup", "time": "9:00", "label": "Wake up (rest day — sleep in!)"},
                    {"id": "study1", "time": "Morning", "label": "Study — 1.5 hrs"},
                    {"id": "study2", "time": "Afternoon", "label": "Study — 1.5 hrs"},
                    {"id": "jobs", "time": "Evening", "label": "Apply to jobs — 1 hr"},
                    {"id": "relax", "time": "All day", "label": "Relax, cheat day, recharge!"},
                ]
            }
        }
        
        schedules = {}
        for mode, data in schedules_data.items():
            blocks = [Block.from_dict(b) for b in data['blocks']]
            schedules[mode] = Schedule(mode=mode, label=data['label'], blocks=blocks)
        
        return schedules
    
    def get_schedule(self, mode: str) -> Optional[Dict[str, Any]]:
        """Returns schedule definition for mode."""
        schedule = self.schedules.get(mode)
        return schedule.to_dict() if schedule else None
    
    def get_all_schedules(self) -> Dict[str, Any]:
        """Returns all schedule definitions."""
        return {mode: schedule.to_dict() for mode, schedule in self.schedules.items()}
    
    def validate_mode(self, mode: str) -> bool:
        """Check if mode is valid."""
        return mode in self.schedules
    
    def get_blocks_for_mode(self, mode: str) -> List[Dict[str, str]]:
        """Returns list of blocks for schedule mode."""
        schedule = self.schedules.get(mode)
        if schedule:
            return [block.to_dict() for block in schedule.blocks]
        return []
