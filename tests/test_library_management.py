import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Assuming TheMachineApp is the class you're testing and check_and_install_requirements is the method.
from ui.services.theMachine import TheMachineApp

class TestTheMachineApp(unittest.TestCase):

    @patch('ui.services.theMachine.storage.Client')  # Mock the Google Cloud Storage client
    @patch('ui.services.theMachine.subprocess.run')  # Mock subprocess.run to avoid actual pip installations
    def test_check_and_install_requirements(self, mock_subprocess_run, mock_storage_client):
        # Set up environment variables that your method relies on
        os.environ['HYBRID_BUCKET'] = 'test-bucket'
        os.environ['HYBRID_REQUIREMENTS_BLOB'] = 'requirements.txt'

        # Mock the bucket and blob objects
        mock_bucket = MagicMock()
        mock_blob = MagicMock()

        # Set up the return value for the storage.Client().bucket().blob() calls
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Mock the download method (avoid downloading the actual file)
        mock_blob.download_to_filename.return_value = None

        # Mock the subprocess.run call to simulate pip installation
        mock_subprocess_run.return_value = MagicMock(stdout="Successfully installed")

        # Create an instance of TheMachineApp
        app = TheMachineApp()

        # Call the method under test
        app.check_and_install_requirements()

        # Assertions to verify that the methods were called with the expected parameters
        mock_storage_client.assert_called_once()  # Ensure storage client is instantiated
        mock_bucket.blob.assert_called_with('requirements.txt')  # Check correct blob is accessed
        mock_blob.download_to_filename.assert_called_with('requirements.txt')  # File download check
        mock_subprocess_run.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-r", 'requirements.txt'],
            check=True,
            capture_output=True,
            text=True
        )
        self.assertIn("Successfully installed", mock_subprocess_run.return_value.stdout)

if __name__ == '__main__':
    unittest.main()
