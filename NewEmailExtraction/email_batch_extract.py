import os
import json
import concurrent.futures
from extract_emails import extract_emails
from fetch_users import get_analyzable_users
import signal
import sys
import threading

def signal_handler(sig, frame):
    print(f"\nThread: {threading.current_thread().name} - Script interrupted.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Folder to save JSON files
os.makedirs("email_json", exist_ok=True)

# File to store processed user IDs
PROCESSED_USERS_FILE = "processed_users.json"

def load_processed_users():
    try:
        with open(PROCESSED_USERS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        print(f"Thread: MainThread - Warning: Could not decode {PROCESSED_USERS_FILE}. Starting with an empty set.")
        return set()

def save_processed_users(processed_users):
    print(f"Thread: MainThread - Saving processed users...")
    with open(PROCESSED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_users), f, indent=2)
    print(f"Thread: MainThread - Processed users saved.")

def save_emails_to_json(user_upn, processed_users_set):
    current_thread_name = threading.current_thread().name
    if user_upn in processed_users_set:
        print(f"Thread: {current_thread_name} - Skipping {user_upn} (already processed).")
        return

    try:
        print(f"Thread: {current_thread_name} - Starting processing for user: {user_upn}")
        emails = extract_emails(user_upn)

        if not emails:
            print(f"Thread: {current_thread_name} - No emails found for user: {user_upn}.")
            processed_users_set.add(user_upn)
            save_processed_users(processed_users_set)
            return

        file_path = os.path.join("email_json", f"emails_{user_upn.replace('@', '_at_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2)

        print(f"Thread: {current_thread_name} - Saved {len(emails)} emails for user: {user_upn} to {file_path}")
        processed_users_set.add(user_upn)
        save_processed_users(processed_users_set)

    except Exception as e:
        print(f"Thread: {current_thread_name} - Error processing user: {user_upn} - {e}")
        processed_users_set.add(user_upn)
        save_processed_users(processed_users_set)
    finally:
        print(f"Thread: {current_thread_name} - Finished processing user: {user_upn}")

def main():
    users = get_analyzable_users()
    main_thread_name = threading.current_thread().name
    print(f"Thread: {main_thread_name} - Found {len(users)} users to analyze: {users}")

    if not users:
        print(f"Thread: {main_thread_name} - No analyzable users found.")
        return

    processed_users_set = load_processed_users()
    print(f"Thread: {main_thread_name} - Previously processed users: {processed_users_set}")

    users_to_process = [user for user in users if user not in processed_users_set]
    print(f"Thread: {main_thread_name} - Users to process in this run: {users_to_process}")

    if not users_to_process:
        print(f"Thread: {main_thread_name} - No new users to process.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # Pass the processed_users set to the save_emails_to_json function
        futures = [executor.submit(save_emails_to_json, user, processed_users_set) for user in users_to_process]
        concurrent.futures.wait(futures)

    print(f"Thread: {main_thread_name} - Finished processing all initial users.")
    print(f"Thread: {main_thread_name} - Final processed users list should be in {PROCESSED_USERS_FILE}")

if __name__ == "__main__":
    main()