# route_tracker.py
import re
from typing import Optional

class RouteContextTracker:
    #Отслеживает текущее направление полета (FROM: ... TO: ...).#
    
    def __init__(self):
        self.departure: Optional[str] = None
        self.arrival: Optional[str] = None
        self._awaiting_from_code = False
        self._awaiting_to_code = False
        self._re_iata = re.compile(r'^[A-Z]{3}$')

    def feed_line(self, line: str) -> None:
        #Анализирует строку на наличие маркеров маршрута.#
        # 1. Заголовок FROM
        if line.startswith('FROM:'):
            parts = line.split()
            if len(parts) > 1 and self._re_iata.match(parts[-1]):
                self.departure = parts[-1]
            else:
                self._awaiting_from_code = True
            return

        # 2. Заголовок TO
        if line.startswith('TO:'):
            parts = line.split()
            if len(parts) > 1 and self._re_iata.match(parts[-1]):
                self.arrival = parts[-1]
            else:
                self._awaiting_to_code = True
            return

        # 3. Ожидание IATA кода отдельной строкой сразу после названия города
        if self._awaiting_from_code:
            if self._re_iata.match(line):
                self.departure = line
                self._awaiting_from_code = False

        elif self._awaiting_to_code:
            if self._re_iata.match(line):
                self.arrival = line
                self._awaiting_to_code = False

    @property
    def is_valid_route(self) -> bool:
        #Маршрут готов к привязке рейсов.#
        return bool(self.departure and self.arrival)