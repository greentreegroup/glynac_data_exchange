from datetime import datetime

def process_messages(messages):
    """Clean and format messages before storing in the database."""
    processed_messages = []
    
    for message in messages:
        message_id = message.get("id", None)
        created_at = message.get("createdDateTime", None)
        formatted_time = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ") if created_at else None
        
        body_content = message.get("body", {}).get("content", None)
        thread_id = message.get("replyToId", None)  # Only for channel messages

        # Ignore system messages
        if message.get("messageType", "") in ["systemEventMessage", "unknownFutureValue"]:
            continue

        # Handle sender information safely
        sender = message.get("from", {})
        sender_name = "Unknown Sender"

        if isinstance(sender, dict) and sender.get("user"):  # Ensure sender is a human user
            sender_name = sender["user"].get("displayName", "Unknown User")
        else:
            continue  # Skip messages from non-users

        processed_messages.append({
            "message_id": message_id,
            "created_at": formatted_time,
            "sender_name": sender_name,
            "body_content": body_content,
            "thread_id": thread_id
        })
    
    return processed_messages
