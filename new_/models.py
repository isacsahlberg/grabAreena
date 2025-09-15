from dataclasses import dataclass
from typing import List, Optional

# for simplicity, use dataclasses
@dataclass
class Piece:
    start: str
    end: str
    text: str

@dataclass
class Program:
    title: str
    start: str
    end: str
    description: str
    pieces: List[Piece]

    def matches(self, pattern: str) -> List[Piece]:
        """Return pieces where pattern appears (case-insensitive)."""
        return [p for p in self.pieces if pattern.lower() in p.text.lower()]


