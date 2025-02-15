import msal
import config

def get_access_token():
    app = msal.ConfidentialClientApplication(
        client_id=config.OUTLOOK_CLIENT_ID,
        client_credential=config.OUTLOOK_CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{config.OUTLOOK_TENANT_ID}"
    )

    token_response = app.acquire_token_for_client(scopes=config.SCOPES)

    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        raise Exception(f"Could not get access token: {token_response}")

# Test authentication
if __name__ == "__main__":
    print("Fetching access token...")
    access_token = get_access_token()
    print("Access Token:", access_token[:50] + "...")