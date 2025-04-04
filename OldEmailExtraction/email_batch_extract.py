import os
import json
import concurrent.futures
from extract_emails import extract_emails
from fetch_users import get_analyzable_users
import signal
import sys

def signal_handler(sig, frame):
    print("\nScript interrupted. Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

COMPLETED_USERS_FILE = "completed_users.txt"

def load_completed_users():
    if not os.path.exists(COMPLETED_USERS_FILE):
        return set()
    with open(COMPLETED_USERS_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_completed_user(user_upn):
    with open(COMPLETED_USERS_FILE, "a") as f:
        f.write(f"{user_upn}\n")


# Folder to save JSON files
os.makedirs("email_json", exist_ok=True)

def save_emails_to_json(user_upn):
    if user_upn in completed_users:
        print(f"Skipping {user_upn} (already completed)")
        return
    try:
        print(f"Fetching emails for {user_upn}...")
        emails = extract_emails(user_upn)

        if not emails:
            print(f"No emails found for {user_upn}.")
            save_completed_user(user_upn)
            return

        file_path = os.path.join("email_json", f"emails_{user_upn.replace('@', '_at_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2)

        print(f"Saved {len(emails)} emails for {user_upn} to {file_path}")
        save_completed_user(user_upn)

    except Exception as e:
        print(f"Error processing {user_upn}: {e}")

def main():
    global completed_users
    users = get_analyzable_users()

    if not users:
        print("No analyzable users found.")
        return

    completed_users = load_completed_users()
    print(f"Skipping {len(completed_users)} users already processed...")

    # Use ThreadPoolExecutor to process users in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(save_emails_to_json, users)

if __name__ == "__main__":
    main()