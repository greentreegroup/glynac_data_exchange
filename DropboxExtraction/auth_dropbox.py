import config

def get_access_token():
    """Get Dropbox access token from config."""
    if config.DROPBOX_ACCESS_TOKEN:
        return config.DROPBOX_ACCESS_TOKEN
    raise Exception("DROPBOX_ACCESS_TOKEN is missing in config.py")

if __name__ == "__main__":
    try:
        token = get_access_token()
        print(f"Access token successfully retrieved: {token[:10]}...")
    except Exception as e:
        print(f"Error: {e}")
