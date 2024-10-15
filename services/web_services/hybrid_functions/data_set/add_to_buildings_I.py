import os
import csv
import sys
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# BigQuery details from .env
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_NAME = os.getenv("DATASET_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")

# Use credentials from environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("SERVICES_JSON")


def load_csv_to_bigquery(csv_file_path):
    try:
        # Initialize BigQuery client
        client = bigquery.Client()

        # Get table schema
        dataset_ref = client.dataset(DATASET_NAME)
        table_ref = dataset_ref.table(TABLE_NAME)
        table = client.get_table(table_ref)
        table_schema = [schema.name for schema in table.schema]

        # Check CSV headers match with BigQuery table
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)

            if len(headers) != len(table_schema):
                raise ValueError(
                    f"CSV headers count ({len(headers)}) does not match BigQuery table columns ({len(table_schema)}).")

            # If header count matches, proceed with data insertion
            rows_to_insert = [row for row in reader]

            # BigQuery insert
            errors = client.insert_rows(table, rows_to_insert)

            if not errors:
                print(f"CSV file {csv_file_path} successfully uploaded to BigQuery table {TABLE_NAME}.")
            else:
                print(f"Encountered errors while inserting rows:")
                for error in errors:
                    print(error)
    except Exception as e:
        print(f"An error occurred during the BigQuery insertion: {str(e)}")


# Main function to handle command-line argument for the CSV file path
if __name__ == "__main__":
    # Ensure that the CSV file path is passed as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python add_to_buildings_I.py <csv_file_path>")
        sys.exit(1)

    # Get the file path from the command-line argument
    csv_file = sys.argv[1]

    # Call the function to load the CSV into BigQuery
    load_csv_to_bigquery(csv_file)
