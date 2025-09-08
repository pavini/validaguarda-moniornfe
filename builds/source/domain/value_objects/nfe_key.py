from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class NFEKey:
    """Value object representing an NFe key"""
    value: str
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Invalid NFe key: {self.value}")
    
    def is_valid(self) -> bool:
        """Check if NFe key is valid (44 digits)"""
        if not self.value:
            return False
        
        # Remove any non-digit characters
        clean_key = re.sub(r'\D', '', self.value)
        
        # NFe key must have exactly 44 digits
        return len(clean_key) == 44 and clean_key.isdigit()
    
    @property
    def formatted(self) -> str:
        """Get formatted NFe key (with spaces every 4 digits)"""
        clean_key = re.sub(r'\D', '', self.value)
        return ' '.join(clean_key[i:i+4] for i in range(0, len(clean_key), 4))
    
    @property
    def clean(self) -> str:
        """Get clean NFe key (digits only)"""
        return re.sub(r'\D', '', self.value)
    
    @classmethod
    def from_string(cls, key_string: Optional[str]) -> Optional['NFEKey']:
        """Create NFEKey from string, return None if invalid"""
        if not key_string:
            return None
        
        try:
            return cls(key_string.strip())
        except ValueError:
            return None
    
    def __str__(self) -> str:
        return self.clean
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, NFEKey):
            return False
        return self.clean == other.clean
    
    def __hash__(self) -> int:
        return hash(self.clean)