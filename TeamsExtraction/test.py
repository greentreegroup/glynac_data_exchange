from datetime import datetime

def mock_teams_messages():
    """Simulates a Microsoft Teams API response for varied message formats."""
    
    mock_response = {
        "value": [
            {
                "id": "10001",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:00:00Z",
                "body": {"content": "<p>Hello team! <b>Let's meet at 3 PM.</b></p>"},
                "from": {"user": {"displayName": "John Doe"}},
                "replyToId": None
            },
            {
                "id": "10002",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:05:00Z",
                "body": {"content": "<p>I'll be there! 😊</p>"},
                "from": {"user": {"displayName": "Jane Smith"}},
                "replyToId": "10001"
            },
            {
                "id": "10003",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:10:00Z",
                "body": {"content": "<p>Here’s the agenda:</p><ul><li>Project updates</li><li>Q&A session</li></ul>"},
                "from": {"user": {"displayName": "Alice Johnson"}},
                "replyToId": None
            },
            {
                "id": "10004",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:15:00Z",
                "body": {"content": '<p>Check this out: <a href="https://example.com">Project Docs</a></p>'},
                "from": {"user": {"displayName": "Bob Miller"}},
                "replyToId": None
            },
            {
                "id": "10005",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:20:00Z",
                "body": {"content": "<blockquote>Can you clarify this?</blockquote><p>Yes, sure! Let me explain.</p>"},
                "from": {"user": {"displayName": "Emily Davis"}},
                "replyToId": "10004"
            },
            {
                "id": "10006",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:25:00Z",
                "body": {"content": "<p>Here's the code snippet:</p><pre>print('Hello, World!')</pre>"},
                "from": {"user": {"displayName": "Michael Scott"}},
                "replyToId": None
            },
            {
                "id": "10007",
                "messageType": "message",
                "createdDateTime": "2025-03-14T10:30:00Z",
                "body": {"content": "<p>@John Doe Could you review this?</p>"},
                "from": {"user": {"displayName": "Pam Beesly"}},
                "replyToId": None
            }
        ]
    }

    return mock_response["value"]  # Return the list of messages
