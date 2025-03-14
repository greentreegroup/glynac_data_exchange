import config
from extract_messages import extract_teams, extract_channels, extract_channel_messages
from store_teams import store_messages_in_db

def main():
    """Extract and store Teams messages."""
    user_upn = config.USER_UPN
    if not user_upn:
        print("Error: USER_UPN is not set.")
        return
    
    print(f"Fetching Teams for {config.USER_UPN}...")
    teams = extract_teams(user_upn)
    
    if not teams:
        print("No Teams found for the user. Exiting.")
        return
    
    for team in teams:
        print(f"\nTeam: {team['displayName']} (ID: {team['id']})")
        
        print("Fetching Channels...")
        channels = extract_channels(team["id"])
        
        if not channels:
            print(f"No Channels found for Team {team['displayName']}. Skipping...")
            continue
        
        for channel in channels:
            print(f"\nChannel: {channel['displayName']} (ID: {channel['id']})")
            
            print("Fetching Messages...")
            messages = extract_channel_messages(team["id"], channel["id"], channel["displayName"])
            
            if not messages:
                print(f"\nNo user messages found in Channel {channel['displayName']}.")
                continue
            
            print(f"\n Total User Messages Fetched: {len(messages)}")
            
            for message in messages[:5]: # Display first 5 messages
                print(f"Chat ID: {message['Chat ID']}")
                print(f"From: {message['From']}")
                print(f"Channel: {message['Channel']}")
                print(f"Message: {message['Message']}")
                print(f"Thread ID: {message.get('Thread ID', 'N/A')}")
                print(f"Timestamp: {message.get('Timestamp', 'N/A')}")
                print(f"Date Extracted: {message['Date Extracted']}\n")

            # Store the message in the database
            store_messages_in_db(messages)    
    

if __name__ == "__main__":
    main()
