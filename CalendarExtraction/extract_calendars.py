import requests
from auth_token import get_access_token
import config
from datetime import datetime

def fetch_paginated_results(url, headers):
    """Handles paginated API requests."""
    all_results = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching data ({response.status_code}): {response.text}")
            return []

        data = response.json()
        all_results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # Get next page if available

    return all_results

def check_calendars(user_upn):
    """Fetches and returns available calendars for a user."""
    access_token = get_access_token()
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/calendars"
    headers = {"Authorization": f"Bearer {access_token}"}

    calendars = fetch_paginated_results(url, headers)
    # Exclude system-generated calendars (holidays, birthdays, etc.)
    excluded_calendars = {"United States holidays", "Birthdays", "Holidays"}
    filtered_calendars = [calendar["name"] for calendar in calendars if calendar["name"] not in excluded_calendars]

    return filtered_calendars

def get_calendar_events(user_upn, calendar_name="Calendar"):
    """Fetches events from a user's specified calendar."""
    access_token = get_access_token()
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/calendars/{calendar_name}/events"
    headers = {"Authorization": f"Bearer {access_token}"}

    events = fetch_paginated_results(url, headers)

    return [
        {
            "Event ID": event["id"],
            "Organizer": event["organizer"]["emailAddress"]["name"],
            "Title": event["subject"],
            "Description": event.get("bodyPreview", "No description"),
            "Location": event.get("location", {}).get("displayName", "No location"),
            "Attendees": {attendee["emailAddress"]["name"]: attendee["type"]
                          for attendee in event.get("attendees", [])},
            "Meeting Type": event.get("meetingMessageType", "No meeting type"),
            "Start": event["start"]["dateTime"],
            "End": event["end"]["dateTime"],
            #"Date Extracted": datetime.now().isoformat()
        }
        for event in events
    ]
