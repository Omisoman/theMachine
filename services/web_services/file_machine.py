"""Import Project Management Libraries"""
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from pathlib import Path
from kivy.clock import Clock
import os
import zipfile
import requests
import chardet

"""Import Encryption Utilities"""
from utilities.encryption_util import encrypt_file_data, decrypt_file_data, get_secure_key, derive_aes_key

"""Entry Configurations"""
Builder.load_file(os.getenv('FILE_MACHINE_KV'))

"""FileMachine Main Class"""
class FileMachine(FloatLayout):
    def __init__(self, function_details, **kwargs):
        super().__init__(**kwargs)
        self.function_details = function_details
        self.accepted_files = []  # Store accepted files in memory
        self.allowed_extension = function_details['Input_Type']  # Allowed file type
        self.processed_files = []  # Store processed file paths
        self.encryption_key = derive_aes_key(get_secure_key())  # Retrieve the encryption key
        self.display_function_details()

        # Bind the Window to handle file drop
        Window.bind(on_drop_file=self.handle_drop_file)

    def display_function_details(self):
        """Display the function details in the app"""
        name_label = Label(text=f"Name: {self.function_details['Name']}",
                           font_name="fonts/PressStart2P-Regular.ttf",
                           font_size=22,
                           color=(1, 1, 1, 1),
                           pos_hint={"center_x": 0.5, "center_y": 0.375})
        self.add_widget(name_label)

        root_label = Label(text=f"Root: {self.function_details['Root']}",
                           font_name="fonts/PressStart2P-Regular.ttf",
                           font_size=22,
                           color=(1, 1, 1, 1),
                           pos_hint={"center_x": 0.5, "center_y": 0.275})
        self.add_widget(root_label)

        input_type_label = Label(text=f"Input Type: {self.function_details['Input_Type']}",
                                 font_name="fonts/PressStart2P-Regular.ttf",
                                 font_size=22,
                                 color=(1, 1, 1, 1),
                                 pos_hint={"center_x": 0.5, "center_y": 0.175})
        self.add_widget(input_type_label)

        output_type_label = Label(text=f"Output Type: {self.function_details['Output_Type']}",
                                  font_name="fonts/PressStart2P-Regular.ttf",
                                  font_size=22,
                                  color=(1, 1, 1, 1),
                                  pos_hint={"center_x": 0.5, "center_y": 0.075})
        self.add_widget(output_type_label)

    def handle_drop_file(self, window, file_path, x, y, *args):
        """Handle files dragged and dropped on the window."""
        file_path = file_path.decode('utf-8')  # Convert byte string to regular string
        file_extension = os.path.splitext(file_path)[1][1:]  # Get file extension

        # Check if the file has the same type as Input_Type
        if file_extension != self.allowed_extension:
            self.accepted_files.clear()  # Clear the list as the files are not valid
            return

        self.accepted_files.append(file_path)

        # Check all previously accepted files again to ensure they are of the same type
        for file in self.accepted_files:
            if os.path.splitext(file)[1][1:] != self.allowed_extension:
                self.accepted_files.clear()
                return

        # Start processing files
        self.process_files()

    def detect_encoding(self, file_path):
        """Detect file encoding using chardet."""
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Read a portion of the file
            result = chardet.detect(raw_data)
            return result['encoding']

    def process_files(self):
        self.ids.files_drop.text = "Processing files..."
        url = self.function_details['URL']
        output_dir = Path(f"{os.path.expanduser('~')}/Desktop/{self.function_details['Root']}")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_extension = self.function_details['Output_Type']

        for file_path in self.accepted_files:
            filename = os.path.basename(file_path)
            input_extension = os.path.splitext(filename)[1][1:]

            output_filename = filename.replace(f".{input_extension}", f".{output_extension}")

            # Read file as binary
            with open(file_path, 'rb') as file:
                file_content = file.read()  # Binary file content

            if file_content:
                # Encrypt file data as binary
                encrypted_file_data = encrypt_file_data(file_content, self.encryption_key)

                # Send the encrypted binary data to the cloud function
                files = {'file': (filename, encrypted_file_data)}

                response = requests.post(url, files=files)

                if response.status_code == 200:
                    # Decrypt the received binary file data
                    decrypted_file_data = decrypt_file_data(response.content, self.encryption_key)

                    output_file_path = output_dir / output_filename
                    with open(output_file_path, 'wb') as f:
                        f.write(decrypted_file_data)  # Write as binary

                    self.processed_files.append(output_file_path)
                else:
                    print(f"Failed to process file {filename}: {response.text}")

        self.compress_files(output_dir)

    def compress_files(self, output_dir):
        self.ids.files_drop.text = "Compressing files..."  # Update label to show compressing status
        zip_file_path = output_dir.with_suffix('.zip')

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file in self.processed_files:
                zipf.write(file, arcname=file.name)

        print(f"Files compressed and saved at: {zip_file_path}")
        self.ids.files_drop.text = "Files saved to Desktop!"
        Clock.schedule_once(self.reset_files_drop_label, 5)

    def reset_files_drop_label(self, *args):
        self.ids.files_drop.text = "Drop files here"

    def on_leave(self):
        Window.unbind(on_drop_file=self.handle_drop_file)
