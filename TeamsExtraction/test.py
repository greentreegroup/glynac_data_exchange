from process_messages import process_messages

def test_process_messages():
    test_messages = [
        {
            "id": "12345",
            "createdDateTime": "2025-02-21T10:15:40.364Z",
            "body": {"content": "Hello, this is a human message!"},
            "from": {
                "user": {"displayName": "Alice"}
            },
            "messageType": "message"
        },
        {
            "id": "12346",
            "createdDateTime": "2025-02-21T10:16:00.000Z",
            "body": {"content": "Hello, I am a bot!"},
            "from": {
                "application": {"displayName": "Bot-App"}
            },
            "messageType": "message"
        },
        {
            "id": "12347",
            "createdDateTime": "2025-02-21T10:16:20.000Z",
            "body": {"content": "<systemEventMessage/>"},
            "from": None,
            "messageType": "systemEventMessage"
        }
    ]

    processed = process_messages(test_messages)
    
    print("Processed Messages:" , processed)

if __name__ == "__main__":
    test_process_messages()