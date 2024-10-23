#PENDING DEVELOPMENT
"""Import Project Management Libraries"""
from google.cloud import storage
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from dotenv import load_dotenv
import sys
import os
import subprocess

"""Entry Configurations"""
load_dotenv()
Builder.load_file(os.getenv('DATA_MACHINE_KV'))

"""DataMachine Main Class"""
class DataMachine(FloatLayout):
    def __init__(self, script_name, **kwargs):
        super().__init__(**kwargs)
        self.script_name = script_name  # Store the selected script name
        self.accepted_files = []  # Store accepted files in memory
        self.update_status(f"<PYTHON_SCRIPT>: {self.script_name}")
        Window.bind(on_drop_file=self.handle_drop_file)  # Bind drag-and-drop

    def handle_drop_file(self, window, file_path, x, y, *args):
        # Handle files dragged and dropped on the window
        file_path = file_path.decode('utf-8')  # Convert byte string to regular string
        self.accepted_files.append(file_path)
        self.update_status(f"{len(self.accepted_files)} file(s) ready for processing.")
        self.process_files()

    def process_files(self):
        # Process the dropped files by sending them to the selected script
        self.update_status("processing files...")

        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket_name = os.getenv('HYBRID_BUCKET')
        source_blob = os.getenv('HYBRID_SOURCE_BLOB')
        bucket = storage_client.bucket(bucket_name)

        # Download the script from Cloud Storage
        script_blob = bucket.blob(f"data_set/{self.script_name}.py")

        # Detect the operating system and set the script path accordingly
        if sys.platform.startswith('win'):
            # For Windows, using backslashes in the path
            script_path = f"C:\\temp\\{self.script_name}.py"
        else:
            # For macOS or Linux, using forward slashes in the path
            script_path = f"/tmp/{self.script_name}.py"

        script_blob.download_to_filename(script_path)

        # Execute the script for each dropped file
        for file_path in self.accepted_files:
            self.update_status(f"processing {file_path}...")
            result = self.execute_script(script_path, file_path)

            if result:
                self.update_status(f"file {file_path} processed successfully.")
            else:
                self.update_status(f"error processing {file_path}")

        # After processing all files, update status and reset after 5 seconds
        self.update_status("all files processed successfully.")
        Clock.schedule_once(self.reset_status, 5)  # Reset the status after 5 seconds

    def execute_script(self, script_path, file_path):
        # Execute the downloaded script with the file as input and capture logs
        try:
            # Detect the Python executable based on the operating system
            if sys.platform.startswith('win'):
                python_executable = 'python'
            else:
                python_executable = 'python3'

            # Run the script using subprocess and pass the file as an argument
            result = subprocess.run([python_executable, script_path, file_path], capture_output=True, text=True)

            # Check if the script executed successfully
            if result.returncode == 0:
                print(f"Script executed successfully for {file_path}")
                print(f"Output: {result.stdout}")
                return True
            else:
                print(f"Error executing script {self.script_name} for {file_path}: {result.stderr}")  # For debugging
                return False
        except Exception as e:
            print(f"An error occurred while executing the script: {str(e)}")
            return False


    def update_status(self, message):
        self.ids.data_drop.text = message

    def reset_status(self, *args):
        self.ids.data_drop.text = "drop files here"

    def on_leave(self):
        Window.unbind(on_drop_file=self.handle_drop_file) # Unbind window
