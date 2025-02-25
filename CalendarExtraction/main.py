from extract_calendar import get_calendar_events, check_calendars
import config

def main():
    """Main function to extract and display calendar events."""
    #print(f"Retrieved user email: {USER_EMAIL}")
    check_calendars(config.USER_UPN)
    events = get_calendar_events(config.USER_UPN)
    
    if events:
        for event in events:
            print(f"Event ID: {event['id']}")
            print(f"Organizer: {event['organizer']['emailAddress']['name']}")
            print(f"Title: {event['subject']}")
            print(f"Description: {event.get('bodyPreview', 'No description')}")
            print(f"Location: {event.get('location', 'No location')}")
            print(f"Attendees: {', '.join([attendee['emailAddress']['name'] for attendee in event.get('attendees', [])])}")
            print(f"Meeting Type: {event.get('meetingMessageType', 'No meeting type')}")
            print(f"Start: {event['start']['dateTime']}")
            print(f"End: {event['end']['dateTime']}\n")
    else:
        print("No events found in default Calendar.")
        
    #Store the events in a database

if __name__ == "__main__":
    main()
