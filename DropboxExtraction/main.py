from extract_dropbox import get_activity_log
from store_dropbox import insert_team_events
import json

def main():
    events = get_activity_log()

    if not events:
        print("No team events found.")
        return

    output_file = "exported_dropbox_team_events.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
        print(f"Exported {len(events)} events to {output_file}")
    except Exception as e:
        print(f"Failed to write to JSON file: {e}")
    
    # insert_team_events(events)

if __name__ == "__main__":
    main()