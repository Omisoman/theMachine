import requests
import os
from google.cloud import secretmanager

# Tessie API Base URL
TESSIE_API_BASE_URL = "https://api.tessie.com"

# Initialize the Secret Manager client
secret_client = secretmanager.SecretManagerServiceClient()

# Helper function to access secrets from Google Secret Manager
def access_secret_version(secret_id):
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode("UTF-8")

# Function to wake up the Tesla vehicle using Tessie API
def wake_up_tesla(request):
    try:
        # Retrieve the Tessie token and Tesla VIN from Secret Manager
        tessie_token = access_secret_version('TESSIE_TOKEN')
        tesla_vin = access_secret_version('TESLA_VIN')

        # Construct the URL for waking up the Tesla vehicle
        url = f"{TESSIE_API_BASE_URL}/{tesla_vin}/wake"

        # Set up the headers, including the Authorization header with the Bearer token
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {tessie_token}"
        }

        # Send the request to Tessie API to wake up the vehicle
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raise an error if the request failed

        return response.text  # Return the response text
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Internal server error: {err}"
