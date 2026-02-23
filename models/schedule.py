from typing import List, Dict, Any


class Block:
    """Represents a time block in a schedule."""
    
    def __init__(self, id: str, time: str, label: str):
        self.id = id
        self.time = time
        self.label = label
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'time': self.time,
            'label': self.label
        }
    
    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'Block':
        """Create instance from dictionary."""
        return Block(
            id=data.get('id', ''),
            time=data.get('time', ''),
            label=data.get('label', '')
        )


class Schedule:
    """Represents a schedule mode definition."""
    
    def __init__(self, mode: str, label: str, blocks: List[Block]):
        self.mode = mode
        self.label = label
        self.blocks = blocks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'mode': self.mode,
            'label': self.label,
            'blocks': [block.to_dict() for block in self.blocks]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Schedule':
        """Create instance from dictionary."""
        blocks = [Block.from_dict(b) for b in data.get('blocks', [])]
        return Schedule(
            mode=data.get('mode', ''),
            label=data.get('label', ''),
            blocks=blocks
        )
