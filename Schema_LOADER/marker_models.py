"""
Data models for the Marker Analysis System.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
from enum import Enum

class MarkerCategory(Enum):
    """Category of a marker."""
    MANIPULATION = "manipulation"
    FRAUD = "fraud"
    EMOTIONAL_ABUSE = "emotional_abuse"
    COMMUNICATION_PATTERN = "communication_pattern"
    POSITIVE = "positive"
    SUPPORT = "support"
    UNCATEGORIZED = "uncategorized"

class MarkerSeverity(Enum):
    """Severity level of a marker."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MarkerPattern:
    """Represents a single pattern for a marker."""
    pattern: str
    type: str = "regex"  # regex, keyword, semantic
    case_sensitive: bool = False
    confidence: float = 1.0

@dataclass
class MarkerDefinition:
    """A complete definition of a single marker."""
    id: str
    name: str
    category: MarkerCategory
    description: str = ""
    severity: MarkerSeverity = MarkerSeverity.MEDIUM
    patterns: List[MarkerPattern] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    weight: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True 