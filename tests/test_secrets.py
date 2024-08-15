import unittest

from aidb.main import run
from aidb.secrets import load_connection_url

CONNECTION_URL = load_connection_url()


class TestSecrets(unittest.TestCase):

    @unittest.skipUnless(CONNECTION_URL, "No connection URL found.")
    def test_load_connection_url(self):
        # Arrange
        rtn = run(CONNECTION_URL, "youtube")
        self.assertEqual(rtn, 0)


if __name__ == "__main__":
    unittest.main()
