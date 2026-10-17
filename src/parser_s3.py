import time
import os
from datetime import timedelta

from konon_parser.xml_parser import parse_text_log
from konon_parser.pdf_parser import parse_pdf_timetable


class S3DataPipeline:
    def __init__(self, xml_path: str, pdf_path: str, output_dir: str):
        self.xml_path = xml_path
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run_xml(self) -> str:
        print("[1/2] Processing XML log...")
        start_time = time.time()

        df_xml = parse_text_log(self.xml_path)
        output_file = os.path.join(self.output_dir, "flights_data.csv")
        df_xml.to_csv(output_file, index=False, encoding='utf-8')

        elapsed = time.time() - start_time
        print(f"XML completed. Rows: {len(df_xml):,}. Time: {timedelta(seconds=int(elapsed))}. Saved: {output_file}")
        return output_file

    def run_pdf(self) -> str:
        print("[2/2] Processing PDF timetable (27,514 pages)...")
        start_time = time.time()

        df_pdf = parse_pdf_timetable(self.pdf_path, max_pages=None)
        output_file = os.path.join(self.output_dir, "timetable_reference.csv")
        df_pdf.to_csv(output_file, index=False, encoding='utf-8')

        elapsed = time.time() - start_time
        print(f"PDF completed. Rows: {len(df_pdf):,}. Time: {timedelta(seconds=int(elapsed))}. Saved: {output_file}")
        return output_file

    def execute_all(self):
        start_total = time.time()
        print("Starting S3 pipeline execution...")
        self.run_xml()
        self.run_pdf()
        total_elapsed = time.time() - start_total
        print(f"Pipeline finished. Total time: {timedelta(seconds=int(total_elapsed))}")


if __name__ == "__main__":
    #TODO: ВОВА СЮДА ВСТАВЬ СВОИ ПУТИ ДЛЯ ФАЙЛОВ!!!!!
    XML_FILE = "/home/daniil/DataScience/PointzAggregator-AirlinesData.xml"
    PDF_FILE = "/home/daniil/DataScience/Skyteam_Timetable.pdf"
    OUTPUT_DIR = "/home/daniil/DataScience/parsed_data"

    pipeline = S3DataPipeline(
        xml_path=XML_FILE,
        pdf_path=PDF_FILE,
        output_dir=OUTPUT_DIR
    )
    pipeline.execute_all()