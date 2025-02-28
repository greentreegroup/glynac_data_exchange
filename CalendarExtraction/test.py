from datetime import datetime
def test(user_email):
    """Simulates fetching calendar events using a mock API response."""
    
    # Mock response simulating an API call
    mock_response = {
        "value": [
            {
                "id": "AAMkAG...",
                "subject": "Test API Meeting",
                "bodyPreview": "This is a test meeting created for API testing.",
                "location": {"displayName": "Test Location"},
                "organizer": {
                    "emailAddress": {"name": "Alice Johnson", "address": "alice.johnson@example.com"}
                },
                "attendees": [
                    {
                        "emailAddress": {"name": "Bob Smith", "address": "bob.smith@example.com"},
                        "type": "required"
                    },
                    {
                        "emailAddress": {"name": "Charlie Lee", "address": "charlie.lee@example.com"},
                        "type": "optional"
                    }
                ],
                "start": {"dateTime": "2024-02-26T10:00:00", "timeZone": "UTC"},
                "end": {"dateTime": "2024-02-26T11:00:00", "timeZone": "UTC"},
                "meetingMessageType": "meetingRequest",
                "Date Extracted": datetime.utcnow().isoformat()
            }
        ]
    }

    return mock_response["value"]
