from extract_calendars import get_calendar_events, check_calendars
from store_calendar import store_calendar_event, connect_db
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

    conn = connect_db()
    if not conn:
        print("Database connection failed. Exiting.")
        return

    for calendar_name in calendar_names:
        print(f"Fetching events from '{calendar_name}'...\n")
        events = get_calendar_events(user_upn) #test(config.USER_UPN) # Testing

        if events:
            for event in events:
                print(f"Event ID: {event['Event ID']}")
                print(f"Organizer: {event['Organizer']}")
                print(f"Title: {event['Title']}")
                print(f"Description: {event['Description']}")
                print(f"Location: {event['Location']}")
                '''attendees_dict = {
                    attendee["emailAddress"]["name"]: attendee["type"]
                    for attendee in event.get("attendees", [])
                }'''
                print(f"Attendees: {event['Attendees']}")
                print(f"Meeting Type: {event['Meeting Type']}") 
                print(f"Start: {event['Start']}")
                print(f"End: {event['End']}")
                print(f"Date Extracted: {event['Date Extracted']}\n")
                store_calendar_event(conn, event)
        else:
            print("No events found in default Calendar.")

    conn.close()
    print("✅ Database connection closed.")

if __name__ == "__main__":
    main()
