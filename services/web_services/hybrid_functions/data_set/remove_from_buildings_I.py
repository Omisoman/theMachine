"""THIS SCRIPT IS PENDING DEVELOPMENT STILL"""
import os
import csv
import sys
import time  # Add this to handle retry
from google.cloud import bigquery
from dotenv import load_dotenv
import logging

# Load environment variables from .env
load_dotenv()

# BigQuery details from .env
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_NAME = os.getenv("DATASET_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")

# Path to credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("SERVICES_JSON")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_rows_from_bigquery(csv_file_path):
    try:
        # Initialize BigQuery client
        client = bigquery.Client()

        # Get table schema
        dataset_ref = client.dataset(DATASET_NAME)
        table_ref = dataset_ref.table(TABLE_NAME)
        table = client.get_table(table_ref)
        table_schema = [schema for schema in table.schema]

        # Prepare SQL DELETE statement for BigQuery
        def generate_delete_query(row):
            conditions = []
            for i, value in enumerate(row):
                col_name = table_schema[i].name
                col_type = table_schema[i].field_type

                # Cast the value based on the column type
                if col_type == 'STRING':
                    conditions.append(f"{col_name} = '{value}'")
                elif col_type == 'INT64':
                    conditions.append(f"{col_name} = {int(value)}")
                elif col_type == 'BOOL':
                    bool_value = True if value.strip().lower() == 'y' else False
                    conditions.append(f"{col_name} = {bool_value}")
                elif col_type == 'DATE':
                    # Format the date to YYYY-MM-DD
                    formatted_date = value.strip().replace('/', '-')
                    conditions.append(f"{col_name} = '{formatted_date}'")

            return f"DELETE FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}` WHERE {' AND '.join(conditions)}"

        # Read CSV file and skip headers
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Skip headers
            rows = [row for row in reader]

            # For each row, generate a delete query and execute it
            for row in rows:
                if len(row) != len(table_schema):
                    logging.error(
                        f"CSV row length ({len(row)}) does not match table column count ({len(table_schema)}).")
                    continue

                delete_query = generate_delete_query(row)
                logging.info(f"Executing query: {delete_query}")

                # Try executing the delete query, and handle streaming buffer errors
                retry_count = 0
                while retry_count < 5:
                    try:
                        query_job = client.query(delete_query)
                        query_job.result()  # Wait for the query to complete
                        logging.info(f"Row {row} deleted from {TABLE_NAME}.")
                        break  # Exit the retry loop on success
                    except Exception as e:
                        if "streaming buffer" in str(e):
                            logging.warning("Row is in the streaming buffer. Retrying in 5 minutes...")
                            time.sleep(300)  # Wait for 5 minutes before retrying
                            retry_count += 1
                        else:
                            logging.error(f"An error occurred: {e}")
                            break

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

# Main function to handle command-line argument for the CSV file path
if __name__ == "__main__":
    # Ensure that the CSV file path is passed as a command-line argument
    if len(sys.argv) != 2:
        logging.error("Usage: python delete_from_bigquery.py <csv_file_path>")
        sys.exit(1)

    # Get the file path from the command-line argument
    csv_file = sys.argv[1]

    # Call the function to delete rows from BigQuery
    delete_rows_from_bigquery(csv_file)
