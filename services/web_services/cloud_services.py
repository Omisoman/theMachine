"""Import Project Management Libraries"""
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.network.urlrequest import UrlRequest
from dotenv import load_dotenv
import json
import os
import certifi

"""Import Services From Modules"""
from ui.services.ui_components import HoverButton
from services.web_services.file_machine import FileMachine

"""Entry Configurations"""
load_dotenv()
Builder.load_file(os.getenv('CLOUD_SERVICES_KV'))

"""CloudServices Main Class"""
class CloudServices(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_functions()

    def load_functions(self):
        hub_file_path = '/tmp/cloud_functions_hub.json'  # Correct path where the JSON is stored

        if not hub_file_path or not os.path.exists(hub_file_path):
            print("Cloud Functions Hub file is not found.")
            return  # Exit if the file is missing

        with open(hub_file_path, 'r') as f:
            functions = json.load(f)

        grid = self.ids.functions_grid
        for function in functions:
            hover_button = HoverButton(
                text=function['Name'],
                size_hint=(None, None),
                size=(200, 50),
                font_name="fonts/PressStart2P-Regular.ttf",
                font_size=24,
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=(0.5, 0.5, 0.5, 1)  # Dimmed text
            )
            hover_button.bind(on_press=self.create_on_function_click_listener(function))
            grid.add_widget(hover_button)

    def create_on_function_click_listener(self, func):
        def on_function_click(instance):
            print(f"Button pressed for function: {func['Name']}")
            if func['Input'] == 'TRIGGER':
                print(f"Trigger function {func['URL']}")  # For debugging
                self.trigger_function(func['URL'])
            elif func['Input'] == 'FILE':
                self.load_file_machine(func)  # Pass function details to load_file_machine

        return on_function_click

    def trigger_function(self, url):
        def on_success(req, result):
            print("Function triggered successfully:", result)

        def on_error(req, result):
            print("Error triggering function:", result)

        print(f"Sending request to {url}")
        headers = {'Content-type': 'application/json'}
        UrlRequest(url, req_body=json.dumps({}), req_headers=headers, on_success=on_success, on_error=on_error,
                   ca_file=certifi.where())

    def load_file_machine(self, function_details):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(FileMachine(function_details=function_details))
        print("Opening file_machine window...", function_details)  # Important tracer


class CloudServicesApp(App):
    def build(self):
        return CloudServices()


if __name__ == '__main__':
    CloudServicesApp().run()
