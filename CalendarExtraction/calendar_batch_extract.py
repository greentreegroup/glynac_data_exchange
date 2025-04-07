import os
import sys
import json
import signal
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from NewEmailExtraction.fetch_users import get_analyzable_users
from extract_calendars import get_calendar_events


def signal_handler(sig, frame):
    print("\nInterrupted. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

os.makedirs("calendar_json", exist_ok=True)

def save_calendar_json(user_upn):
    try:
        print(f"Fetching calendar events for {user_upn}")
        events = get_calendar_events(user_upn)


        file_path = os.path.join("calendar_json", f"calendar_{user_upn.replace('@', '_at_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(events if events else [], f, indent=2)

        print(f"Saved {len(events) if events else 0} events for {user_upn}")

    except Exception as e:
        print(f"Error processing {user_upn}: {e}")

        error_path = os.path.join("calendar_json", f"calendar_{user_upn.replace('@', '_at_')}_error.json")
        with open(error_path, "w", encoding="utf-8") as f:
            json.dump({"error": str(e)}, f, indent=2)

def main():
    users = get_analyzable_users()
    if not users:
        print("No users found.")
        return


    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(save_calendar_json, users)

if __name__ == "__main__":
    main()