import requests
import json
import os

# Define the API URL for sample user data
API_URL = "https://jsonplaceholder.typicode.com/users"

# Define the output path for the raw data
# We construct a path to the project's root, then into data/raw/
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "api_users_data.json")

def fetch_data_from_api():
    """
    Fetches user data from the API and saves it to a JSON file.
    """
    print(f"Fetching data from {API_URL}...")
    try:
        # Make a GET request to the API
        response = requests.get(API_URL, timeout=15)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Parse the JSON data from the response
        data = response.json()

        # Ensure the output directory exists before saving
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Write the data to a JSON file with pretty printing
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ API data saved successfully to: {OUTPUT_FILE}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return False

if __name__ == "__main__":
    fetch_data_from_api()