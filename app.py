from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get configuration from environment variables
PROJECT_ID = os.getenv('DEVCYCLE_PROJECT_ID')
FEATURE_ID = os.getenv('DEVCYCLE_FEATURE_ID')
CLIENT_ID = os.getenv('DEVCYCLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('DEVCYCLE_CLIENT_SECRET')
TOKEN_URL = os.getenv('DEVCYCLE_TOKEN_URL', 'https://auth.devcycle.com/oauth/token')
BASE_API_URL = os.getenv('DEVCYCLE_BASE_API_URL', 'https://api.devcycle.com/v1')

def get_access_token():
    """Fetch an access token using client credentials."""
    print("Fetching access token...")
    payload = {
        "grant_type": "client_credentials",
        "audience": "https://api.devcycle.com/",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

@app.route("/get-variations", methods=["GET"])
def get_variations():
    """Retrieve all variations for the configured feature."""
    if not all([PROJECT_ID, FEATURE_ID, CLIENT_ID, CLIENT_SECRET]):
        return jsonify({
            "error": "Missing required environment variables. Please check your .env file."
        }), 500
        
    try:
        token = get_access_token()
        url = f"{BASE_API_URL}/projects/{PROJECT_ID}/features/{FEATURE_ID}/variations"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        feature_data = response.json()
        return jsonify({
            "message": "Variations retrieved successfully", 
            "variations": feature_data
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"API request failed: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5125))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, port=port)