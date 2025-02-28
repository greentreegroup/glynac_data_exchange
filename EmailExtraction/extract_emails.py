import requests
from auth_token import get_access_token
import config
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse

def fetch_paginated_results(url, headers):
    """Fetches all results from a paginated API endpoint. 
    Microsoft Graph API returns large datasets in multiple pages. 
    This function follows the '@odata.nextLink' field to request 
    additional pages until all results are retrieved."""
    all_results = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching data ({response.status_code}): {response.text}")
            return []

        data = response.json()
        all_results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # Get next page if available

    return all_results

def fetch_user_emails(user_email):
    """Fetch all emails for a given user."""
    access_token = get_access_token()
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_email}/messages" # ?$top=100"
    headers = {"Authorization": f"Bearer {access_token}"}

    return fetch_paginated_results(url, headers)

def html_to_text(html_content):
    """Convert HTML content to plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

def extract_emails(user_email):
    """Fetch and process emails."""
    emails = fetch_user_emails(user_email)
    processed_emails = []
    for email in emails:
        email_id = email.get("id", "N/A")
        conversation_id = email.get("conversationId", "N/A")
        sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")
        
        to_recipients = ", ".join(
            [recipient["emailAddress"]["address"] for recipient in email.get("toRecipients", []) if "emailAddress" in recipient]
        ) or "N/A"

        reply_to = ", ".join(
            [recipient["emailAddress"]["address"] for recipient in email.get("replyTo", []) if "emailAddress" in recipient]
        ) or "N/A"

        subject = email.get("subject", "No Subject")
        body = html_to_text(email.get("body", {}).get("content", "No Content"))

        def parse_timestamp(timestamp):
            """Automatically parse timestamps using dateutil.parser."""
            if not timestamp:
                return "N/A"
            try:
                return parse(timestamp).isoformat()  # Detects format
            except Exception:
                print(f"Invalid timestamp format: {timestamp}")
                return "Invalid Timestamp"

        received_at = parse_timestamp(email.get("receivedDateTime"))
        sent_at = parse_timestamp(email.get("sentDateTime"))

        # Add to processed list
        processed_emails.append({
            "Email ID": email_id,
            "Conversation ID": conversation_id,
            "From": sender,
            "To": to_recipients,
            "Reply-To": reply_to,
            "Subject": subject,
            "Body": body,
            "Received At": received_at,
            "Sent At": sent_at,
            "Date Extracted": datetime.utcnow().isoformat()
        })

    return processed_emails