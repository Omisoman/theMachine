import unittest
from unittest.mock import patch, MagicMock
import json

# Assuming load_cloud_functions_hub is the method you're testing from ui.services.theMachine
from ui.services.theMachine import load_cloud_functions_hub

class TestFunctionHubOrchestration(unittest.TestCase):

    @patch('ui.services.theMachine.get_secret')  # Mock the get_secret function
    def test_function_hub_orchestration(self, mock_get_secret):
        # Simulated JSON response retrieved from the secret manager
        mock_service_data = json.dumps([
            {
                "Name": "wake_up_tesla",
                "URL": "https://mocked-url/wake_up_tesla",
                "Service_Category": "Cloud",
                "Root": "tesla_api",
                "API_Type": "POST",
                "API_Body": "none",
                "Input": "TRIGGER",
                "Output": "ACTION"
            },
            {
                "Name": "lock_car",
                "URL": "https://mocked-url/lock_car",
                "Service_Category": "Cloud",
                "Root": "tesla_api",
                "API_Type": "POST",
                "API_Body": "none",
                "Input": "TRIGGER",
                "Output": "ACTION"
            }
        ])

        # Mock the get_secret function to return the JSON string
        mock_get_secret.return_value = mock_service_data

        # Call the function that loads the cloud functions hub
        services = load_cloud_functions_hub()

        # Ensure the get_secret function was called with the expected secret name
        mock_get_secret.assert_called_once_with('CLOUD_FUNCTIONS_HUB')

        # Check that two services were retrieved
        self.assertEqual(len(services), 2)

        # Validate the first service data
        self.assertEqual(services[0]['Name'], 'wake_up_tesla')
        self.assertEqual(services[0]['URL'], 'https://mocked-url/wake_up_tesla')

        # Validate the second service data
        self.assertEqual(services[1]['Name'], 'lock_car')
        self.assertEqual(services[1]['URL'], 'https://mocked-url/lock_car')


if __name__ == '__main__':
    unittest.main()
