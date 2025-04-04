import requests
from auth_token import get_access_token
from config import GRAPH_API_ENDPOINT
from datetime import datetime
import re
from bs4 import BeautifulSoup

def fetch_paginated_results(url, headers):
    all_results = []
    while url:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Error fetching data ({response.status_code}): {response.text}")
            return []

        data = response.json()
        all_results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")

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

    print(f"Fetched {len(messages)} messages for channel: {channel_name}")

    filtered_messages = []
    for message in messages:
        # Ignore system-generated messages
        if message.get("messageType") in ["systemEventMessage", "unknownFutureValue"]:
            #print(f"Skipping system message (ID: {message.get('id')})") # Uncomment to see skipped messages
            continue

        # Ensure sender is a real user (not a bot or system process) #not sender or
        sender = message.get("from") or {}
        user_info = sender.get("user", {})

        sender_name = user_info.get("displayName", "Unknown").strip()

        if "user" not in sender: 
            #print(f"Skipping message from non-user (ID: {message.get('id')})")
            continue

        mentions = message.get("mentions", [])
        mentioned_users = [m.get("user", {}).get("displayName") for m in mentions if "user" in m]

        body = html_to_text(message.get("body", {}).get("content", "No Content"))

        filtered_messages.append({
            "platform": "Teams",
            "chat_id": message.get("id"),
            "chat_from": sender.get("user", {}).get("displayName", "Unknown"),
            "channel": channel_name,
            "message": body,
            "thread_id": message.get("replyToId"),
            "timestamp": message.get("createdDateTime"),
            "mentioned_users": ", ".join(mentioned_users) if mentioned_users else None,
            "date_extracted": datetime.utcnow().isoformat()
        }) # TODO: Add more fields if needed

    return filtered_messages

def extract_messages(user_upn):
    final_messages = []

    try:
        teams = extract_teams(user_upn)
        if not teams:
            print(f"No Teams found for {user_upn}")
            return []

        for team in teams:
            team_id = team.get("id")
            team_name = team.get("displayName", "Unnamed Team")
            channels = extract_channels(team_id)

            for channel in channels:
                channel_id = channel.get("id")
                channel_name = channel.get("displayName", "Unnamed Channel")

                messages = extract_channel_messages(team_id, channel_id, f"{team_name} / {channel_name}")
                final_messages.extend(messages)

    except Exception as e:
        print(f"Error extracting messages for {user_upn}: {e}")

    return final_messages