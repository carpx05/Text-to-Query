import os
import sys
from typing import List, Dict, Any
from langchain.schema import Document
from google.generativeai import GenerativeModel, configure
from langchain.prompts import PromptTemplate
import json
import google.generativeai as genai

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(src_dir)
from data_sources.mysql_connector import CustomEncoder
from data_sources.faiss_connector import FAISSConnector
from data_sources.sqlite_connector import SQLiteConnector

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_dir)
from config import Config


class RAGAgent:
    def __init__(self):
        self.model = self._init_gemini()
        self.sqlite_connector = SQLiteConnector()
        self.prompt_template = self._create_prompt_template()
        self.faiss_connector = FAISSConnector()
        # self.mysql_connector = MySQLConnector()

    def _init_gemini(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        return GenerativeModel(Config.MODEL_NAME)

    def _create_prompt_template(self):
        template = """
        Context:
        {context}

        Question:
        {question}

        If you don't know the answer, return:
        {{
            "type": None,
            "query": None
        }}
        Don't try to make up an answer.

        A natural language query is given to you. Convert it into a CSV or SQL query based on the schemas and sample data provided in the context.
        In case of CSV, the query will be the Python code.

        If the data source is SQL, return:
        {{
            "type": "sql",
            "query": <sql_query>
        }}

        If the data source is CSV, return:
        {{
            "type": "csv",
            "query": <csv_query>
        }}

        Provide your answer in the exact format specified above.
        """
        return PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

    def retriever(self, query: str) -> List[Document]:
        # Placeholder for the actual search_index function
        results = self.faiss_connector.search_faiss(query)
        return [
            Document(
                page_content=json.dumps(r.get("sample_data", [])),
                metadata={
                    "score": r.get("score"),
                    "context": r.get("context", {}),
                    "schema": r.get("schema"),
                    "table": r.get("table"),
                    "database": r.get("database"),
                },
            )
            for r in results
        ]

    def rag_function(self, query: str) -> tuple:
        self.sqlite_connector.connect()

        # Check if the query result is in the SQLite persistence layer
        persisted_answer, persisted_sources = self.sqlite_connector.get_result(query)

        if persisted_answer:
            self.sqlite_connector.close()
            return persisted_answer, persisted_sources

        # If not in persistence layer, perform the RAG pipeline
        docs = self.retriever(query)

        # Prepare context
        context = "\n\n".join([doc.page_content for doc in docs])

        # Prepare the prompt
        full_prompt = self.prompt_template.format(context=context, question=query)

        # Get the response from the Gemini model
        response = self.model.generate_content(full_prompt)

        answer = response.text

        sources = [doc.metadata for doc in docs]

        # Store the results in the SQLite persistence layer
        self.sqlite_connector.store_result(query, answer, sources)

        self.sqlite_connector.close()
        return answer, sources

    def run_rag_pipeline(self, query: str) -> tuple:
        return self.rag_function(query)


# Example usage
if __name__ == "__main__":
    rag_agent = RAGAgent()
    query = "What is the average sales for the last quarter?"
    answer, sources = rag_agent.run_rag_pipeline(query)
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
