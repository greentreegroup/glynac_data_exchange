import os
import json
import requests
from auth_token import get_access_token
import config
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse
import re
from concurrent.futures import ThreadPoolExecutor
import time
import threading

EMAIL_JSON_FOLDER = "email_json"
NO_MORE_EMAILS_FILE = "no_more_emails.json"

def fetch_paginated_message_ids(user_upn, skip_pages=50):
    """Fetch all message metadata (IDs) for a user using pagination, with an option to skip initial pages."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/messages?$select=id&$top=10"

    all_ids = []
    page_count = 0
    max_pages = 51  # Increased safety cap
    skipped_count = 0  # Number of pages to skip

    while url and page_count < max_pages:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if skipped_count < skip_pages:
                print(f"Thread: {threading.current_thread().name} - Skipping page {page_count + 1} for {user_upn}...")
                url = data.get("@odata.nextLink")
                page_count += 1
                skipped_count += 1
                continue  # Skip processing this page's IDs

            message_batch = [msg['id'] for msg in data.get("value", [])]
            all_ids.extend(message_batch)

            page_count += 1
            current_thread = threading.current_thread()
            print(f"Thread: {current_thread.name} - Fetched {len(message_batch)} email IDs (Page {page_count}) for {user_upn}...")

            url = data.get("@odata.nextLink")

        except requests.exceptions.RequestException as e:
            current_thread = threading.current_thread()
            print(f"Thread: {current_thread.name} - Error fetching IDs for {user_upn} on page {page_count}: {e}")
            return all_ids

    if page_count >= max_pages and url:
        current_thread = threading.current_thread()
        print(f"Thread: {current_thread.name} - Warning: Reached maximum page limit ({max_pages}) while fetching IDs for {user_upn}. Some emails might have been skipped.")

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

def record_no_more_emails(user_upn):
    processed_users = set()
    if os.path.exists(NO_MORE_EMAILS_FILE):
        try:
            with open(NO_MORE_EMAILS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    processed_users.update(data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Will create a new file or overwrite if corrupted

    processed_users.add(user_upn)
    try:
        with open(NO_MORE_EMAILS_FILE, 'w') as f:
            json.dump(list(processed_users), f, indent=2)
        print(f"Thread: {threading.current_thread().name} - Recorded '{user_upn}' in '{NO_MORE_EMAILS_FILE}' as no emails were found.")
    except Exception as e:
        print(f"Thread: {threading.current_thread().name} - Error writing to '{NO_MORE_EMAILS_FILE}': {e}")

def is_user_in_no_more_emails(user_upn):
    if os.path.exists(NO_MORE_EMAILS_FILE):
        try:
            with open(NO_MORE_EMAILS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and user_upn in data:
                    print(f"Thread: {threading.current_thread().name} - Skipping user '{user_upn}' as they are in '{NO_MORE_EMAILS_FILE}'.")
                    return True
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # File might not exist or be corrupted, proceed as normal
    return False

def extract_emails(user_upn):
    if is_user_in_no_more_emails(user_upn):
        return []
    existing_message_ids = set()
    for filename in os.listdir(EMAIL_JSON_FOLDER):
        if filename.startswith(f"emails_{user_upn.replace('@', '_at_')}") and filename.endswith(".json"):
            filepath = os.path.join(EMAIL_JSON_FOLDER, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for email_data in data:
                        if 'email_id' in email_data:
                            existing_message_ids.add(email_data['email_id'])
            except Exception as e:
                print(f"Thread: {threading.current_thread().name} - Error reading existing JSON file {filename}: {e}")

    print(f"Thread: {threading.current_thread().name} - Found {len(existing_message_ids)} email IDs already in JSON files for user: {user_upn}.")

    all_message_ids_fetched = fetch_paginated_message_ids(user_upn)
    new_message_ids_to_process = [mid for mid in all_message_ids_fetched if mid not in existing_message_ids]

    print(f"Thread: {threading.current_thread().name} - Fetched {len(all_message_ids_fetched)} message IDs from API.")
    print(f"Thread: {threading.current_thread().name} - Found {len(new_message_ids_to_process)} new message IDs to process for {user_upn}.")
    if not all_message_ids_fetched:
        print(f"Thread: {threading.current_thread().name} - No message IDs fetched from API for user: {user_upn}.")
        record_no_more_emails(user_upn)
        return []

    processed_emails = []
    parent_thread = threading.current_thread()
    print(f"Thread: {parent_thread.name} - Starting processing of {len(new_message_ids_to_process)} new email IDs for user: {user_upn}.")
    total_count = len(new_message_ids_to_process)
    processed_count = 0
    processed_message_ids_in_run = set()

    def process_message(message_id):
        nonlocal processed_count
        if message_id in processed_message_ids_in_run:
            print(f"Thread: {threading.current_thread().name} - Skipping already processed message ID '{message_id}' for user: {user_upn} in this run.")
            return None

        processed_count += 1
        current_thread = threading.current_thread()
        print(f"Thread: {current_thread.name} - Processing new message ID {message_id} ({processed_count}/{total_count}) for user: {user_upn}")
        email = fetch_full_message(user_upn, message_id)
        if not email:
            print(f"Thread: {current_thread.name} - Could not fetch full message for new ID: {message_id} for user: {user_upn}")
            return None

        sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")
        to_recipients_list = [r["emailAddress"]["address"].lower() for r in email.get("toRecipients", []) if "emailAddress" in r]
        if user_upn.lower() not in to_recipients_list and sender.lower() != user_upn.lower():
            print(f"Thread: {current_thread.name} - Skipping new message ID: {message_id} for user: {user_upn} (not to or from user)")
            return None

        reply_to = ", ".join([r["emailAddress"]["address"] for r in email.get("replyTo", []) if "emailAddress" in r]) or sender
        subject = email.get("subject", "No Subject")
        in_reply_to = email.get("inReplyTo", "N/A")
        body = html_to_text(email.get("body", {}).get("content", "No Content"))

        def parse_timestamp(ts):
            if not ts: return "N/A"
            try:
                return parse(ts).isoformat()
            except Exception as e:
                print(f"Thread: {current_thread.name} - Error parsing timestamp '{ts}': {e}")
                return "Invalid Timestamp"

        print(f"Thread: {current_thread.name} - Extracted details for new message ID: {message_id} for user: {user_upn}")
        processed_message_ids_in_run.add(message_id)
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

    with ThreadPoolExecutor(max_workers=24) as executor:
        results = executor.map(process_message, new_message_ids_to_process)

    processed_emails = [email for email in results if email is not None]
    print(f"Thread: {parent_thread.name} - Finished processing {len(processed_emails)} new emails for user: {user_upn}.")
    return processed_emails