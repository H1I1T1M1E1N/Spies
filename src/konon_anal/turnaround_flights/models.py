# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class FlightEdge:
    #Атрибуты ребра в мультиграфе полетов.#
    departure: str
    arrival: str
    flight_date: datetime
    flight_number: str

@dataclass
class CourierCandidate:
    #Результат идентификации подозрительного курьера.#
    passenger_id: str
    first_name: str
    last_name: str
    turnaround_count: int
    total_flights: int
    turnaround_ratio: float