from extract_calendars import get_calendar_events, check_calendars
#from store_calendars import store_calendar_events
import config
from test import test

def main():
    """Extract and store calendar events."""
    user_upn = config.USER_UPN
    if not user_upn:
        print("Error: USER_UPN is not set.")
        return

    print(f"Fetching calendars for {user_upn}...")
    calendar_names = check_calendars(user_upn)

    if not calendar_names:
        print("No calendars found.")
        return

    print(f"Calendars found: {calendar_names}")

    for calendar_name in calendar_names:
        print(f"Fetching events from '{calendar_name}'...")
        events = get_calendar_events(user_upn) #test(config.USER_UPN) # Testing

        if events:
            for event in events:
                print(f"Event ID: {event['id']}")
                print(f"Organizer: {event['organizer']['emailAddress']['name']}")
                print(f"Title: {event['subject']}")
                print(f"Description: {event.get('bodyPreview', 'No description')}")
                print(f"Location: {event.get('location', {}).get('displayName', 'No location')}")
                attendees_dict = {
                    attendee["emailAddress"]["name"]: attendee["type"]
                    for attendee in event.get("attendees", [])
                }
                print(f"Attendees: {attendees_dict}")
                print(f"Meeting Type: {event.get('meetingMessageType', 'No meeting type')}") 
                print(f"Start: {event['start']['dateTime']}")
                print(f"End: {event['end']['dateTime']}")
                print(f"Date Extracted: {event['Date Extracted']}\n")
        else:
            print("No events found in default Calendar.")

        # Store the events in a database

if __name__ == "__main__":
    main()
