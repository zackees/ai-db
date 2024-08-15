import unittest

from aidb.secrets import load_connection_url

CONNECTION_URL = load_connection_url()


class TestSecrets(unittest.TestCase):

    @unittest.skipUnless(CONNECTION_URL, "No connection URL found.")
    def test_load_connection_url(self):
        # Arrange
        print()

    @unittest.skipUnless(CONNECTION_URL, "No connection URL found.")
    def test_store_connection_url(self):
        # Arrange
        print()


if __name__ == "__main__":
    unittest.main()
