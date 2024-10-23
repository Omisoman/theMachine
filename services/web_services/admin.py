#PENDING DEVELOPMENT
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
import os
from google.cloud import secretmanager, storage
from utilities.encryption_util import encrypt_data, derive_aes_key, get_secure_key

class CloudDeployer(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.deployer_type = None
        self.encryption_key = derive_aes_key(get_secure_key())  # Get secure encryption key

        # Bind the new event 'on_drop_file' (instead of deprecated 'on_dropfile')
        Window.bind(on_drop_file=self.handle_drop_file)

    def handle_drop_file(self, window, file_path, x, y, *args):
        """Handle files dragged and dropped on the window."""
        file_path = file_path.decode('utf-8')  # Convert byte string to regular string
        file_extension = os.path.splitext(file_path)[1].lower()

        print(f"File dropped: {file_path}")  # Log the file path and type
        print(f"File extension: {file_extension}")

        if self.deployer_type == 'function_deployer' and file_extension == '.json':
            print("Processing as function_deployer")
            self.deploy_to_secret_manager(file_path)
        elif self.deployer_type == 'script_deployer' and file_extension == '.py':
            print("Processing as script_deployer")
            self.deploy_encrypted_script_to_bucket(file_path)
        else:
            print(f"Invalid file type: {file_extension}. Expected: {self.deployer_type}")
            self.ids.files_drop.text = f"Invalid file type: {file_extension}"
            return

        # If everything goes well, log the acceptance and processing
        print("File accepted for processing.")

    def deploy_to_secret_manager(self, file_path):
        """Deploy JSON file to Secret Manager (CLOUD_FUNCTIONS_HUB)."""
        print(f"Deploying to Secret Manager: {file_path}")
        client = secretmanager.SecretManagerServiceClient()
        secret_name = os.getenv('CLOUD_FUNCTIONS_HUB_SECRET')

        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                json_data = f.read()

            # Upload the new version of the secret
            project_id = os.getenv('PROJECT_ID')
            secret_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.add_secret_version(parent=secret_name, payload={'data': json_data.encode()})

            print(f"Function deployed to Secret Manager, version: {response.name}")
        except Exception as e:
            print(f"Failed to deploy function: {e}")
            self.ids.status_label.text = "Deployment failed."

    def deploy_encrypted_script_to_bucket(self, file_path):
        """Encrypt and deploy PY file to Google Cloud Storage."""
        print(f"Uploading script to bucket: {file_path}")
        client = storage.Client()
        bucket_name = os.getenv('HYBRID_BUCKET')
        blob_name = f"{os.getenv('HYBRID_SOURCE_BLOB')}{os.path.basename(file_path)}"

        try:
            # Read the Python file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Encrypt the file
            encrypted_data = encrypt_data(file_data, self.encryption_key)

            # Upload encrypted data to Cloud Storage
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(encrypted_data)

            print(f"Encrypted script uploaded to {bucket_name}/{blob_name}.")
        except Exception as e:
            print(f"Failed to upload script: {e}")
            self.ids.status_label.text = "Upload failed."

    def on_leave(self):
        """Unbind the event when leaving the screen"""
        Window.unbind(on_drop_file=self.handle_drop_file)
