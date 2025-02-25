import config
from extract_messages import extract_teams
from extract_messages import extract_channels
from extract_messages import extract_channel_messages
from process_messages import process_messages

def main():
    """Main function to extract Teams, Channels, and Messages."""
    
    print(f"Fetching Teams for {config.USER_UPN}...")
    teams = extract_teams(config.USER_UPN)
    
    if not teams:
        print("No Teams found for the user. Exiting.")
        return
    
    for team in teams[:2]:  # Limit to first 2 teams for testing
        print(f"\nTeam: {team['displayName']} (ID: {team['id']})")
        
        print("Fetching Channels...")
        channels = extract_channels(team["id"])
        
        if not channels:
            print(f"No Channels found for Team {team['displayName']}. Skipping...")
            continue
        
        for channel in channels[:2]:  # Limit to first 2 channels
            print(f"\nChannel: {channel['displayName']} (ID: {channel['id']})")
            
            print("Fetching Messages...")
            messages = extract_channel_messages(team["id"], channel["id"])
            
            if not messages:
                print(f"No messages found in Channel {channel['displayName']}.")
                continue
            
            print(f"Total Messages Fetched: {len(messages)}")
            
            # Process the messages
            processed_messages = process_messages(messages)
        print("Processed Messages:", processed_messages)

                # Store the message in the database
                
    

if __name__ == "__main__":
    main()
