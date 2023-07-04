import unittest
from unittest.mock import patch, MagicMock
from signalrcore.hub_connection_builder import HubConnectionBuilder
from main import Main


class MainTests(unittest.TestCase):
    @patch('signalrcore.hub_connection_builder.HubConnectionBuilder')
    def test_setSensorHub(self, mock_hub_builder):
        # Arrange
        main = Main()
        
        # Act
        main.setSensorHub()
        
        # Assert
        mock_hub_builder.return_value.with_url.assert_called_with(f"{main.HOST}/SensorHub?token={main.TOKEN}")
        mock_hub_builder.return_value.configure_logging.assert_called_with(logging.INFO)
        mock_hub_builder.return_value.with_automatic_reconnect.assert_called_with({
            "type": "raw",
            "keep_alive_interval": 10,
            "reconnect_interval": 5,
            "max_attempts": 999,
        })
        mock_hub_builder.return_value.build.assert_called()

    def test_analyzeDatapoint_above_threshold(self):
        # Arrange
        main = Main()
        main.T_MAX = 25
        main.TICKETS = 5
        main.sendActionToHvac = MagicMock()
        
        # Act
        main.analyzeDatapoint("2023-07-04", 30)
        
        # Assert
        main.sendActionToHvac.assert_called_with("2023-07-04", "TurnOnAc", 5)

    def test_analyzeDatapoint_below_threshold(self):
        # Arrange
        main = Main()
        main.T_MIN = 10
        main.TICKETS = 2
        main.sendActionToHvac = MagicMock()
        
        # Act
        main.analyzeDatapoint("2023-07-04", 5)
        
        # Assert
        main.sendActionToHvac.assert_called_with("2023-07-04", "TurnOnHeater", 2)


if __name__ == '__main__':
    unittest.main()
