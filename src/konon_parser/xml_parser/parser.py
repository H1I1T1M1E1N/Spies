# konon_parser/xml_parser/parser.py
from typing import Iterator, List, Dict, Any, Optional
import pandas as pd
import re
from .interfaces import IParser
from .models import XmlToken, TokenType

class FlightHierarchyParser(IParser):
    #
    #Парсер-автомат со стеком контекстов.
    #Приводит данные строго к Единому стандарту (11 колонок).
    #

    # Ровно 11 колонок в строгом порядке из "Золотого правила"
    TARGET_COLUMNS = [
        'first_name',
        'last_name',
        'birth_date',
        'document_number',
        'flight_date',
        'flight_number',
        'departure',
        'arrival',
        'pnr',
        'ticket_number',
        'ff_number'
    ]

    def __init__(self):
        self._current_user: Dict[str, Optional[str]] = {}
        self._current_card: Dict[str, Optional[str]] = {}
        self._current_flight: Dict[str, Optional[str]] = {}
        self._in_flight: bool = False
        self._records: List[Dict[str, Any]] = []

    def parse(self, tokens: Iterator[XmlToken]) -> pd.DataFrame:
        self._records.clear()
        self._reset_all_contexts()

        for token in tokens:
            self._dispatch_token(token)

        return self._build_dataframe()

    def _dispatch_token(self, token: XmlToken) -> None:
        if token.type == TokenType.START_ELEMENT:
            self._handle_start_tag(token)
        elif token.type == TokenType.END_ELEMENT:
            self._handle_end_tag(token)

    def _handle_start_tag(self, token: XmlToken) -> None:
        if token.tag == 'name':
            self._current_user['first_name'] = token.attributes.get('first', '').upper()
            self._current_user['last_name'] = token.attributes.get('last', '').upper()

        elif token.tag == 'card':
            # "Золотое правило": только номер карты, без префиксов типа FF# / FB / KE
            raw_card = token.attributes.get('number', '')
            # Оставляем только цифры/номер после пробела (например 'FB 171388778' -> '171388778')
            clean_ff = re.sub(r'^[A-Za-z#\s]+', '', raw_card).strip()
            self._current_card['ff_number'] = clean_ff

        elif token.tag == 'activity' and token.attributes.get('type') == 'Flight':
            self._in_flight = True
            self._current_flight.clear()

    def _handle_end_tag(self, token: XmlToken) -> None:
        if self._in_flight:
            if token.tag == 'Code':
                self._current_flight['flight_number'] = token.text
            elif token.tag == 'Date':
                self._current_flight['flight_date'] = token.text
            elif token.tag == 'Departure':
                self._current_flight['departure'] = token.text.upper() if token.text else None
            elif token.tag == 'Arrival':
                self._current_flight['arrival'] = token.text.upper() if token.text else None
            elif token.tag == 'activity':
                self._commit_flight_record()
                self._in_flight = False

    def _commit_flight_record(self) -> None:
        # Собираем запись с гарантированным наличием всех 11 полей
        record = {
            'first_name': self._current_user.get('first_name'),
            'last_name': self._current_user.get('last_name'),
            'birth_date': None,
            'document_number': None,
            'flight_date': self._current_flight.get('flight_date'),
            'flight_number': self._current_flight.get('flight_number'),
            'departure': self._current_flight.get('departure'),
            'arrival': self._current_flight.get('arrival'),
            'pnr': None,
            'ticket_number': None,
            'ff_number': self._current_card.get('ff_number')
        }
        self._records.append(record)

    def _reset_all_contexts(self) -> None:
        self._current_user.clear()
        self._current_card.clear()
        self._current_flight.clear()
        self._in_flight = False

    def _build_dataframe(self) -> pd.DataFrame:
        if not self._records:
            return pd.DataFrame(columns=self.TARGET_COLUMNS)
        return pd.DataFrame(self._records)[self.TARGET_COLUMNS]