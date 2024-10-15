"""Import Project Management Libraries"""
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.graphics import Color, Line
from dotenv import load_dotenv
import pyperclip
import os
import re

"""Entry Configurations"""
load_dotenv()
Builder.load_file(os.getenv('DATA_SORT_KV'))

"""DataSort Main Class"""
class DataSortScreen(FloatLayout):
    text_input_2 = None
    separator_mode = 0

    def toggle_text_inputs(self):
        if self.ids.lookup_button.text == "lookup":
            self.ids.text_input_1.text = ''
            self.ids.lookup_button.text = "x "
            self.text_input_2 = TextInput(
                hint_text="enter text",
                font_name="fonts/PressStart2P-Regular.ttf",
                font_size=20,
                multiline=True,
                size_hint=(None, None),
                size=(300, 300),
                foreground_color=(1, 1, 1, 1),
                background_color=(0, 0, 0, 0),
                background_normal='',
                background_active='',
                pos_hint={"center_x": 0.7, "center_y": 0.48},
                padding=[10, 10]
            )
            self.text_input_2.bind(pos=self.update_canvas, size=self.update_canvas)
            self.add_widget(self.text_input_2)
            self.ids.text_input_1.pos_hint = {"center_x": 0.3, "center_y": 0.48}
        else:
            self.ids.lookup_button.text = "lookup"
            self.ids.text_input_1.text = ''
            self.ids.read_button.pos_hint = {"center_x": 0.5, "center_y": 0.1}
            self.ids.clear_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.a_difference_b_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.b_difference_a_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.a_union_b_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.a_intersection_b_button.pos_hint = {"center_x": 2, "center_y": 2}
            if self.text_input_2:
                self.remove_widget(self.text_input_2)
                self.text_input_2 = None
            self.ids.text_input_1.pos_hint = {"center_x": 0.5, "center_y": 0.48}

    def update_canvas(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)
            Line(width=2, rectangle=(instance.x, instance.y, instance.width, instance.height))

    def clean_text_input(self, text_input):
        raw_text = text_input.text
        cleaned_list = re.split(r'\W+', raw_text)
        cleaned_list = list(filter(None, cleaned_list))
        cleaned_text = '\n'.join(cleaned_list)
        text_input.text = cleaned_text

    def process_input_data(self):
        if re.search(r'[a-zA-Z0-9]', self.ids.text_input_1.text) and self.ids.lookup_button.text != "x ":
            self.clean_text_input(self.ids.text_input_1)
            self.ids.separate_button.pos_hint = {"center_x": 0.85, "center_y": 0.1}
            self.ids.deduplicate_button.pos_hint = {"center_x": 0.15, "center_y": 0.1}
            self.ids.clear_button.pos_hint = {"center_x": 0.5, "center_y": 0.1}
            self.ids.read_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.lookup_button.pos_hint = {"center_x": 2, "center_y": 2}

        if self.ids.lookup_button.text == "x " and self.ids.text_input_1:
            self.clean_text_input(self.ids.text_input_1)

        if self.ids.lookup_button.text == "x " and self.text_input_2:
            self.clean_text_input(self.text_input_2)

        if self.ids.lookup_button.text == "x " and self.text_input_2.text and self.ids.text_input_1.text:
            self.clean_text_input(self.ids.text_input_1)
            self.clean_text_input(self.text_input_2)
            self.ids.a_difference_b_button.pos_hint = {"center_x": 0.3, "center_y": 0.2}
            self.ids.b_difference_a_button.pos_hint = {"center_x": 0.7, "center_y": 0.2}
            self.ids.a_union_b_button.pos_hint = {"center_x": 0.3, "center_y": 0.1}
            self.ids.a_intersection_b_button.pos_hint = {"center_x": 0.7, "center_y": 0.1}
            self.ids.read_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.clear_button.pos_hint = {"center_x": 0.5, "center_y": 0.1}

    def clear_input_data(self):
        self.ids.text_input_1.text = ''
        if self.text_input_2:
            self.text_input_2.text = ''
        if self.ids.lookup_button.text == "x ":
            self.ids.a_difference_b_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.b_difference_a_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.a_union_b_button.pos_hint = {"center_x": 2, "center_y": 2}
            self.ids.a_intersection_b_button.pos_hint = {"center_x": 2, "center_y": 2}
        self.ids.clear_button.pos_hint = {"center_x": 2, "y": 2}
        self.ids.deduplicate_button.pos_hint = {"center_x": 2, "center_y": 2}
        self.ids.separate_button.pos_hint = {"center_x": 2, "center_y": 2}
        self.ids.read_button.pos_hint = {"center_x": 0.5, "center_y": 0.1}
        self.ids.lookup_button.pos_hint = {"center_x": 0.9, "center_y": 0.9}

    def deduplicate_text(self):
        raw_text = self.ids.text_input_1.text
        cleaned_list = re.split(r'\W+', raw_text)
        cleaned_list = list(dict.fromkeys(filter(None, cleaned_list)))
        cleaned_text = '\n'.join(cleaned_list)
        self.ids.text_input_1.text = cleaned_text

    def separate_text(self):
        raw_text = self.ids.text_input_1.text


        if "'," in raw_text:
            text_list = raw_text.replace("'", "").split(',')
            cleaned_text = ',\n'.join([f'"{item.strip()}"' for item in text_list if item.strip()])
            self.ids.text_input_1.text = cleaned_text
            return


        if '",' in raw_text:
            text_list = raw_text.replace('"', '').split(',')
            cleaned_text = ',\n'.join([item.strip() for item in text_list if item.strip()])
            self.ids.text_input_1.text = cleaned_text
            return


        if ',' in raw_text:
            text_list = raw_text.split(',')
            cleaned_text = ',\n'.join([f"'{item.strip()}'" for item in text_list if item.strip()])
            self.ids.text_input_1.text = cleaned_text
            return


        text_list = raw_text.splitlines()
        cleaned_text = ',\n'.join(text_list)
        self.ids.text_input_1.text = cleaned_text

    def set_difference(self):
        set_a = set(self.ids.text_input_1.text.splitlines())
        set_b = set(self.text_input_2.text.splitlines())
        result = set_a - set_b
        self.copy_to_clipboard(result)

    def set_difference_b_a(self):
        set_a = set(self.ids.text_input_1.text.splitlines())
        set_b = set(self.text_input_2.text.splitlines())
        result = set_b - set_a
        self.copy_to_clipboard(result)

    def set_union(self):
        set_a = set(self.ids.text_input_1.text.splitlines())
        set_b = set(self.text_input_2.text.splitlines())
        result = set_a | set_b
        self.copy_to_clipboard(result)

    def set_intersection(self):
        set_a = set(self.ids.text_input_1.text.splitlines())
        set_b = set(self.text_input_2.text.splitlines())
        result = set_a & set_b
        self.copy_to_clipboard(result)

    def copy_to_clipboard(self, result_set):
        result = '\n'.join(result_set)
        if result != '':
            pyperclip.copy(result)  # Copy the result to clipboard
            self.show_copied_label()

    def show_copied_label(self):
        self.ids.copied_label.opacity = 1
        Clock.schedule_once(self.hide_copied_label, 1)

    def hide_copied_label(self, dt):
        self.ids.copied_label.opacity = 0
