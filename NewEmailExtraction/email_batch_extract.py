import os
import json
import concurrent.futures
from extract_emails import extract_emails
from fetch_users import get_analyzable_users
import signal
import sys
import threading

signal.signal(signal.SIGINT, lambda sig, frame: (print("\nInterrupted."), sys.exit(0)))

EMAIL_JSON_FOLDER = "email_json"
FOLDERS = ["Inbox", "SentItems"]

# Folder to save JSON files
os.makedirs(EMAIL_JSON_FOLDER, exist_ok=True)

def save_emails_to_json(user_upn, folder_name):
    current_thread_name = threading.current_thread().name
    print(f"Thread: {current_thread_name} - Extracting from {folder_name} for user: {user_upn}")

    try:
        new_emails = extract_emails(user_upn, folder_name=folder_name)

        if not new_emails:
            print(f"Thread: {current_thread_name} - No new emails found for {user_upn} [{folder_name}].")
            return

        file_path = os.path.join(
            EMAIL_JSON_FOLDER,
            f"{folder_name.lower()}_emails_{user_upn.replace('@', '_at_')}.json"
        )

        existing_emails = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    existing_emails = json.load(f)
                except json.JSONDecodeError:
                    print(f"Thread: {current_thread_name} - Corrupted JSON for {user_upn} [{folder_name}]. Starting fresh.")

        updated_emails = existing_emails + new_emails

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(updated_emails, f, indent=2)

        print(f"Thread: {current_thread_name} - Saved {len(new_emails)} emails to {file_path} (Total: {len(updated_emails)})")

    except Exception as e:
        print(f"Thread: {current_thread_name} - Error processing {user_upn} [{folder_name}]: {e}")

def main():
    users = get_analyzable_users()
    print(f"Thread: MainThread - Found {len(users)} users to analyze.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for user in users:
            for folder in FOLDERS:
                executor.submit(save_emails_to_json, user, folder)

    print("Thread: MainThread - Finished processing all users.")

if __name__ == "__main__":
    main()
