from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# API URLs
AUTH_URL = "https://login.ssen.co.uk/85cc94c1-367c-4fe5-a9f8-511bc5a4721e/B2C_1A_SIGNUP_SIGNIN/oauth2/v2.0/token"
STATIC_DATA_URL = "https://nerda-prod-apis-v2.azurewebsites.net/api/ApiNerdaStatic"
HISTORICAL_DATA_URL = "https://nerda-prod-apis-v2.azurewebsites.net/api/ApiNerdaAfter?measurement="

# Store token and refresh token globally
ACCESS_TOKEN = ""
REFRESH_TOKEN = "eyJraWQiOiJZWjRteWlycy1hVjRKREF4NmhUc1A2b3hKWl96LXEyTnZ6ZnVXMTB1NTk4IiwidmVyIjoiMS4wIiwiemlwIjoiRGVmbGF0ZSIsInNlciI6IjEuMCJ9.D5KPymYj7a1CQ-VxOjykB3pli35SEJhIQ0Im-n6uYkYj4LpaYQj4SuFIC_jC-10u4k-ovivjpOqMUhPn4uCg5blmhFxYAl4H5-r0eTGPkKgGa6rI3VdiPXglEGft0EB2lLnAG0yaw4PgIFrVIObmjDWYUMay-R21Pud8qI1hOnHndexAkH-ugTkk32DvR8tpv664Jq684eImO3IMj9B05K2BpvThQcNuPfXkoQRyuRh0eRaiyxdQbi2VKfaajFfELH0x35aWPWc0F_ipaUwfEnz1t8T-B6XYf5hBCHLUN69SWBJiOu4hUhyY9UQQ7kT2YyGJNCNQyjQAyZkesG9GvA.Nc8YmUFRVYqhYcK_.iI6kDMIyJ7L21eSZZB8AyQMuK6pM82l4ySgRMJBgNjTpc_-rYT2zKGSqHKdk-YNf5nwZDp3rvBbvaBtP3uwkh6pjZeI3Lgr3rVtxEkNC7Eg7pF0_R6W0n7CsFoc6M0BTaeSeEgSTruoG_wMyO193Npy9ZFtjEILZOPKG-SUlZms_hVBK4BCuon-n8GGJSH05PgZofz60R-VvbueAfRJ79cKhzgl3G04baqOrQwwxjMz1t8BHXyH3-93-zwQ-RrxLmakKsBicm1Y1mFpDxgCn6rsABh4bOh5VlUvdXLgdyGWoc2s3Ku_GwVOcxRuTLqhz2eztbyx8Uk9OVTqlIPIVBm0KinZMb6o1RorVyUY5kdr6lEA2XJWRILClZSvXX8JAOQvYAYkYC_sIy4Ic_dLOrcK01iUiqyx_brBwbdUjNLeIOrwfjepXAEnUj-8wf0EOkafiQS9jdgRxjYHaOoxRZTsij0TsE9hFCMus2IST0YcOeKF4HEw3G2ZlE3U_Mc1Lqa8G0EHmdQ8mlxqAuyvm_7hEuO3C7imoZui1I7rfcr2iv5c4JVFwRlCcx86L3TSAFaJPQ6m7Jt-EE4XSgzgqIr2aAIuNr6crPzx18MPAJuCgV1lucEbJ5E9Lo56tFQgM-BxMx2honPvZtW9Wjqq5oA4rQ-WS2DZt7Oh4FQGgAsG2LYbDgyN_Y7dAfyBImcdwWk0nk5H1sR16uGErmnLond74m3vAiIaiiWgdYyY75EN4QRw2y5QMqbA4qX2dkPxSQFGLaZNzHFRO59TQLeApcw3FlXT-CDbJtxtQrRq468gT-1dVV18CVAm42NKdXvD7N5NggFFGH50iTFZvm_BGCeIa.76BxrGPiSxSjjgNfZipKNw"  # Replace with your stored refresh token

# Function to get a new access token using the refresh token
def refresh_access_token():
    global ACCESS_TOKEN
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": "b2e78631-df56-47a8-83ca-d88b2a29beff",
        "grant_type": "refresh_token",
        "scope": "openid offline_access https://networksdistb2cloginprd.onmicrosoft.com/b2e78631-df56-47a8-83ca-d88b2a29beff/nerda.read",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(AUTH_URL, data=data, headers=headers)
    
    if response.status_code == 200:
        # Parse the new access token
        data = response.json()
        ACCESS_TOKEN = data.get("access_token", "")
        return ACCESS_TOKEN
    else:
        return None  # In case of error

# Fetch historical data for a specific line
@app.route("/api/historical", methods=["GET"])
def get_historical():
    # Get line_id from query parameters
    line_id = request.args.get("line")
    
    # Calculate the date 365 days in the past
    today = datetime.utcnow()  # Current time in UTC
    past_date = today - timedelta(days=365)  # Subtract 365 days
    past_date_str = past_date.strftime("%Y-%m-%dT00:00:00.000Z")  # Format date for the API with time as 00:00:00

    # If the access token is expired, refresh it
    if not ACCESS_TOKEN:
        ACCESS_TOKEN = refresh_access_token()  # Refresh the token

    # Construct the full API URL with the line_id and the 'after' parameter (365 days ago)
    historical_url = f"{HISTORICAL_DATA_URL}{line_id}&after={past_date_str}"
    
    # Include the Authorization header with the access token
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # Make the API request
    response = requests.get(historical_url, headers=headers)
    
    # Return the response data to the client
    return jsonify(response.json())

if __name__ == "__main__":
    # Optionally, refresh the access token at startup
    ACCESS_TOKEN = refresh_access_token()  # Fetch token at startup
    app.run(host="0.0.0.0", port=5000)
