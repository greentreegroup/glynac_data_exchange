import requests
from auth_token import get_access_token
import config
#from fetch_id import get_user_id

# Fetch user ID for authentication
#user_id = get_user_id(config.USER_UPN)

# Get access token
ACCESS_TOKEN = get_access_token()
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_all_pages(url):
    """Fetch all pages of data from a paginated API endpoint."""
    items = []
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            items.extend(data.get("value", []))
            url = data.get("@odata.nextLink")  # Get the next page URL
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break
    return items

def extract_teams(user_upn):
    """Extract all teams the user is part of."""
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/joinedTeams"
    return fetch_all_pages(url)

def extract_channels(team_id):
    """Extract channels in a specific team."""
    url = f"{config.GRAPH_API_ENDPOINT}/teams/{team_id}/channels"
    return fetch_all_pages(url)

def extract_channel_messages(team_id, channel_id):
    """Extract messages from a specific channel."""
    url = f"{config.GRAPH_API_ENDPOINT}/teams/{team_id}/channels/{channel_id}/messages"
    return fetch_all_pages(url)
    