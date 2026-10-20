import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

DATASET_PATH = "MASTER_AIRLINES_DB_sorted.csv"
EVENTS_PATH = "world_events.csv"
OUTPUT_CSV = "spies_world_events.csv"
MIN_INCIDENTS = 3


def main():
    print("🔄 Загрузка базы перелетов и мировых событий...")
    flights = pd.read_csv(DATASET_PATH, dtype=str, low_memory=False)
    events = pd.read_csv(EVENTS_PATH, dtype=str)

    flights.columns = flights.columns.str.strip()
    events.columns = events.columns.str.strip()

    flights["document_number"] = (
        flights["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    flights["birth_date"] = flights["birth_date"].fillna("Неизвестно")

    flights["flight_date_dt"] = pd.to_datetime(flights["flight_date"], errors="coerce")
    events["event_date_dt"] = pd.to_datetime(events["event_date"], errors="coerce")

    flights = flights.dropna(
        subset=["flight_date_dt", "departure", "arrival", "first_name", "last_name", "document_number"]
    )
    flights = flights[~flights["document_number"].isin(["", "nan", "None"])]

    # Пересечения по вылету и прилету
    matches_dep = pd.merge(flights, events, left_on="departure", right_on="iata_code", how="inner")
    matches_arr = pd.merge(flights, events, left_on="arrival", right_on="iata_code", how="inner")
    all_matches = pd.concat([matches_dep, matches_arr], ignore_index=True)

    # Разница в днях (за 0-7 дней до события)
    all_matches["days_before"] = (all_matches["event_date_dt"] - all_matches["flight_date_dt"]).dt.days
    suspects = all_matches[
        (all_matches["days_before"] >= 0) & (all_matches["days_before"] <= 7)
    ].copy()

    if suspects.empty:
        print("❌ Подозреваемых не найдено.")
        return

    suspects["event_id"] = suspects["event_date"].astype(str) + "_" + suspects["iata_code"]
    suspects["event_detail"] = (
        "«" + suspects["event_title"].astype(str) + "» (аэропорт " + suspects["iata_code"].astype(str)
        + ", за " + suspects["days_before"].astype(str) + " дн. до события " + suspects["event_date"].astype(str) + ")"
    )

    # Группируем по пассажиру
        # Группируем по пассажиру
    summary = (
        suspects.groupby(["document_number", "first_name", "last_name"], as_index=False)
        .agg(
            birth_date=("birth_date", "first"),
            incident_count=("event_id", "nunique"),
            # Добавили проверку на пустоты (pd.notna) и принудительный перевод в строку str()
            events_details=("event_detail", lambda x: sorted([str(i) for i in set(x) if pd.notna(i)])),
        )
    )

    top_suspects = summary[summary["incident_count"] >= MIN_INCIDENTS].sort_values(
        by="incident_count", ascending=False
    ).copy()

    if top_suspects.empty:
        print(f"❌ Подозреваемых с {MIN_INCIDENTS} и более совпадениями не найдено.")
        return

    def build_comment(row):
        details_str = "; ".join(row["events_details"])
        return (
            f"Подозревается в причастности к диверсионной или разведывательной деятельности: "
            f"присутствовал(а) в регионе за 0–7 дней до начала {row['incident_count']} крупных мировых инцидентов "
            f"({details_str})."
        )

    top_suspects["comment"] = top_suspects.apply(build_comment, axis=1)

    result_df = top_suspects[
        ["document_number", "first_name", "last_name", "birth_date", "comment"]
    ]
    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Найдено подозреваемых: {len(result_df)}. Сохранено в '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()
