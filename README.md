# Repository Overview
A system that can convert natural language queries into SQL queries to retrieve data from multiple sources (MySQL database and CSV data).

### Tech Stack
Python, Flask, MySQL, SQLite, Google Gemini, FAISS, Langchain

### Approach
A Text-to-SQL query system that uses a RAG chain implemented on a vector store to query data from csv and SQL db.. The system can take a natural language query (e.g., “Show me all all transactions in the last month”) and convert it into an SQL query to fetch data from either:
  * A MySQL database with predefined tables
  * CSV data, which is treated like a separate data source.
It is implemented on a RESTful with an endpoint ‘/query’ that accepts a natural language query and returns the result from either the MySQL database or CSV.

### Technical Implementation
![Architecture](assets\concept_map.png)

#### Architecture Overview
1. Backend: Python with RESTful API
  * wsgi.py: RESTful API application setup.
  * test: contains unit test files for agents and connectors 
  * docker/: docker files
  * config.py: config files for server and db
  * src/: 
    * agents: agents for orchestration and setting up RAG chain
    * data_sources: connector files for each data source
    * routes:  API endpoint definitions.
  Gemini APIs and other such LLMs can be used for csv and sql query generation looking at the data ingested through vector stores using similarity searches.

2. Database: MySQL, SQLite, FAISS
  Reliability, faster read and write speeds, and storing structured data.
  * write speeds, and storing structured data.
  * SQLite: persistence dbs
  * FAISS: vector dbs for RAG

#### Current API Specifications
Generate Query

***Endpoint:*** `/query`
***Method:*** POST

##### Request Body

The request body should be in JSON format with the following structure:

```json
{
  "query": "string"
}
```

##### Response

The response will be in JSON format with the following structure:

```json
{
  "result": {
    "answer": "string",
    "sources": [
      "string",
      "string",
      "string",
      "string",
      "string"
    ]
  }
}
```

##### Additional Information

- The `query` field in the request should contain the user's question or input.
- The `answer` field in the response will contain the API's response to the query.
- The `sources` array in the response will list up to 5 sources used to generate the answer.

### Example Usage
To run the WSGI application:

Ensure you're in the project directory and your virtual environment is activated (if you're using one).
Run the following command:
```
python wsgi.py
```
This will start the server, typically on http://127.0.0.1:5000.