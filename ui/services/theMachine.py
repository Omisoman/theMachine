"""Import Project Management Libraries"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import storage
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

"""Import Services From Modules"""
from services.web_services.hybrid_services import HybridServices
from services.app_services.data_sort import DataSortScreen
from services.app_services.data_set import DataSetScreen
from services.web_services.cloud_services import CloudServices
from services.web_services.data_machine import DataMachine

"""Entry Configurations"""
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('SERVICES_JSON')
Window.size = (1200, 800)

"""The Machine Main Class"""
class TheMachineApp(App):

    def build(self):
        if self.check_google_credentials():
            self.check_and_install_requirements()
            self.sync_cloud_function_hub()
            self.load_home()
        else:
            self.root.clear_widgets()
            self.root = Builder.load_file(os.getenv('LOGON_KV'))

    def check_and_install_requirements(self):
        # install any missing libraries for hybrid_services from Google Cloud Storage
        bucket_name = os.getenv('HYBRID_BUCKET')
        requirements_blob_name = os.getenv('HYBRID_REQUIREMENTS_BLOB')
        local_requirements_file = 'requirements.txt'

        try:
            # Initialize Google Cloud Storage client
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(requirements_blob_name)

            # Download the requirements.txt file
            blob.download_to_filename(local_requirements_file)
            print(f"Downloaded {requirements_blob_name} from bucket {bucket_name} to {local_requirements_file}.")

            # Install required libraries using pip
            self.install_requirements_file(local_requirements_file)

        except Exception as e:
            print(f"Failed to check and install requirements: {e}")

    def install_requirements_file(self, requirements_file):
        # Install packages from a requirements.txt file using pip
        try:
            # Using sys.executable to ensure using the right Python environment
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            print(f"Successfully installed packages from {requirements_file}.") #For debugging
        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages from {requirements_file}: {e}")
            print(f"Error output: {e.stderr}")

    def sync_cloud_function_hub(self):
        bucket_name = os.getenv('CLOUD_BUCKET')
        source_blob_name = os.getenv('CLOUD_SOURCE_BLOB')
        destination_file_name = os.getenv('CLOUD_FUNCTIONS_HUB')
        #Sync function hub to cast available functions
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            print(f"Downloaded {source_blob_name} from bucket {bucket_name} to {destination_file_name}.")
        except Exception as e:
            print(f"Failed to download {source_blob_name} from bucket {bucket_name}: {e}")

    def animate_and_sign_in(self):
        self.root.ids.google_logon.pos_hint = {"center_x": 2, "center_y": 2}
        label = self.root.ids.machine_label
        anim = Animation(pos_hint={'center_x': 0.5, 'center_y': 0.7}, duration=0.2)
        anim.bind(on_complete=lambda *x: Clock.schedule_once(self.google_sign_in, 0.1))
        anim.start(label)

    def google_sign_in(self, *args):
        credentials = self.get_google_credentials()
        if credentials:
            self.load_home()

    def get_google_credentials(self, service_account=False):
        creds = None
        token_file = os.getenv('TOKEN_JSON')
        credentials_file = os.getenv('CREDENTIALS_JSON')  # OAuth credentials

        if os.path.exists(token_file):
            with open(token_file, "r") as token:
                creds = Credentials.from_authorized_user_info(json.load(token))

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file,
                                                                 ['https://www.googleapis.com/auth/cloud-platform'])
                creds = flow.run_local_server(port=8000, prompt='consent')
            with open(token_file, "w") as token:
                token.write(creds.to_json())

        return creds

    def check_google_credentials(self):
        token_file = os.getenv('TOKEN_JSON')
        if os.path.exists(token_file):
            with open(token_file, "r") as token:
                creds = Credentials.from_authorized_user_info(json.load(token))
            if creds and creds.valid:
                return True
            elif creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    with open(token_file, "w") as token:
                        token.write(creds.to_json())
                    return True
                except Exception:
                    return False
        return False

    """Load widgets"""
    def load_home(self):
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('THE_MACHINE_KV')))

    def load_services(self):
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('SERVICES_KV')))

    def load_app_services(self):
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('APP_SERVICES_KV')))

    def load_web_services(self):
        self.root.clear_widgets()
        self.root.add_widget(Builder.load_file(os.getenv('WEB_SERVICES_KV')))

    def load_cloud_services(self):
        self.root.clear_widgets()
        self.root.add_widget(CloudServices())

    def load_hybrid_services(self):
        self.root.clear_widgets()
        self.root.add_widget(HybridServices())

    def load_data_sort(self):
        self.root.clear_widgets()
        self.root.add_widget(DataSortScreen())

    def load_data_set(self):
        self.root.clear_widgets()
        self.root.add_widget(DataSetScreen())

    def load_data_machine(self, function_name):
        # Pass the function name to DataMachine when switching to the new window
        self.root.clear_widgets()
        self.root.add_widget(DataMachine(script_name=function_name))


if __name__ == "__main__":
    TheMachineApp().run()
