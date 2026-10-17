# models.py
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class TokenType(Enum):
    #Типы токенов, генерируемые XML-лексером.
    START_ELEMENT = auto()
    END_ELEMENT = auto()

@dataclass(frozen=True)
class XmlToken:
    #Токен, представляющий событие в XML-потоке.
    type: TokenType
    tag: str
    attributes: Dict[str, str] = field(default_factory=dict)
    text: Optional[str] = None