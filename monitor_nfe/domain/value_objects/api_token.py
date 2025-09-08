from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class APIToken:
    """Value object representing an API token"""
    value: str
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError("API token cannot be empty or contain only whitespace")
    
    def is_valid(self) -> bool:
        """Check if token is valid (not empty, has content)"""
        return bool(self.value and self.value.strip())
    
    @property
    def masked(self) -> str:
        """Get masked version of token for display"""
        if len(self.value) <= 8:
            return "***"
        return f"{self.value[:4]}...{self.value[-4:]}"
    
    @classmethod
    def from_string(cls, token_string: Optional[str]) -> Optional['APIToken']:
        """Create APIToken from string, return None if invalid"""
        if not token_string or not token_string.strip():
            return None
        
        try:
            return cls(token_string.strip())
        except ValueError:
            return None
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, APIToken):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)