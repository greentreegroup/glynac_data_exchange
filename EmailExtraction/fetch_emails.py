import requests
from auth_token import get_access_token
import config
from bs4 import BeautifulSoup

# Specify the email fetch emails from
USER_EMAIL = config.USER_EMAIL

def fetch_outlook_emails():
    """Fetch emails from Outlook using Microsoft Graph API."""
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # API endpoint for fetching emails
    messages_url = config.GRAPH_API_MESSAGES_ENDPOINT.format(user_id=USER_EMAIL)
    
    # Fetch emails (handle pagination)
    emails = []
    while messages_url:
        response = requests.get(messages_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            emails.extend(data.get("value", []))  # Add emails from this page
            messages_url = data.get("@odata.nextLink")  # Get the next page URL
        else:
            print(f"Error fetching emails: {response.status_code} - {response.text}")
            break
    
    return emails

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

# Test fetching emails
if __name__ == "__main__":
    emails = fetch_outlook_emails()
    for email in emails[:5]:  # Print first 5 emails
        to_recipients = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("toRecipients", [])])
        reply_to = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("replyTo", [])])

        print(f"Email ID: {email['id']}")
        print(f"Received At: {email['receivedDateTime']}")
        print(f"Sent At: {email['sentDateTime']}")
        print(f"From: {email['from']['emailAddress']['address']}")
        print(f"To: {to_recipients}")
        print(f"Conversation ID: {email['conversationId']}")
        print(f"Reply-To: {reply_to}\n")
        print(f"Subject: {email['subject']}")
        print(f"Body: {html_to_text(email['body']['content'])}\n")