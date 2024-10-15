import os
import json
from google.cloud import bigquery
from dotenv import load_dotenv
from datetime import date, datetime

# Load environment variables from .env
load_dotenv()

# BigQuery details from .env
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_NAME = os.getenv("DATASET_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")

# Path to credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("SERVICES_JSON")

def extract_table_as_json():
    # Initialize BigQuery client
    client = bigquery.Client()

    # Query to extract all data from the specified table
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`"
    query_job = client.query(query)

    # Execute the query and fetch the results
    rows = query_job.result()

    # Convert rows to a list of dictionaries (for JSON output)
    result_list = [dict(row) for row in rows]

    # Return the result as a JSON string with a custom encoder
    return json.dumps(result_list, default=json_serial, indent=4)

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # Convert date/time to ISO 8601 string format
    raise TypeError(f"Type {type(obj)} not serializable")

# Example usage: return JSON data
if __name__ == "__main__":
    result_json = extract_table_as_json()
    print(result_json)  # Return JSON data to the tool
