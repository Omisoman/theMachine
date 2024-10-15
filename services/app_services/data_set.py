"""Import Project Management Libraries"""
from google.cloud import bigquery
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.clock import Clock
from dotenv import load_dotenv
import os

"""Entry Configurations"""
load_dotenv()
Builder.load_file(os.getenv('DATA_SET_KV'))

"""DataSet Main Class"""
class DataSetScreen(FloatLayout):
    selected_dataset = None
    selected_table = None
    selected_columns = set()  # For multi-selection columns
    all_selected = False  # Track the state for select all/unselect all

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fetch_datasets()

    def fetch_datasets(self):
        client = bigquery.Client()
        datasets = [dataset.dataset_id for dataset in client.list_datasets()]
        self.selected_dataset = datasets[0] if datasets else None
        Clock.schedule_once(lambda dt: self.update_datasets(datasets))
        # Automatically fetch tables for the selected dataset
        if self.selected_dataset:
            self.fetch_tables(self.selected_dataset)

    def fetch_tables(self, dataset_name):
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_name)
        tables = [table.table_id for table in client.list_tables(dataset_ref)]
        self.selected_table = tables[0] if tables else None
        Clock.schedule_once(lambda dt: self.update_tables(tables))
        # Automatically fetch columns for the selected table
        if self.selected_table:
            self.fetch_columns(self.selected_table)

    def fetch_columns(self, table_name):
        client = bigquery.Client()
        table_ref = client.dataset(self.selected_dataset).table(table_name)
        table = client.get_table(table_ref)
        columns = [schema_field.name for schema_field in table.schema]
        Clock.schedule_once(lambda dt: self.update_columns(columns))

    def update_datasets(self, datasets):
        box_layout = self.ids.datasets_box
        box_layout.clear_widgets()
        for dataset in datasets:
            btn = Button(
                text=dataset,
                font_size=12,
                font_name="fonts/PressStart2P-Regular.ttf",
                size_hint_y=None,
                height=40,
                background_color=(0, 0, 0, 0),  # Transparent background
                color=(0.5, 0.5, 0.5, 1)  # Dimmed text
            )
            btn.bind(on_press=self.on_dataset_select)
            box_layout.add_widget(btn)
        self.highlight_selected_dataset()

    def update_tables(self, tables):
        box_layout = self.ids.tables_box
        box_layout.clear_widgets()
        for table in tables:
            btn = Button(
                text=table,
                font_size=12,
                font_name="fonts/PressStart2P-Regular.ttf",
                size_hint_y=None,
                height=40,
                background_color=(0, 0, 0, 0),  # Transparent background
                color=(0.5, 0.5, 0.5, 1)  # Dimmed text
            )
            btn.bind(on_press=self.on_table_select)
            box_layout.add_widget(btn)
        self.highlight_selected_table()

    def update_columns(self, columns):
        box_layout = self.ids.columns_box
        box_layout.clear_widgets()
        for column in columns:
            btn = Button(
                text=column,
                font_size=12,
                font_name="fonts/PressStart2P-Regular.ttf",
                size_hint_y=None,
                height=40,
                background_color=(0, 0, 0, 0),  # Transparent background
                color=(0.5, 0.5, 0.5, 1)  # Dimmed text
            )
            btn.bind(on_press=self.on_column_select)
            box_layout.add_widget(btn)
        self.highlight_selected_columns()

    def on_dataset_select(self, instance):
        self.selected_dataset = instance.text
        self.fetch_tables(self.selected_dataset)
        self.highlight_selected_dataset()

    def on_table_select(self, instance):
        self.selected_table = instance.text
        self.fetch_columns(self.selected_table)
        self.highlight_selected_table()

    def on_column_select(self, instance):
        column = instance.text
        if column in self.selected_columns:
            self.selected_columns.remove(column)
        else:
            self.selected_columns.add(column)
        self.highlight_selected_columns()

    def highlight_selected_dataset(self):
        for btn in self.ids.datasets_box.children:
            btn.color = (1, 1, 1, 1) if btn.text == self.selected_dataset else (0.5, 0.5, 0.5, 1)

    def highlight_selected_table(self):
        for btn in self.ids.tables_box.children:
            btn.color = (1, 1, 1, 1) if btn.text == self.selected_table else (0.5, 0.5, 0.5, 1)

    def highlight_selected_columns(self):
        for btn in self.ids.columns_box.children:
            btn.color = (1, 1, 1, 1) if btn.text in self.selected_columns else (0.5, 0.5, 0.5, 1)

    def view_records(self):
        if not self.selected_dataset or not self.selected_table or not self.selected_columns:
            print("Please select a dataset, table, and columns to view records.") #For debugging
            return

        client = bigquery.Client()
        dataset_table = f"{self.selected_dataset}.{self.selected_table}"
        query = f"SELECT {', '.join(self.selected_columns)} FROM `{dataset_table}` LIMIT 100"

        query_job = client.query(query)
        results = query_job.result()

        # Convert RowIterator to list to allow indexing
        results_list = list(results)

        self.display_records(results_list)

    def display_records(self, results):
        records_view = self.ids.records_view
        records_grid = self.ids.records_grid

        # Set the number of columns for GridLayout
        num_columns = len(self.selected_columns)
        records_grid.cols = num_columns
        records_grid.clear_widgets()

        font_size = 12

        # Adding headers with column names
        for column in self.selected_columns:
            lbl = Label(
                text=column,
                size_hint_x=None,
                width=120,
                size_hint_y=None,
                height=40,
                font_name="fonts/PressStart2P-Regular.ttf",
                font_size=font_size,
                color=(1, 1, 1, 1)
            )
            records_grid.add_widget(lbl)

        # Adding rows with records
        for row in results:
            for column in self.selected_columns:
                lbl = Label(
                    text=str(row[column]),
                    size_hint_x=None,
                    width=120,
                    size_hint_y=None,
                    height=40,
                    font_name="fonts/PressStart2P-Regular.ttf",
                    font_size=font_size,
                    color=(1, 1, 1, 1)
                )
                records_grid.add_widget(lbl)

        # Resize the GridLayout to fit its content
        records_grid.bind(minimum_width=records_grid.setter('width'))
        records_grid.bind(minimum_height=records_grid.setter('height'))

    def all_records(self): #Records selection button behavior
        if self.all_selected:
            self.selected_columns.clear()
        else:
            box_layout = self.ids.columns_box
            self.selected_columns = {btn.text for btn in box_layout.children}

        self.all_selected = not self.all_selected
        self.highlight_selected_columns()
