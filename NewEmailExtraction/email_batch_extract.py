import os
import json
import concurrent.futures
import threading
import signal
import sys
from extract_emails import extract_emails
from fetch_users import get_analyzable_users

# Create directory if not exists
os.makedirs("email_json", exist_ok=True)

# Track processed users per folder
PROCESSED_USERS_FILE = "processed_users.json"
FOLDERS = ["Inbox", "SentItems"]

# Gracefully handle Ctrl+C
def signal_handler(sig, frame):
    print(f"\nThread: {threading.current_thread().name} - Script interrupted.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Load processed state
def load_processed_users():
    try:
        with open(PROCESSED_USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save processed state
def save_processed_users(processed_users):
    with open(PROCESSED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_users, f, indent=2)

# Save emails to JSON for all folders for one user
def save_emails_to_json(user_upn):
    thread_name = threading.current_thread().name
    processed = load_processed_users()
    user_record = processed.get(user_upn, [])

    for folder_name in FOLDERS:
        if folder_name in user_record:
            print(f"Thread: {thread_name} - [{folder_name}] Skipping {user_upn} (already processed)")
            continue

        print(f"Thread: {thread_name} - [{folder_name}] Fetching emails for {user_upn}...")
        try:
            emails = extract_emails(user_upn, folder_name)

            if not emails:
                print(f"Thread: {thread_name} - [{folder_name}] No emails found for {user_upn}.")
            else:
                filename = f"{folder_name.lower()}_emails_{user_upn.replace('@', '_at_')}.json"
                filepath = os.path.join("email_json", filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(emails, f, indent=2)
                print(f"Thread: {thread_name} - [{folder_name}] Saved {len(emails)} emails for {user_upn}")

            # Update processed status
            user_record.append(folder_name)
            processed[user_upn] = list(set(user_record))  # ensure uniqueness
            save_processed_users(processed)

        except Exception as e:
            print(f"Thread: {thread_name} - [{folder_name}] Error processing {user_upn}: {e}")

def main():
    users = get_analyzable_users()
    print(f"MainThread - Found {len(users)} users to process.")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(save_emails_to_json, users)

if __name__ == "__main__":
    main()
