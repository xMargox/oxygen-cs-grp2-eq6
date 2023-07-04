import unittest
from unittest.mock import patch
import sys
import os

# Add the project root directory to the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import Main


class MainTests(unittest.TestCase):
    def test_token(self):
        # Arrange
        os.environ.pop("TOKEN", None)  # Remove the "TOKEN" key from os.environ if it exists

        # Act & Assert
        with self.assertRaises((KeyError, TypeError)):
            main = Main()
            token = main.TOKEN 

    @patch.dict("os.environ", {"TOKEN": "test_token"})
    def test_default_t_max_value(self):
        # Arrange
        main = Main()

        # Act & Assert
        self.assertEqual(main.T_MAX, 21)

    @patch.dict("os.environ", {"TOKEN": "test_token"})
    def test_default_t_min_value(self):
        # Arrange
        main = Main()

        # Act & Assert
        self.assertEqual(main.T_MIN, 15)

if __name__ == '__main__':
    unittest.main()
