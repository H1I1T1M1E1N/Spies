# row_fsm.py
import re
from enum import Enum, auto
from typing import Optional, Dict

class RowState(Enum):
    WAITING_VALIDITY = auto()
    WAITING_DAYS_AND_TIME = auto()
    WAITING_ARR_TIME = auto()
    WAITING_FLIGHT_NUM = auto()

class FlightRowFsm:
    #Конечный автомат для распознавания одного блока рейса.#

    def __init__(self):
        self._state = RowState.WAITING_VALIDITY
        self._buffer: Dict[str, str] = {}
        
        self._re_validity = re.compile(r'^(\d{2}\s+[A-Za-z]{3})\s*-\s*(\d{2}\s+[A-Za-z]{3})$')
        self._re_time_split = re.compile(r'\s+(\d{2}:\d{2})$')
        self._re_time = re.compile(r'^\d{2}:\d{2}')

    def feed_line(self, line: str) -> Optional[Dict[str, str]]:
        #
        #Принимает строку. 
        #Возвращает заполненный словарь рейса, если строка была завершающей, иначе None.
        #
        
        # Шаг 1: Validity (01 Nov - 31 Jan)
        val_match = self._re_validity.match(line)
        if val_match:
            self._buffer = {
                'valid_from': val_match.group(1).strip(),
                'valid_to': val_match.group(2).strip()
            }
            self._state = RowState.WAITING_DAYS_AND_TIME
            return None

        # Шаг 2: Days + Departure Time (1234567 06:00)
        if self._state == RowState.WAITING_DAYS_AND_TIME:
            time_match = self._re_time_split.search(line)
            if time_match:
                days = line[:time_match.start()].strip()
                self._buffer['days'] = days
                self._state = RowState.WAITING_ARR_TIME
            else:
                self.reset()
            return None

        # Шаг 3: Arrival Time (07:25)
        if self._state == RowState.WAITING_ARR_TIME:
            if self._re_time.match(line):
                self._state = RowState.WAITING_FLIGHT_NUM
            else:
                self.reset()
            return None

        # Шаг 4: Flight Number (KL1328)
        if self._state == RowState.WAITING_FLIGHT_NUM:
            # Номер рейса: 2 символа авиакомпании + от 1 до 4 цифр
            flight_num = line.replace(" ", "").strip()
            self._buffer['flight_number'] = flight_num
            
            result = self._buffer.copy()
            self.reset()
            return result

        return None

    def reset(self) -> None:
        self._state = RowState.WAITING_VALIDITY
        self._buffer.clear()