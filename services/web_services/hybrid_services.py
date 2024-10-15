"""Import Project Management Libraries"""
from google.cloud import storage
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from dotenv import load_dotenv
from pathlib import Path
import sys
import subprocess
import os
import shutil

"""Import Services From Modules"""
from ui.services.ui_components import HoverButton

"""Entry Configurations"""
load_dotenv()
Builder.load_file(os.getenv('HYBRID_SERVICES_KV'))

"""HybridServices Main Class"""
class HybridServices(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_functions()

    def load_functions(self):
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()

        bucket_name = os.getenv('HYBRID_BUCKET')
        source_blob = os.getenv('HYBRID_SOURCE_BLOB')

        # Access the bucket
        bucket = storage_client.bucket(bucket_name)

        # List blobs in the specified path
        blobs = bucket.list_blobs(prefix='data_set/')

        # Filter and sort .py files
        functions = [
            blob.name for blob in blobs if blob.name.endswith('.py')
        ]
        # Sort by file name, without the '.py' extension
        functions = sorted([os.path.basename(f).replace('.py', '') for f in functions])

        # Get the GridLayout for adding buttons
        grid = self.ids.scripts_grid

        # Create a button for each function
        for function in functions:
            hover_button = HoverButton(
                text=function,  # Display the file name without '.py'
                size_hint=(None, None),
                size=(200, 50),
                font_name="fonts/PressStart2P-Regular.ttf",
                font_size=24,
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=(0.5, 0.5, 0.5, 1) # Dimmed text
            )
            hover_button.bind(on_press=self.create_on_function_click_listener(function))
            grid.add_widget(hover_button)

    def create_on_function_click_listener(self, function_name):
        def on_click(instance): #File name check and direct
            if function_name.endswith('_I'): # _I for require input scripts
                print(f"Opening data machine window for {function_name}") #For debugging
                App.get_running_app().load_data_machine(function_name)
            elif function_name.endswith('_O'): # _O for require output scripts
                print(f"Executing script {function_name}")
                self.execute_script(function_name)  # Call the method to execute the script

        return on_click

    def execute_script(self, function_name, *args):
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()

        # Download the script from Google Cloud Storage
        bucket_name = os.getenv('HYBRID_BUCKET')
        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(f"data_set/{function_name}.py")

        # Detect the operating system and set the script path accordingly
        if sys.platform.startswith('win'):
            # For Windows, using backslashes in the path
            script_path = f"C:\\temp\\{function_name}.py"
        else:
            # For macOS or Linux, using forward slashes in the path
            script_path = f"/tmp/{function_name}.py"

        blob.download_to_filename(script_path)

        # Detect the correct Python executable based on the environment
        if sys.platform.startswith('win'):
            python_executable = 'python'
        else:
            python_executable = 'python3'

        # Execute the script using subprocess and capture the output
        result = subprocess.run([python_executable, script_path], capture_output=True, text=True)

        if result.returncode == 0:
            # File name check and direct
            file_type = function_name.split('_as_')[-1].replace('_O', '')

            # Define the output file extension based on the file type
            file_extension = {
                'json': 'json',
                'xls': 'xls',
                'xlsx': 'xlsx',
                'csv': 'csv',
                'txt': 'txt',
                'pdf': 'pdf',
                'xml': 'xml',
                # Add more file types as needed
            }.get(file_type, 'txt')  # Default to 'txt' if no match

            # The script output is in result.stdout
            output_content = result.stdout

            # Save the output to the Desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            output_dir = Path(desktop_path) / f"{function_name}_output"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save the output in the appropriate format
            output_file = output_dir / f"{function_name}_output.{file_extension}"
            with open(output_file, 'w') as f:
                f.write(output_content)

            # Compress the output folder as part of every execution
            zip_file_path = output_dir.with_suffix('.zip')
            shutil.make_archive(output_dir, 'zip', output_dir)
            print(f"Output saved and compressed at: {zip_file_path}")
        else:
            print(f"Error executing script {function_name}: {result.stderr}")