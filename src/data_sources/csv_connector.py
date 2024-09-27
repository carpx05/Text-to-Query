import os
import sys
import csv
import logging
from typing import List, Dict, Any

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_dir)
from config import Config
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CSVConnector:
    def __init__(self):
        self.csv_directory = Config.CSV_DIRECTORY
        self.encoding = Config.ENCODING
        self.max_sample_rows = Config.MAX_SAMPLE_ROWS

    def extract_all_csv_data(self) -> List[Dict[str, Any]]:
        all_data = []

        try:
            for filename in os.listdir(self.csv_directory):
                if filename.endswith(".csv"):
                    file_data = self._process_csv_file(filename)
                    if file_data:
                        all_data.append(file_data)
        except OSError as e:
            self.logger.error(f"Error accessing directory {self.csv_directory}: {e}")

        return all_data

    def _process_csv_file(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.csv_directory, filename)
        try:
            with open(filepath, "r", newline="", encoding=self.encoding) as csvfile:
                csv_reader = csv.reader(csvfile)
                schema = next(csv_reader, [])
                sample_data = self._get_sample_data(csv_reader)

                return {
                    "database": self.csv_directory,
                    "table": filename,
                    "schema": schema,
                    "sample_data": sample_data,
                }
        except IOError as e:
            self.logger.error(f"Error reading file {filepath}: {e}")
        except csv.Error as e:
            self.logger.error(f"CSV error in file {filepath}: {e}")
        return {}

    def _get_sample_data(self, csv_reader) -> List[List[str]]:
        sample_data = []
        for _ in range(self.max_sample_rows):
            try:
                row = next(csv_reader, None)
                if row is None:
                    break
                sample_data.append(row)
            except csv.Error as e:
                self.logger.warning(f"Error reading row: {e}")
                break
        return sample_data
