import requests
from auth_token import get_access_token
import config
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse
import re
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_paginated_message_ids(user_upn):
    """Fetch only message metadata (IDs) for a user."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/messages?$select=id&$top=100"

    all_ids = []
    page_count = 0
    max_pages = 5  # Safety cap: fetch at most 5 pages (5 x 30 = 150 emails)

    while url and page_count < max_pages:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            message_batch = [msg['id'] for msg in data.get("value", [])]
            all_ids.extend(message_batch)

            page_count += 1
            # print(f"Fetched {len(message_batch)} emails (Page {page_count}) for {user_upn}...")

            url = data.get("@odata.nextLink")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching IDs for {user_upn}: {e}")
            return []

    return all_ids

def fetch_full_message(user_upn, message_id):
    """Fetch full message details for a single message, with retry on 429."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/messages/{message_id}"

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"429 rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching full message {message_id} for {user_upn}: {e}")
            time.sleep(2)
            continue

    return None


def html_to_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for tag in soup.find_all(True):
        tag.attrs = {}
    text = soup.get_text(separator="\n")
    return re.sub(r'\n+', '\n', text).strip()

def extract_emails(user_upn):
    message_ids = fetch_paginated_message_ids(user_upn)
    processed_emails = []

    def process_message(message_id):
        email = fetch_full_message(user_upn, message_id)
        if not email:
            return None

        sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")
        to_recipients_list = [r["emailAddress"]["address"].lower() for r in email.get("toRecipients", []) if "emailAddress" in r]
        if user_upn.lower() not in to_recipients_list and sender.lower() != user_upn.lower():
            return None

        reply_to = ", ".join([r["emailAddress"]["address"] for r in email.get("replyTo", []) if "emailAddress" in r]) or sender
        subject = email.get("subject", "No Subject")
        in_reply_to = email.get("inReplyTo", "N/A")
        body = html_to_text(email.get("body", {}).get("content", "No Content"))

        def parse_timestamp(ts):
            if not ts: return "N/A"
            try: return parse(ts).isoformat()
            except: return "Invalid Timestamp"

        return {
            "email_id": message_id,
            "conversation_id": email.get("conversationId", "N/A"),
            "from": sender,
            "to": ", ".join(to_recipients_list) or "N/A",
            "reply_to": reply_to,
            "in_reply_to": in_reply_to,
            "subject": subject,
            "body": body,
            "received_at": parse_timestamp(email.get("receivedDateTime")),
            "sent_at": parse_timestamp(email.get("sentDateTime")),
            "date_extracted": datetime.utcnow().isoformat()
        }

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(process_message, message_ids)

    processed_emails = [email for email in results if email is not None]
    return processed_emails