import requests
from auth_token import get_access_token
import config
from datetime import datetime
from bs4 import BeautifulSoup
import re

def fetch_paginated_results(url, headers):
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

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")

    text = re.sub(r"[_]{5,}", "", text)  # Remove lines with 5 or more underscores
    text = re.sub(r"\n\s*\n", "\n", text)  # Remove empty lines
    text = re.sub(r"\s{2,}", " ", text.strip())  # Replace multiple spaces

    return text.strip()
        
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
    """Fetches events from a user's calendar."""
    access_token = get_access_token()
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/calendars/{calendar_name}/events" #?$top=10"
    headers = {"Authorization": f"Bearer {access_token}"}

    events = fetch_paginated_results(url, headers)

    extracted_events = []
    for event in events:

        location = event.get("location", {}).get("displayName", "").strip()
        description = html_to_text(event.get("bodyPreview", "No description"))
        virtual = event.get("isOnlineMeeting", False)

        # Fix Virtual Meetings with Meeting Links
        meeting_links = ["zoom.us", "google.com", "meet.google", "teams.microsoft", "interview-links.indeed", "employers.indeed.com", "virtual-interviews/upcoming"]
        if any(link in location.lower() for link in meeting_links) or any(link in description.lower() for link in meeting_links):
            virtual = True
        if not location or location.lower() == "virtual meeting (link in description)":
            location = "Virtual Meeting (link in Description)"


        attendees = {attendee["emailAddress"]["name"]: attendee["type"] for attendee in event.get("attendees", [])}
        if not attendees:
            attendees = {event["organizer"]["emailAddress"]["name"]: "Organizer"}

        extracted_events.append({
            "Event ID": event["id"],
            "Tenant ID": config.TENANT_ID,
            "Organizer": event["organizer"]["emailAddress"]["name"],
            "Title": event.get("subject") or "No title",
            "Description": description,
            "Location": location,
            "Attendees": attendees,
            "Virtual": virtual,
            "Start": event["start"]["dateTime"],
            "End": event["end"]["dateTime"],
            "Date Extracted": datetime.utcnow().isoformat()
        })

    return extracted_events
