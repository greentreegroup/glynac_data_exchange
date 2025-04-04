import requests
import config
def get_access_token():
    url = f"https://login.microsoftonline.com/{config.TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": config.OUTLOOK_CLIENT_ID,
        "client_secret": config.OUTLOOK_CLIENT_SECRET,
        "scope": config.SCOPES
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json().get("access_token")

if __name__ == "__main__":
    print("Fetching access token...")
    try:
        access_token = get_access_token()
        print("Access Token:", access_token[:50] + "...")
    except requests.exceptions.RequestException as e:
        print("Error fetching access token:", e)