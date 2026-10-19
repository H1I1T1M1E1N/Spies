# detector.py
import json
import pandas as pd
from typing import Dict, List
from .interfaces import ILoyaltyPoolDetector


class SharedLoyaltyDetector(ILoyaltyPoolDetector):
    # Детектор общих карт лояльности между закрытыми профилями форума и авиационной базой

    def __init__(self, forum_json_path: str = "/home/daniil/DataScience/FrequentFlyerForum-Profiles.json"):
        self.forum_json_path = forum_json_path

    def detect(self, df: pd.DataFrame, min_passengers: int = 2) -> pd.DataFrame:
        # 1. Читаем сырые данные форума для поиска коллизий в профилях
        with open(self.forum_json_path, 'r', encoding='utf-8') as f:
            forum_data = json.load(f)

        card_to_profiles: Dict[str, List[Dict]] = {}

        for profile in forum_data.get('Forum Profiles', []):
            nickname = profile.get('NickName', 'Unknown')
            real_name = profile.get('Real Name') or {}
            full_name = f"{real_name.get('First Name', '')} {real_name.get('Last Name', '')}".strip() or 'ANONYMOUS'

            for lp in profile.get('Loyality Programm', []):
                card_num = str(lp.get('Number', '')).strip()
                prog = str(lp.get('programm', '')).strip()
                if card_num:
                    clean_id = f"{prog} {card_num}"
                    card_to_profiles.setdefault(clean_id, []).append({
                        'nickname': nickname,
                        'name': full_name
                    })

        # 2. Фильтруем карты, которые указаны в нескольких профилях форума
        shared_in_forum = {k: v for k, v in card_to_profiles.items() if len(v) >= min_passengers}

        if not shared_in_forum:
            return pd.DataFrame()

        # 3. Обогащаем данными о реальных рейсах и паспортах из MASTER_DB
        results = []
        for card_id, profiles in shared_in_forum.items():
            num_only = card_id.split()[-1]
            matches = df[df['ff_number'].astype(str).str.contains(num_only, na=False)]

            # Извлекаем все известные документы и имена по этой карте из базы
            pax_records = matches.dropna(subset=['first_name', 'last_name']).drop_duplicates(subset=['document_number'])
            
            doc_str = 'None'
            real_names_str = 'None'
            if not pax_records.empty:
                doc_str = ', '.join(pax_records['document_number'].astype(str).str.replace(r'\.0$', '', regex=True).unique())
                real_names_str = ', '.join((pax_records['first_name'] + ' ' + pax_records['last_name']).unique())

            nicks = [p['nickname'] for p in profiles]
            forum_names = [p['name'] for p in profiles]

            results.append({
                'shared_card': card_id,
                'forum_nicknames': ' <-> '.join(nicks),
                'forum_profiles': ' | '.join(forum_names),
                'master_db_passengers': real_names_str,
                'identified_documents': doc_str,
                'total_flights_in_db': len(matches)
            })

        return pd.DataFrame(results)