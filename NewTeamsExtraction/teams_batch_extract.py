import os
import json
import concurrent.futures
from extract_messages import extract_messages
from fetch_users import get_analyzable_users
import signal
import sys

def signal_handler(sig, frame):
    print("\nScript interrupted. Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Folder to save Teams JSON files
os.makedirs("teams_json", exist_ok=True)

def save_messages_to_json(user_upn):
    try:
        print(f"Fetching Teams messages for {user_upn}...")
        messages = extract_messages(user_upn)

        if not messages:
            print(f"No Teams messages found for {user_upn}.")
            return

        file_path = os.path.join("teams_json", f"teams_{user_upn.replace('@', '_at_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)

        print(f"Saved {len(messages)} messages for {user_upn} to {file_path}")

    except Exception as e:
        print(f"Error processing {user_upn}: {e}")

def main():
    users = get_analyzable_users()

    if not users:
        print("No analyzable users found.")
        return

    # Use threads to fetch in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(save_messages_to_json, users)

if __name__ == "__main__":
    main()