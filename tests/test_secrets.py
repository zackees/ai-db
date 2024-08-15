import unittest
from unittest.mock import patch

from aidb.secrets import load_connection_url, store_connection_url


class TestSecrets(unittest.TestCase):

    @patch("aidb.secrets.keyring.get_password")
    def test_load_connection_url(self, mock_get_password):
        # Arrange
        expected_url = "postgresql://user:password@localhost:5432/db"
        mock_get_password.return_value = expected_url

        # Act
        result = load_connection_url()

        # Assert
        self.assertEqual(result, expected_url)
        mock_get_password.assert_called_once_with("aidb", "connection_url")

    @patch("aidb.secrets.keyring.set_password")
    def test_store_connection_url(self, mock_set_password):
        # Arrange
        test_url = "postgresql://user:password@localhost:5432/db"

        # Act
        store_connection_url(test_url)

        # Assert
        mock_set_password.assert_called_once_with("aidb", "connection_url", test_url)


if __name__ == "__main__":
    unittest.main()
