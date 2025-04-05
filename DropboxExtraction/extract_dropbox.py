import requests
from auth_dropbox import get_access_token
import uuid

DROPBOX_LOG_EVENTS_URL = "https://api.dropboxapi.com/2/team_log/get_events"
DROPBOX_LOG_EVENTS_CONTINUE_URL = "https://api.dropboxapi.com/2/team_log/get_events/continue"

RELEVANT_EVENT_TYPES = {
    "file_add", "file_delete", "file_edit", "file_rename",
    "folder_add", "folder_delete", "folder_rename"
}

def get_activity_log():
    """Fetch and return Dropbox team file/folder activity events."""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    team_activity = []
    body = {}

    while True:
        url = DROPBOX_LOG_EVENTS_URL if "cursor" not in body else DROPBOX_LOG_EVENTS_CONTINUE_URL
        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            print(f"Error: {response.status_code} — {response.text}")
            break

        data = response.json()
        events = data.get("events", [])
        cursor = data.get("cursor")
        has_more = data.get("has_more", False)

        for event in events:
            try:
                event_type = event.get("event_type", {}).get(".tag")
                if event_type not in RELEVANT_EVENT_TYPES:
                    continue

                asset = next((a for a in event.get("assets", []) if a.get(".tag") in {"file", "folder"}), {})
                actor = event.get("actor", {}).get("admin") or event.get("actor", {}).get("user") or {}

                team_activity.append({
                    "event_id": str(uuid.uuid4()),
                    "timestamp": event.get("timestamp"),
                    "event_type": event_type,
                    "asset_type": asset.get(".tag"),
                    "name": asset.get("display_name"),
                    "path": asset.get("path", {}).get("contextual"),
                    "actor_name": actor.get("display_name"),
                    "actor_email": actor.get("email")
                })
            except Exception as e:
                print(f"Skipping malformed event: {e}")

        if has_more and cursor:
            body = {"cursor": cursor}
        else:
            break

    print(f"Fetched {len(team_activity)} relevant Dropbox team activity events.")
    return team_activity

if __name__ == "__main__":
    get_activity_log()