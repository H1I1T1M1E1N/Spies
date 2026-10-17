# models.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

class TimetableState(Enum):
    #Состояния автомата при чтении расписания.#
    SEEKING_ROUTE = auto()       # Ищем/ждем FROM: или TO:
    EXPECT_FROM_CODE = auto()    # Ожидаем 3-буквенный IATA код вылета
    EXPECT_TO_CODE = auto()      # Ожидаем 3-буквенный IATA код прилета
    READING_SCHEDULE = auto()    # Внутри таблицы рейсов

@dataclass
class FlightScheduleRecord:
    departure: Optional[str] = None
    arrival: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    days: Optional[str] = None
    flight_number: Optional[str] = None