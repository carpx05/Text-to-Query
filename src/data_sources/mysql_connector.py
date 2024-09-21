import json
import logging
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import os
import sys

import mysql.connector
from mysql.connector import Error

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_dir)
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)

class MySQLConnector:
    def __init__(self):
        self.host=Config.MYSQL_HOST
        self.user=Config.MYSQL_USER
        self.password=Config.MYSQL_PASSWORD

    def connect(self, database: Optional[str] = None) -> Optional[mysql.connector.MySQLConnection]:
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=database
            )
            return connection
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return None

    @staticmethod
    def execute_query(connection: mysql.connector.MySQLConnection, query: str) -> List[tuple]:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return []

    def get_databases(self) -> List[str]:
        connection = self.connect()
        if not connection:
            return []

        query = "SHOW DATABASES"
        results = self.execute_query(connection, query)
        connection.close()

        return [db[0] for db in results if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

    def get_tables(self, database: str) -> List[str]:
        connection = self.connect(database)
        if not connection:
            return []

        query = "SHOW TABLES"
        results = self.execute_query(connection, query)
        connection.close()

        return [table[0] for table in results]

    def get_schema(self, database: str, table: str) -> List[Dict[str, str]]:
        connection = self.connect(database)
        if not connection:
            return []

        query = f"DESCRIBE {table}"
        results = self.execute_query(connection, query)
        connection.close()

        return [{"Field": column[0], "Type": column[1]} for column in results]

    def get_sample_data(self, database: str, table: str) -> List[Dict[str, Any]]:
        connection = self.connect(database)
        if not connection:
            return []

        query = f"SELECT * FROM {table} LIMIT 10"
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        connection.close()
        return results

    def extract_all_mysql_data(self) -> List[Dict[str, Any]]:
        all_data = []
        databases = self.get_databases()

        for db in databases:
            tables = self.get_tables(db)
            for table in tables:
                schema = self.get_schema(db, table)
                sample_data = self.get_sample_data(db, table)
                all_data.append({
                    "database": db,
                    "table": table,
                    "schema": schema,
                    "sample_data": sample_data
                })

        return all_data

def main():
    connector = MySQLConnector()
    all_data = connector.extract_all_mysql_data()
    
    # Example: Save the data to a JSON file
    with open('mysql_data.json', 'w') as f:
        json.dump(all_data, f, cls=CustomEncoder, indent=2)

    logger.info("Data extraction completed successfully.")

if __name__ == "__main__":
    main()