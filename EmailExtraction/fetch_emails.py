import requests
from auth_token import get_access_token
import config
from bs4 import BeautifulSoup

# Get access token
ACCESS_TOKEN = get_access_token()
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_all_pages(url):
    """Fetch all pages of data from a paginated API endpoint."""
    items = []
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            items.extend(data.get("value", []))  # Add emails from this page
            url = data.get("@odata.nextLink")  # Get the next page URL
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break
    return items

def fetch_user_emails(user_email):
    """Fetch all emails for a given user."""
    url = config.GRAPH_API_MESSAGES_ENDPOINT.format(user_id=user_email)
    return fetch_all_pages(url)

def html_to_text(html_content):
    """Convert HTML content to plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

# Test fetching emails
if __name__ == "__main__":
    user_email = config.USER_EMAIL  # Set user identifier
    emails = fetch_user_emails(user_email)

    if not emails:
        print("No emails found.")
    else:
        print(f"Found {len(emails)} emails. Displaying first 5 messages...")

        for email in emails[:5]:  # Print first 5 emails
            to_recipients = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("toRecipients", [])])
            reply_to = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("replyTo", [])])

            print(f"\nEmail ID: {email['id']}")
            print(f"Received At: {email['receivedDateTime']}")
            print(f"Sent At: {email['sentDateTime']}")
            print(f"From: {email['from']['emailAddress']['address']}")
            print(f"To: {to_recipients}")
            print(f"Conversation ID: {email['conversationId']}")
            print(f"Reply-To: {reply_to}")
            print(f"Subject: {email['subject']}")
            print(f"Body: {html_to_text(email['body']['content'])}\n")
