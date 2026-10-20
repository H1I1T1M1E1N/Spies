import pandas as pd

DATASET_PATH = "datasets/MASTER_AIRLINES_DB_sorted.csv"
OUTPUT_TELEPORTS = "datasets/spies_teleports.csv"
OUTPUT_ETERNAL_TRANSIT = "datasets/spies_eternal_transit.csv"
OUTPUT_TAILS = "datasets/spies_surveillance_tails.csv"


def analyze_route_anomalies(df: pd.DataFrame):
    print("🔄 Загрузка и очистка данных...")
    df = df.copy()
    df.columns = df.columns.str.strip()

    df["document_number"] = (
        df["document_number"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    df["birth_date"] = df["birth_date"].fillna("Неизвестно")

    df["flight_date_clean"] = (
        df["flight_date"]
        .astype(str)
        .str.replace("'", "", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
    )
    df["flight_date_dt"] = pd.to_datetime(df["flight_date_clean"], errors="coerce")

    df = df.dropna(subset=["flight_date_dt", "first_name", "last_name", "document_number"])
    df = df[~df["document_number"].isin(["", "nan", "None"])]

    pass_cols = ["document_number", "first_name", "last_name"]
    df = df.sort_values(by=pass_cols + ["flight_date_dt"]).reset_index(drop=True)

    # =========================================================================
    # 1. ТОЧКИ ТЕЛЕПОРТАЦИИ (Разрывы маршрутов <= 1 дня)
    # =========================================================================
    prev_arrival = df.groupby(pass_cols)["arrival"].shift(1)
    prev_date = df.groupby(pass_cols)["flight_date_dt"].shift(1)
    days_diff = (df["flight_date_dt"] - prev_date).dt.days

    teleports = df[
        (df["departure"] != prev_arrival) & (prev_arrival.notna()) & (days_diff <= 1)
    ].copy()

    teleports["prev_arrival"] = prev_arrival
    teleports["prev_date"] = prev_date
    teleports["days_diff"] = days_diff

    if not teleports.empty:
        teleports["episode"] = (
            teleports["prev_date"].dt.strftime("%Y-%m-%d")
            + " прилетел в "
            + teleports["prev_arrival"].astype(str)
            + ", но уже "
            + teleports["flight_date_dt"].dt.strftime("%Y-%m-%d")
            + " вылетел из "
            + teleports["departure"].astype(str)
            + " (разница "
            + teleports["days_diff"].astype(str)
            + " дн.)"
        )
        tp_grouped = (
            teleports.groupby(pass_cols, as_index=False)
            .agg(
                birth_date=("birth_date", "first"),
                tp_count=("episode", "count"),
                # Отфильтровали NaN и перевели всё в строки перед склейкой
                episodes=("episode", lambda x: "; ".join([str(i) for i in x if pd.notna(i)][:3])),
            )
        )
        tp_grouped["comment"] = tp_grouped.apply(
            lambda r: (
                f"Зафиксирована маршрутная аномалия («телепортация», всего случаев: {r['tp_count']}): "
                f"пассажир менял аэропорт вылета за 0–1 день без легального зарегистрированного перелета "
                f"({r['episodes']}), что указывает на использование закрытых спецбортов или подставных документов."
            ),
            axis=1,
        )
        tp_grouped[["document_number", "first_name", "last_name", "birth_date", "comment"]].to_csv(
            OUTPUT_TELEPORTS, index=False, encoding="utf-8"
        )
        print(f"✅ Телепорты сохранены в '{OUTPUT_TELEPORTS}' ({len(tp_grouped)} чел.)")

    # =========================================================================
    # 2. ВЕЧНЫЕ ТРАНЗИТНИКИ (Люди без домашнего аэропорта)
    # =========================================================================
    temp_stats = df[pass_cols + ["birth_date", "flight_number", "departure"]].copy()
    temp_stats["days_diff"] = days_diff

    transit_stats = (
        temp_stats.groupby(pass_cols, as_index=False)
        .agg(
            birth_date=("birth_date", "first"),
            total_flights=("flight_number", "count"),
            max_gap_days=("days_diff", "max"),
            unique_airports=("departure", "nunique"),
        )
    )

    eternal_transit = transit_stats[
        (transit_stats["total_flights"] >= 10) & (transit_stats["max_gap_days"] <= 3)
    ].sort_values(by="total_flights", ascending=False).copy()

    if not eternal_transit.empty:
        eternal_transit["comment"] = eternal_transit.apply(
            lambda r: (
                f"Профиль «вечного транзитника» без домашнего аэропорта: совершил(а) {r['total_flights']} "
                f"перелетов через {r['unique_airports']} различных аэропортов, при этом максимальная пауза "
                f"между рейсами ни разу не превысила {int(r['max_gap_days'])} дн., что типично для "
                f"нелегального курьера или оперативника в непрерывной ротации."
            ),
            axis=1,
        )
        eternal_transit[
            ["document_number", "first_name", "last_name", "birth_date", "comment"]
        ].to_csv(OUTPUT_ETERNAL_TRANSIT, index=False, encoding="utf-8")
        print(f"✅ Вечные транзитники сохранены в '{OUTPUT_ETERNAL_TRANSIT}' ({len(eternal_transit)} чел.)")

    # =========================================================================
    # 3. ПОИСК СЛЕЖКИ (Хвост в лабиринте >= 3 совместных рейсов)
    # =========================================================================
    flights_subset = df[
        pass_cols + ["birth_date", "flight_date_clean", "flight_number", "departure", "arrival"]
    ].drop_duplicates()

    merged = pd.merge(
        flights_subset,
        flights_subset,
        on=["flight_date_clean", "flight_number", "departure", "arrival"],
        suffixes=("_1", "_2"),
    )
    pairs = merged[merged["document_number_1"] != merged["document_number_2"]].copy()

    tail_stats = (
        pairs.groupby(
            [
                "document_number_1",
                "first_name_1",
                "last_name_1",
                "birth_date_1",
                "document_number_2",
                "first_name_2",
                "last_name_2",
            ],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "shared_flights"})
    )

    suspicious_tails = tail_stats[tail_stats["shared_flights"] >= 3].copy()

    if not suspicious_tails.empty:
        suspicious_tails["partner_info"] = (
            suspicious_tails["first_name_2"]
            + " "
            + suspicious_tails["last_name_2"]
            + " (паспорт № "
            + suspicious_tails["document_number_2"]
            + ", общих рейсов: "
            + suspicious_tails["shared_flights"].astype(str)
            + ")"
        )
        tails_grouped = (
            suspicious_tails.groupby(
                ["document_number_1", "first_name_1", "last_name_1", "birth_date_1"],
                as_index=False,
            )
            # То же самое: отфильтровали NaN
            .agg(partners=("partner_info", lambda x: "; ".join([str(i) for i in x if pd.notna(i)][:5])))
            .rename(
                columns={
                    "document_number_1": "document_number",
                    "first_name_1": "first_name",
                    "last_name_1": "last_name",
                    "birth_date_1": "birth_date",
                }
            )
        )
        tails_grouped["comment"] = tails_grouped.apply(
            lambda r: (
                f"Подозревается в ведении наружного наблюдения («хвост») или работе в связке: "
                f"неоднократно (3 и более раз) летал(а) одними и теми же рейсами в одни и те же даты "
                f"со следующими лицами: {r['partners']}."
            ),
            axis=1,
        )
        tails_grouped[
            ["document_number", "first_name", "last_name", "birth_date", "comment"]
        ].to_csv(OUTPUT_TAILS, index=False, encoding="utf-8")
        print(f"✅ Подозрительные хвосты сохранены в '{OUTPUT_TAILS}' ({len(tails_grouped)} чел.)")

def main():
    df = pd.read_csv(DATASET_PATH, sep=",", dtype=str, low_memory=False)
    analyze_route_anomalies(df)

if __name__ == "__main__":
    main()
