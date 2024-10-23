#PENDING DEVELOPMENT
"""Import Project Management Libraries"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import secretmanager, storage
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.animation import Animation
from dotenv import load_dotenv
import subprocess
import sys
import os
import json

from services.web_services.hybrid_services import HybridServices
from services.app_services.data_sort import DataSortScreen
from services.app_services.data_set import DataSetScreen
from services.web_services.cloud_services import CloudServices
from services.web_services.data_machine import DataMachine
from services.web_services.admin import CloudDeployer


"""Import Encryption Utilities"""
from utilities.encryption_util import encrypt_data, decrypt_data, get_secure_key, derive_aes_key

"""Helper Functions"""
def get_secret(secret_name):
    """Retrieve the secret value from Google Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.getenv('PROJECT_ID')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def upload_token_to_storage(token_data):
    """Encrypt and upload the token to Google Cloud Storage"""
    client = storage.Client()
    bucket_name = os.getenv('TOKEN')  # The name of your bucket in .env
    token_blob_name = 'oauth_token.json'
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(token_blob_name)

    # Get secure key and derive AES key
    secure_key = get_secure_key()
    aes_key = derive_aes_key(secure_key)

    # Convert token_data to bytes (since it's a JSON string)
    token_data_bytes = token_data.encode('utf-8')

    # Encrypt the token data
    encrypted_token = encrypt_data(token_data_bytes, aes_key)

    # Upload the encrypted token data
    blob.upload_from_string(encrypted_token)
    print(f"Token uploaded to {bucket_name}/{token_blob_name}.")

def download_token_from_storage():
    """Download and decrypt the token from Google Cloud Storage"""
    client = storage.Client()
    bucket_name = os.getenv('TOKEN')  # The name of your bucket in .env
    token_blob_name = 'oauth_token.json'
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(token_blob_name)

    try:
        # Download the encrypted token data
        encrypted_token_data = blob.download_as_text()

        # Get secure key and derive AES key
        secure_key = get_secure_key()
        aes_key = derive_aes_key(secure_key)

        # Decrypt the token data (Keep it as binary data)
        decrypted_token = decrypt_data(encrypted_token_data, aes_key)
        print(f"Token downloaded and decrypted successfully.")
        return decrypted_token  # Return the binary token data
    except Exception as e:
        print(f"Error downloading token: {e}")
        return None  # Return None if the token is not found or decryption fails

def load_service_account_credentials():
    """Load service account credentials from Google Secret Manager"""
    secret_name = os.getenv('SERVICES_JSON')  # Secret name for the service account credentials
    credentials_data = get_secret(secret_name)

    # Write the credentials to a temp file for Google SDKs to use
    credentials_file_path = '/tmp/service_account.json'
    with open(credentials_file_path, 'w') as f:
        f.write(credentials_data)

    # Set the environment variable for Google Cloud SDK
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file_path

def load_cloud_functions_hub():
    """Load the Cloud Functions Hub JSON from Secret Manager"""
    try:
        secret_name = os.getenv('CLOUD_FUNCTIONS_HUB_SECRET')
        cloud_functions_hub_json = get_secret(secret_name)

        functions_data = json.loads(cloud_functions_hub_json)

        with open('/tmp/cloud_functions_hub.json', 'w') as f:
            f.write(cloud_functions_hub_json)

        print(f"Loaded Cloud Functions Hub from secret {secret_name}.")
        return functions_data

    except Exception as e:
        print(f"Failed to load Cloud Functions Hub from Secret Manager: {e}")
        return None

def save_oauth_credentials_to_file():
    """Save the OAuth credentials from Secret Manager to a temporary file"""
    credentials_data = get_secret('oauth_credentials')

    # Save to a temporary file
    credentials_file_path = '/tmp/oauth_credentials.json'
    with open(credentials_file_path, 'w') as f:
        f.write(credentials_data)

    print(f"OAuth credentials saved to {credentials_file_path}.")
    return credentials_file_path

"""Entry Configurations"""
load_dotenv()
load_service_account_credentials()
Window.size = (1200, 800)

