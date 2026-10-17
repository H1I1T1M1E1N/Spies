# parser.py
from typing import Iterator, List, Dict, Any
import pandas as pd
from .interfaces import ITimetableParser
from .route_tracker import RouteContextTracker
from .row_fsm import FlightRowFsm

class TimetableParser(ITimetableParser):
    #Оркестратор: читает строки, координирует RouteTracker и RowFsm.#

    TARGET_COLUMNS = ['departure', 'arrival', 'valid_from', 'valid_to', 'days', 'flight_number']

    def __init__(self):
        self._route_tracker = RouteContextTracker()
        self._row_fsm = FlightRowFsm()
        self._records: List[Dict[str, Any]] = []

    def parse(self, lines: Iterator[str]) -> pd.DataFrame:
        self._records.clear()
        self._row_fsm.reset()

        for line in lines:
            # 1. Отдаем строку трекеру маршрута
            self._route_tracker.feed_line(line)

            # 2. Если маршрут валиден, пробуем собирать строку рейса
            if self._route_tracker.is_valid_route:
                flight_data = self._row_fsm.feed_line(line)
                
                # Если рейс собран — склеиваем с текущим маршрутом
                if flight_data:
                    record = {
                        'departure': self._route_tracker.departure,
                        'arrival': self._route_tracker.arrival,
                        **flight_data
                    }
                    self._records.append(record)

        if not self._records:
            return pd.DataFrame(columns=self.TARGET_COLUMNS)

        return pd.DataFrame(self._records)[self.TARGET_COLUMNS]