from collections import defaultdict
from dateutil.parser import parse

def calculate_response_times(emails):
    """Computes email response times within conversations."""
    
    # Group emails by conversationId
    conversations = defaultdict(list)
    for email in emails:
        conversations[email["Conversation ID"]].append(email)

    response_times = []
    
    # Process each thread
    for conv_id, conv_emails in conversations.items():
        # Sort emails by timestamp
        conv_emails.sort(key=lambda x: parse(x["Received At"]))
        
        email_lookup = {email["Email ID"]: email for email in conv_emails}
        
        # Find replies and calculate response time
        for email in conv_emails:
            if email.get("InReplyTo") and email["InReplyTo"] in email_lookup:
                prev_email = email_lookup[email["InReplyTo"]]

                # Ensure it's a reply & from a different sender
                if email["From"] != prev_email["From"]:
                    prev_received = parse(prev_email["Received At"])
                    curr_received = parse(email["Received At"])

                    # Compute response time
                    response_time = (curr_received - prev_received).total_seconds() / 60  # Convert to minutes

                    response_times.append({
                        "Conversation ID": conv_id,
                        "Reply Email ID": email["Email ID"],
                        "Reply From": email["From"],
                        "Reply To": prev_email["From"],
                        "Response Time (minutes)": response_time
                    })
    
    return response_times

def categorize_sender(sender_email):
    """Categorizes the sender as Internal, Vendor, or Client based on domain."""
    
    if not sender_email:
        return "Unknown"  # If email is missing, categorize as Unknown

    sender_email = sender_email.lower()

    # Define domains
    internal_domains = {"glynac.ai", "greentree.group", "springer.capital"}  # Your company's domain
    vendor_domains = {"supplier.com", "thirdparty.org"}  # Add vendor domains
    client_domains = {"customer.com", "businessclient.io"}  # Add client domains
    automated_patterns = [
        "noreply@", "no-reply@", "bot@", "notification@", "alerts@", 
        "system@", "support@", "teams.microsoft.com", "zoom.us", 
        "slack.com", "webex.com", "atlassian.com"
    ]  # Automated system patterns

    # Categorization logic
    if any(sender_email.endswith(f"@{domain}") for domain in internal_domains):
        return "Internal"
    elif any(sender_email.endswith(f"@{domain}") for domain in vendor_domains):
        return "Vendor"
    elif any(sender_email.endswith(f"@{domain}") for domain in client_domains):
        return "Client"
    elif any(pattern in sender_email for pattern in automated_patterns):
        return "Automated"
    else:
        return "External"  # If not categorized, label as External