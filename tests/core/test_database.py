import unittest
from unittest.mock import MagicMock
from core.database import DatabaseClient

class TestDatabaseMigration(unittest.TestCase):
    def setUp(self):
        self.client = DatabaseClient()
        self.mock_conn = MagicMock()
        self.client.connection = self.mock_conn

    def test_list_tables_usage(self):
        """Verify list_tables is used."""
        # Configure mock
        self.mock_conn.list_tables.return_value = []

        # Act
        try:
            self.client.get_or_create_core_table()
        except Exception:
            pass

        # Assert
        self.assertTrue(self.mock_conn.list_tables.called, "list_tables() should be called")
        self.assertFalse(self.mock_conn.table_names.called, "table_names() should NOT be called")

    def test_no_fallback(self):
        """Verify that if list_tables is missing, it raises AttributeError (no fallback)."""
        # Remove list_tables from mock
        del self.mock_conn.list_tables

        # Configure table_names to be present, to ensure we don't accidentally use it
        self.mock_conn.table_names.return_value = []

        # Act & Assert
        with self.assertRaises(AttributeError):
            self.client.get_or_create_core_table()
