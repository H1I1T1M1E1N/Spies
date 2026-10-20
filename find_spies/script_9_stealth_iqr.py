import time
import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple, Optional

DATASET_PATH = "datasets/MASTER_AIRLINES_DB_sorted.csv"
PLOT_OUTPUT = "datasets/stealth_iqr_plot.png"
OUTPUT_CSV = "datasets/spies_stealth_iqr.csv"
TOP_N: Optional[int] = 10  # Поставь None, если нужно выгрузить ВСЕ выбросы сверх порога IQR


class IqrOutlierDetector:
    """Детектор статистических выбросов по числу полетов среди пассажиров без карт лояльности."""

    def __init__(self, multiplier: float = 1.5):
        self.multiplier = multiplier

    def detect_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
        # Оставляем перелеты без программы лояльности
        mask_no_ff = df["ff_number"].isna() | (
            df["ff_number"].astype(str).str.strip().isin(["", "nan", "None"])
        )
        stealth_flights = df[mask_no_ff].copy()

        stealth_flights["clean_doc"] = (
            stealth_flights["document_number"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )
        stealth_flights["birth_date"] = stealth_flights["birth_date"].fillna("Неизвестно")

        stealth_flights = stealth_flights.dropna(
            subset=["first_name", "last_name", "clean_doc"]
        )
        stealth_flights = stealth_flights[
            ~stealth_flights["clean_doc"].isin(["", "nan", "None"])
        ].copy()

        stats = (
            stealth_flights.groupby("clean_doc", as_index=False)
            .agg(
                first_name=("first_name", "first"),
                last_name=("last_name", "first"),
                birth_date=("birth_date", "first"),
                flight_count=("flight_number", "count"),
                unique_airports=("departure", "nunique"),
            )
            .rename(columns={"clean_doc": "document_number"})
        )

        stats = stats.sort_values(by="flight_count", ascending=False).reset_index(drop=True)

        q1 = stats["flight_count"].quantile(0.25)
        q3 = stats["flight_count"].quantile(0.75)
        iqr = q3 - q1
        threshold = q3 + self.multiplier * iqr

        n_pax = len(stats)
        stats["percentile"] = (stats.index + 1) / n_pax * 100.0

        outliers = stats[stats["flight_count"] > threshold].copy()
        return outliers, stats, threshold


class StealthVisualizer:
    """Построение графика распределения перелетов и порога IQR."""

    @staticmethod
    def plot_distribution(stats_df: pd.DataFrame, threshold: float, output_path: str) -> None:
        plt.figure(figsize=(10, 6), dpi=300)
        plt.plot(
            stats_df["percentile"],
            stats_df["flight_count"],
            color="#2b5c8f",
            linewidth=2,
            label="Активность пассажиров",
        )
        plt.axhline(
            y=threshold,
            color="#d9534f",
            linestyle="--",
            linewidth=1.5,
            label=f"Порог аномалий IQR ({threshold:.1f} перелетов)",
        )
        plt.title(
            "Распределение перелетов пассажиров без карт лояльности (Stealth)",
            fontsize=13,
            pad=12,
        )
        plt.xlabel("Накопительный процент людей (%)", fontsize=11)
        plt.ylabel("Количество перелетов", fontsize=11)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()


def analyze_stealth_iqr(
    df: pd.DataFrame, plot_path: str = "stealth_iqr_plot.png", top_n: Optional[int] = 10
) -> Tuple[pd.DataFrame, float]:
    detector = IqrOutlierDetector(multiplier=1.5)
    visualizer = StealthVisualizer()

    outliers, full_stats, threshold = detector.detect_outliers(df)
    if not full_stats.empty:
        visualizer.plot_distribution(full_stats, threshold, plot_path)

    if outliers.empty:
        return pd.DataFrame(), threshold

    if top_n is not None:
        outliers = outliers.head(top_n).copy()

    outliers["comment"] = outliers.apply(
        lambda r: (
            f"Выявлен методом межквартильного размаха (IQR) в категории «Stealth»: "
            f"совершил(а) аномально большое количество перелетов ({r['flight_count']} рейсов "
            f"через {r['unique_airports']} аэропортов при статистическом пороге выброса {threshold:.1f} рейсов), "
            f"намеренно избегая регистрации в программах лояльности (ff_number отсутствует) "
            f"для сокрытия регулярной оперативной активности."
        ),
        axis=1,
    )

    result_df = outliers[
        ["document_number", "first_name", "last_name", "birth_date", "comment"]
    ]
    return result_df, threshold


def main():
    print(f"Загрузка данных: {DATASET_PATH} ...")
    start = time.time()
    df = pd.read_csv(DATASET_PATH, dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    print(f"Загружено записей: {len(df):,} за {time.time() - start:.2f} сек.")

    print("\nЗапуск детекции аномалий через Межквартильный размах (IQR)...")
    result_df, threshold = analyze_stealth_iqr(df, plot_path=PLOT_OUTPUT, top_n=TOP_N)

    print("=" * 70)
    print(f"ПОРОГ АНОМАЛИЙ IQR: > {threshold:.1f} перелетов")
    print("=" * 70)

    if result_df.empty:
        print("Аномальных пассажиров не найдено.")
        return

    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Сохранено подозреваемых: {len(result_df)} в '{OUTPUT_CSV}'.")
    print(f"📊 График сохранен в: {PLOT_OUTPUT}")


if __name__ == "__main__":
    main()
