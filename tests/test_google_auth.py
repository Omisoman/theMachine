import unittest
from unittest.mock import patch, MagicMock, call, ANY
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# Importing the main app class we're testing
from ui.services.theMachine import TheMachineApp

# Initialize the app so we can call its methods in the test
app = TheMachineApp()


class TestGoogleAuth(unittest.TestCase):

    @patch('ui.services.theMachine.get_secret')  # Mock get_secret to simulate secret retrieval from Secret Manager
    @patch('ui.services.theMachine.Credentials')  # Mock the Google OAuth Credentials class
    def test_google_credentials_retrieval(self, mock_credentials, mock_get_secret):
        # Simulate what get_secret would return when retrieving valid OAuth tokens from Secret Manager
        mock_get_secret.return_value = json.dumps({
            "token": "valid_token",
            "refresh_token": "valid_refresh_token",
            "expiry": "2024-12-31T23:59:59Z"
        })

        # Mock the credentials object with valid credentials (pretending creds are good)
        mock_creds = MagicMock()
        mock_creds.valid = True  # This simulates that the credentials we got are still valid
        mock_credentials.from_authorized_user_info.return_value = mock_creds

        # Call the method we're testing, which should now use the mocked values
        creds = app.get_google_credentials()

        # Verify get_secret was called twice, once for 'oauth_token' and once for 'oauth_credentials'
        # This ensures the app correctly retrieves both pieces of information
        mock_get_secret.assert_has_calls([call('oauth_token'), call('oauth_credentials')])

        # After running the function, we expect creds to be valid
        self.assertTrue(creds.valid)  # Should be true since the creds are mocked as valid

    @patch('ui.services.theMachine.get_secret')  # Mocking get_secret again for the second test
    @patch('ui.services.theMachine.Credentials')  # Mock the Credentials class as well
    def test_expired_credentials_refresh(self, mock_credentials, mock_get_secret):
        # Simulate expired credentials
        mock_creds = MagicMock()
        mock_creds.valid = False  # Credentials are expired
        mock_creds.expired = True  # Mark them as expired
        mock_creds.refresh_token = 'valid_refresh_token'  # There's a refresh token available to refresh the creds

        # Mock the refresh method to simulate refreshing the credentials
        # When refresh is called, we update mock_creds.valid to True, mimicking a successful refresh
        mock_creds.refresh = MagicMock(side_effect=lambda _: setattr(mock_creds, 'valid', True))
        mock_credentials.from_authorized_user_info.return_value = mock_creds

        # Mock the get_secret call to return the refresh token when needed
        mock_get_secret.return_value = json.dumps({"refresh_token": "valid_refresh_token"})

        # Simulate the credentials being serialized to JSON for storage (post-refresh)
        mock_creds.to_json.return_value = json.dumps({
            "token": "valid_token",
            "refresh_token": "valid_refresh_token",
            "expiry": "2024-12-31T23:59:59Z"
        })

        # Call the function we're testing
        creds = app.get_google_credentials()

        # Make sure the refresh method was called with a Request object (which handles the actual HTTP refresh)
        mock_creds.refresh.assert_called_once_with(
            ANY)  # ANY allows us to assert that refresh was called with any Request instance

        # After refreshing, the credentials should now be valid
        self.assertTrue(creds.valid)  # If refresh worked, creds.valid should now be True
