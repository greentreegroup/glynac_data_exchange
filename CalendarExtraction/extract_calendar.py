import requests
from auth_token import get_access_token
import config

def check_calendars(user_email):
    """Fetches and prints the available calendars for a user."""
    print("Fetching calendars for user:", config.USER_UPN)
    access_token = get_access_token()
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/calendars"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    
    print("Calendars:", [calendar["name"] for calendar in response.json().get("value", [])])


def get_calendar_events(user_email):
    """Fetches calendar events for a specified user."""
    access_token = get_access_token()
    if not access_token:
        print("Failed to retrieve access token.")
        return

    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_email}/events"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)

    #print("Full API Response:", response.status_code, response.text) # Debugging

    if response.status_code == 200:
        events = response.json().get("value", [])
        return events
    else:
        print("Error fetching calendar events:", response.status_code, response.text)
        return None
