import unittest
from unittest.mock import Mock, patch
from src.agents.orchestrator_agent import OrchestratorAgent

class TestOrchestratorAgent(unittest.TestCase):

    def setUp(self):
        self.orchestrator = OrchestratorAgent()

    @patch('src.agents.orchestrator_agent.DataSourceIdentifierAgent')
    @patch('src.agents.orchestrator_agent.DDLUnderstandingAgent')
    @patch('src.agents.orchestrator_agent.TextToSQLAgent')
    @patch('src.agents.orchestrator_agent.QueryExecutionAgent')
    @patch('src.agents.orchestrator_agent.SQLiteMemory')
    def test_process_query_non_ddl(self, MockMemory, MockQueryExecution, MockTextToSQL, MockDDL, MockDataSource):
        # Setup mocks
        mock_data_source = MockDataSource.return_value
        mock_data_source.identify.return_value = 'mysql'

        mock_ddl = MockDDL.return_value
        mock_ddl.is_ddl.return_value = False

        mock_text_to_sql = MockTextToSQL.return_value
        mock_text_to_sql.convert.return_value = 'SELECT * FROM sales WHERE date > "2023-08-01"'

        mock_query_execution = MockQueryExecution.return_value
        mock_query_execution.execute.return_value = [{'date': '2023-08-15', 'amount': 1000}]

        # Test
        query = "Show me the sales data for last month"
        result = self.orchestrator.process_query(query)

        # Assertions
        self.assertEqual(result['query'], query)
        self.assertEqual(result['data_source'], 'mysql')
        self.assertEqual(result['sql_query'], 'SELECT * FROM sales WHERE date > "2023-08-01"')
        self.assertEqual(result['result'], [{'date': '2023-08-15', 'amount': 1000}])

        # Verify method calls
        mock_data_source.identify.assert_called_once_with(query)
        mock_ddl.is_ddl.assert_called_once_with(query)
        mock_text_to_sql.convert.assert_called_once_with(query)
        mock_query_execution.execute.assert_called_once_with('SELECT * FROM sales WHERE date > "2023-08-01"', 'mysql')

    @patch('src.agents.orchestrator_agent.DataSourceIdentifierAgent')
    @patch('src.agents.orchestrator_agent.DDLUnderstandingAgent')
    @patch('src.agents.orchestrator_agent.TextToSQLAgent')
    @patch('src.agents.orchestrator_agent.QueryExecutionAgent')
    @patch('src.agents.orchestrator_agent.SQLiteMemory')
    def test_process_query_ddl(self, MockMemory, MockQueryExecution, MockTextToSQL, MockDDL, MockDataSource):
        # Setup mocks
        mock_data_source = MockDataSource.return_value
        mock_data_source.identify.return_value = 'mysql'

        mock_ddl = MockDDL.return_value
        mock_ddl.is_ddl.return_value = True

        mock_query_execution = MockQueryExecution.return_value
        mock_query_execution.execute.return_value = "Table created successfully"

        # Test
        query = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50))"
        result = self.orchestrator.process_query(query)

        # Assertions
        self.assertEqual(result['query'], query)
        self.assertEqual(result['data_source'], 'mysql')
        self.assertEqual(result['sql_query'], query)
        self.assertEqual(result['result'], "Table created successfully")

        # Verify method calls
        mock_data_source.identify.assert_called_once_with(query)
        mock_ddl.is_ddl.assert_called_once_with(query)
        mock_text_to_sql.convert.assert_not_called()
        mock_query_execution.execute.assert_called_once_with(query, 'mysql')

if __name__ == '__main__':
    unittest.main()