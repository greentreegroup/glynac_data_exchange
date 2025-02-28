from datetime import datetime

def mock_teams_messages():
    """Simulates a Microsoft Teams API response for channel messages."""
    
    mock_response = {
        "value": [
            {
                "id": "12345",
                "messageType": "message",  # ✅ This is a user message
                "createdDateTime": "2025-02-28T10:00:00Z",
                "body": {"content": "Hello team! Let's meet at 3 PM."},
                "from": {"user": {"displayName": "John Doe"}},
                "replyToId": None  # Not a reply
            },
            {
                "id": "12346",
                "messageType": "message",  # ✅ Another user message
                "createdDateTime": "2025-02-28T10:05:00Z",
                "body": {"content": "I'll be there!"},
                "from": {"user": {"displayName": "Jane Smith"}},
                "replyToId": "12345"  # A reply to message ID 12345
            },
            {
                "id": "12347",
                "messageType": "systemEventMessage",  # ❌ This should be filtered out
                "createdDateTime": "2025-02-28T10:10:00Z",
                "body": {"content": "User joined the channel."},
                "from": {"application": {"displayName": "Microsoft Teams"}},
                "replyToId": None
            },
            {
                "id": "12348",
                "messageType": "message",  # ✅ Another user message
                "createdDateTime": "2025-02-28T10:15:00Z",
                "body": {"content": "Looking forward to the meeting."},
                "from": {"user": {"displayName": "Alice Johnson"}},
                "replyToId": None
            }
        ]
    }

    return mock_response["value"]  # Return the list of messages