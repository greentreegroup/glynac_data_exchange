def process_messages(messages):
    """Processes raw Teams messages and extracts key details."""
    processed = []
    for msg in messages.get("value", []):  # 'value' contains the list of messages
        processed.append({
            "channel": msg.get("channelIdentity", {}).get("channelId"),
            "sender": msg.get("from", {}).get("user", {}).get("displayName"),
            "text": msg.get("body", {}).get("content"),
            "timestamp": msg.get("createdDateTime")
        })
    return processed