"""The Machine Main Class"""
class TheMachineApp(App):

    def build(self):
        """Build the app and check Google credentials"""
        if self.check_google_credentials():
            self.check_and_install_requirements()
            self.sync_cloud_function_hub()
            self.load_home()
        else:
            self.root.clear_widgets()
            self.root = Builder.load_file(os.getenv('LOGON_KV'))

    def check_and_install_requirements(self):
        """Check and install missing libraries from hybrid services in Google Cloud Storage"""
        bucket_name = os.getenv('HYBRID_BUCKET')
        requirements_blob_name = os.getenv('HYBRID_REQUIREMENTS_BLOB')
        local_requirements_file = 'requirements.txt'

        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(requirements_blob_name)
            blob.download_to_filename(local_requirements_file)
            print(f"Downloaded {requirements_blob_name} from bucket {bucket_name}.")

            self.install_requirements_file(local_requirements_file)
        except Exception as e:
            print(f"Failed to check and install requirements: {e}")

    def install_requirements_file(self, requirements_file):
        """Install packages from the requirements.txt file using pip"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            print(f"Successfully installed packages from {requirements_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages from {requirements_file}: {e}")

    def sync_cloud_function_hub(self):
        """Sync the cloud function hub from Google Secret Manager"""
        functions_data = load_cloud_functions_hub()

        if functions_data:
            hub_file_path = '/tmp/cloud_functions_hub.json'
            with open(hub_file_path, 'w') as f:
                json.dump(functions_data, f)
            print(f"Cloud Functions Hub synced to {hub_file_path}.")
        else:
            print("Cloud Functions Hub sync failed.")

    def animate_and_sign_in(self):
        """Trigger Google sign-in animation and process"""
        self.root.ids.google_logon.pos_hint = {"center_x": 2, "center_y": 2}
        label = self.root.ids.machine_label
        anim = Animation(pos_hint={'center_x': 0.5, 'center_y': 0.7}, duration=0.2)
        anim.bind(on_complete=lambda *x: Clock.schedule_once(self.google_sign_in, 0.1))
        anim.start(label)

    def google_sign_in(self, *args):
        """Sign in with Google OAuth"""
        credentials = self.get_google_credentials()
        if credentials:
            self.load_home()

    def get_google_credentials(self):
        """Retrieve or refresh Google credentials"""
        creds = None
        try:
            # Fetch token from Google Cloud Storage instead of Secret Manager
            token_data = download_token_from_storage()
            if token_data:
                creds = Credentials.from_authorized_user_info(json.loads(token_data))

        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

        # If no valid credentials or token, perform sign-in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                new_token_data = creds.to_json()
                self.save_token(new_token_data)  # Save refreshed token
            else:
                credentials_file = save_oauth_credentials_to_file()  # Save OAuth credentials to temp file
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file,
                                                                 ['https://www.googleapis.com/auth/cloud-platform'])
                creds = flow.run_local_server(port=8000, prompt='consent')
                new_token_data = creds.to_json()
                self.save_token(new_token_data)  # Save new token to storage

        return creds

    def save_token(self, token_data):
        """Save the OAuth token to Google Cloud Storage"""
        upload_token_to_storage(token_data)
        print(f"Saved token data to storage.")

    def check_google_credentials(self):
        """Check if the Google credentials are valid"""
        token_data = download_token_from_storage()

        if token_data:
            try:
                # Convert the token data back to a dictionary (if it's JSON data)
                creds = Credentials.from_authorized_user_info(json.loads(token_data))
                if creds and creds.valid:
                    print("Token is valid.")
                    return True
                elif creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self.save_token(creds.to_json())
                    print("Token refreshed and saved.")
                    return True
            except Exception as e:
                print(f"Error loading credentials: {e}")
                return False
        else:
            # Token is missing, perform Google sign-in to get new credentials
            creds = self.get_google_credentials()
            return creds is not None

        return False

    # Load widgets

    def load_home(self):
        """Load the main home screen"""
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('THE_MACHINE_KV')))

    def load_services(self):
        """Load services screen"""
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('SERVICES_KV')))

    def load_admin(self):
        """Load admin screen"""
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('ADMIN_KV')))

    def cloud_deployer(self, deploy_type):
        """Load Cloud Deployer screen and pass the deploy type ('function_deployer' or 'script_deployer')."""
        # Clear the current screen
        self.root.clear_widgets()
        # Load the CloudDeployer screen from the KV file
        self.root.add_widget(Builder.load_file(os.getenv('CLOUD_DEPLOYER_KV')))
        # Pass the deploy_type to the CloudDeployer class instance (if needed)
        self.root.children[0].deploy_type = deploy_type  # Example of passing deploy_type

    def load_app_services(self):
        """Load app services screen"""
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('APP_SERVICES_KV')))

    def load_web_services(self):
        """Load web services screen"""
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('WEB_SERVICES_KV')))

    def load_cloud_services(self):
        """Load cloud services screen"""
        self.root.clear_widgets()
        self.root.add_widget(CloudServices())

    def load_hybrid_services(self):
        """Load hybrid services screen"""
        self.root.clear_widgets()
        self.root.add_widget(HybridServices())

    def load_data_sort(self):
        """Load data sort screen"""
        self.root.clear_widgets()
        self.root.add_widget(DataSortScreen())

    def load_data_set(self):
        """Load data set screen"""
        self.root.clear_widgets()
        self.root.add_widget(DataSetScreen())

    def load_data_machine(self, function_name):
        """Load data machine screen with a specific function"""
        self.root.clear_widgets()
        self.root.add_widget(DataMachine(script_name=function_name))


if __name__ == "__main__":
    TheMachineApp().run()
