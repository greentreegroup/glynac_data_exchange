import requests
from auth_token import get_access_token
from config import GRAPH_API_ENDPOINT
from datetime import datetime
from test import mock_teams_messages

def fetch_paginated_results(url, headers):
    all_results = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching data ({response.status_code}): {response.text}")
            return []

        data = response.json()
        all_results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # Get next page if available

    return all_results

def extract_teams(user_upn):
    """Extract all teams the user is part of."""
    access_token = get_access_token()
    url = f"{GRAPH_API_ENDPOINT}/users/{user_upn}/joinedTeams"
    headers = {"Authorization": f"Bearer {access_token}"}

    return fetch_paginated_results(url, headers)

def extract_channels(team_id):
    """Extract channels in a specific team."""
    access_token = get_access_token()
    url = f"{GRAPH_API_ENDPOINT}/teams/{team_id}/channels"
    headers = {"Authorization": f"Bearer {access_token}"}

    return fetch_paginated_results(url, headers)

def extract_channel_messages(team_id, channel_id, channel_name):
    """Extract messages from a specific channel."""
    access_token = get_access_token()
    url = f"{GRAPH_API_ENDPOINT}/teams/{team_id}/channels/{channel_id}/messages" #?$top=100"
    headers = {"Authorization": f"Bearer {access_token}"}

    messages = fetch_paginated_results(url, headers)
    #messages = mock_teams_messages()  # Use this for testing

    print(f"Total Messages Fetched: {len(messages)}")

    filtered_messages = []
    for message in messages:
        # Ignore system-generated messages
        if message.get("messageType") in ["systemEventMessage", "unknownFutureValue"]:
            #print(f"Skipping system message (ID: {message.get('id')})") # Uncomment to see skipped messages
            continue

        # Ensure sender is a real user (not a bot or system process)
        sender = message.get("from", {})
        if not sender or "user" not in sender:
            #print(f"Skipping message from non-user (ID: {message.get('id')})")
            continue

        filtered_messages.append({
            "Chat ID": message.get("id"),
            "From": sender["user"].get("displayName", "Unknown User"),
            "Channel": channel_name,
            "Message": message.get("body", {}).get("content", "").strip(),
            "Thread ID": message.get("replyToId"),
            "Timestamp": message.get("createdDateTime"),
            "Date Extracted": datetime.utcnow().isoformat()
        })

    return filtered_messages