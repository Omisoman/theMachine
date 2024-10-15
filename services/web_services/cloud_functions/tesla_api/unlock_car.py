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

# Function to honk the Tesla's horn
def unlock_car(request):
    try:
        tessie_token = access_secret_version('TESSIE_TOKEN')
        tesla_vin = access_secret_version('TESLA_VIN')

        url = f"{TESSIE_API_BASE_URL}/{tesla_vin}/command/unlock?retry_duration=40&wait_for_completion=true"

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {tessie_token}"
        }

        response = requests.post(url, headers=headers)
        response.raise_for_status()

        return response.text
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Internal server error: {err}"





