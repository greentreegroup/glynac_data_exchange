import os
import json
import concurrent.futures
from extract_emails import extract_emails
from fetch_users import get_analyzable_users
import signal
import sys

signal.signal(signal.SIGINT, lambda sig, frame: (print("\nInterrupted. Exiting..."), sys.exit(0)))

os.makedirs("email_json", exist_ok=True)

FOLDERS = ["Inbox", "SentItems"]

def save_emails_to_json(user_upn):
    for folder_name in FOLDERS:
        filename = f"{folder_name.lower()}_emails_{user_upn.replace('@', '_at_')}.json"
        filepath = os.path.join("email_json", filename)
        if os.path.exists(filepath):
            print(f"[{folder_name}] Skipping {user_upn} (already done)")
            continue

        try:
            print(f"[{folder_name}] Fetching emails for {user_upn}...")
            emails = extract_emails(user_upn, folder_name)

            if not emails:
                print(f"[{folder_name}] No emails found for {user_upn}.")
                continue

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(emails, f, indent=2)

            print(f"[{folder_name}] Saved {len(emails)} emails for {user_upn}")

        except Exception as e:
            print(f"[{folder_name}] Error processing {user_upn}: {e}")

def main():
    users = get_analyzable_users()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor: # Adjust max_workers as needed
        executor.map(save_emails_to_json, users)

if __name__ == "__main__":
    main()