import requests
from auth_token import get_access_token
from config import GRAPH_API_ENDPOINT
from datetime import datetime
from test import mock_teams_messages
import re
from bs4 import BeautifulSoup

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

def html_to_text(html_content):
    """Convert HTML content to plain text."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # <br> and <p> tags
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all("p"):
        p.insert_before("\n")
    
    # List items
    for li in soup.find_all("li"):
        li.insert_before("\n- ")
        li.insert_after("\n")  # Adds new line

    # Convert blockquote messages (e.g., replies in Teams)
    for blockquote in soup.find_all("blockquote"):
        blockquote.insert_before("\n> ")  # Adds quote formatting
        blockquote.insert_after("\n")

    # Handle links: Keep text + URL in brackets
    for a in soup.find_all("a", href=True):
        a.replace_with(f"{a.get_text()} ({a['href']})")

    # Handle code snippets
    for code in soup.find_all("pre"):
        code.insert_before("\n```\n")  # Markdown-style block
        code.insert_after("\n```\n")

    text = soup.get_text(separator=" ")

    # Clean up excessive newlines and whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

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
        sender = message.get("from") or {}
        if not sender or "user" not in sender:
            #print(f"Skipping message from non-user (ID: {message.get('id')})")
            continue

        body = html_to_text(message.get("body", {}).get("content", "No Content"))

        filtered_messages.append({
            "Chat ID": message.get("id"),
            "From": sender.get("user", {}).get("displayName", "Unknown User"),
            "Channel": channel_name,
            "Message": body,
            "Thread ID": message.get("replyToId"),
            "Timestamp": message.get("createdDateTime"),
            "Date Extracted": datetime.utcnow().isoformat()
        })

    return filtered_messages