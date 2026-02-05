import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

TOKEN_URL = "https://api.francetravail.io/connexion/oauth2/access_token"

def test_auth():
    print("CLIENT_ID loaded :", bool(CLIENT_ID))
    print("CLIENT_SECRET loaded :", bool(CLIENT_SECRET))

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "api_offresdemploiv2 o2dsoffre"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    print("Status code:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    test_auth()
