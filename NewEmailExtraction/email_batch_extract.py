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

# Folder to save JSON files
os.makedirs("email_json", exist_ok=True)

def save_emails_to_json(user_upn):
    try:
        print(f"Fetching emails for {user_upn}...")
        emails = extract_emails(user_upn)

        if not emails:
            print(f"No emails found for {user_upn}.")
            return

        file_path = os.path.join("email_json", f"emails_{user_upn.replace('@', '_at_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2)

        print(f"Saved {len(emails)} emails for {user_upn} to {file_path}")

    except Exception as e:
        print(f"Error processing {user_upn}: {e}")

def main():
    users = get_analyzable_users()

    if not users:
        print("No analyzable users found.")
        return

    # Use ThreadPoolExecutor to process users in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(save_emails_to_json, users)

if __name__ == "__main__":
    main()