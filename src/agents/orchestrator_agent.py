import os
import sys
from typing import List, Dict, Any, Optional, Tuple
import json
import re

from src.agents.rag_agent import RAGAgent

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_dir)
from data_sources.mysql_connector import MySQLConnector
from data_sources.sqlite_connector import SQLiteConnector
from data_sources.faiss_connector import FAISSConnector
from data_sources.csv_connector import CSVConnector

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_dir)
from config import Config

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self):
        self.mysql_connector = MySQLConnector()
        self.sqlite_connector = SQLiteConnector()
        self.faiss_connector = FAISSConnector()
        self.csv_connector = CSVConnector()
        self.rag_agent = RAGAgent()

    def extract_data(self) -> List[Any]:
        """
        Extract data from all data sources.
        """
        try:
            sql_data = self.mysql_connector.extract_all_mysql_data()
            csv_data = self.csv_connector.extract_all_csv_data()
            logger.info("Data extracted successfully")
            # Add other data sources as needed
            return sql_data + csv_data
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            raise

    def store_data_in_faiss(self, data: List[Any]) -> None:
        """
        Store the extracted data in FAISS.
        """
        try:
            self.faiss_connector.store_in_faiss(data)
            logger.info("Data stored in FAISS successfully")
        except Exception as e:
            logger.error(f"Error storing data in FAISS: {str(e)}")
            raise

    def process_query(self, query: str) -> Tuple[str, List[str]]:
        """
        Process the query using the RAG pipeline.
        """
        try:
            return self.rag_agent.run_rag_pipeline(query)
            logger.info("Query processed successfully")
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def orchestrate_query(self, query: str) -> Tuple[str, List[str]]:
        """
        Orchestrate the entire query process.
        """
        try:
            logger.info(f"Processing query: {query}")
            data = self.extract_data()
            self.store_data_in_faiss(data)
            answer, sources = self.process_query(query)
            logger.info("Query processed successfully")
            query, source_type = self.post_process(answer)

            return query, source_type, sources
        except Exception as e:
            logger.error(f"Error orchestrating query: {str(e)}")
            raise

    def post_process(self, answer: str):
        """
        Post-processing steps.
        """
        try:
            # json_str = answer.replace('`', '').replace('python', 'json', '', 1).strip()
            json_str = re.sub(r'`|python|json|java', '', answer).strip()
            answer_json = json.loads(json_str)

            if answer_json['type'] == "csv":
                # Post-process the CSV data
                query = self._process_csv(answer_json['query'])
            elif answer_json['type'] == "sql":
                # Post-process the SQL data
                query = answer_json['query']
                self._process_sql(query)
            elif answer_json['type'] == None:
                logger.info("No post-processing required.") 
                query = None
            return query, answer_json['type']           
        except Exception as e:
            logger.error(f"Error in post-processing: {str(e)}")
            raise

    def _process_csv(self, query: str) -> Tuple[str, List[str]]:
        """
        Process the CSV query.
        """
        try:
            with open('response.txt', 'r') as file:
                response_str = file.read()

            data_dir = Config.CSV_DATA_DIRECTORY
            pattern = r"open\('(.+\.csv)', 'r'\)"
            match = re.search(pattern, query)

            if match:
                csv_filename = match.group(1)  # Extract the current CSV file name
                csv_path = data_dir / csv_filename  # Construct the new path
                csv_path_str = str(csv_path).replace("\\", "/")
                updated_query = re.sub(pattern, lambda m: f"open(r'{csv_path_str}', 'r')", answer_query)
                try:
                    exec(updated_query)
                except Exception as e:
                    logger.error(f"Error executing updated query: {str(e)}")
            else:
                print("No CSV file found in the query.")
        except Exception as e:
            logger.error(f"Error processing CSV query: {str(e)}")

    def _process_sql(self, query: str) -> Tuple[str, List[str]]:
        """
        Process the SQL query.
        """
        try:
            connection = self.mysql_connector.connect()
            # results = self.mysql_connector.execute_query(connection, query)
            connection.close()
            logger.info(f"Executed SQL query: {query}")
            
        except Exception as e:
            logger.error(f"Error processing SQL query: {str(e)}")
            

# Example usage
if __name__ == "__main__":
    orchestrator_agent = OrchestratorAgent()
    query = "show me user id for FZwdkpHZ"
    answer, sources = orchestrator_agent.orchestrate_query(query)
    print("Answer:", answer)
    # print("Type:", answer[type])
    # print("Sources:", sources)