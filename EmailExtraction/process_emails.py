import config
from fetch_emails import fetch_user_emails, html_to_text
from datetime import datetime

def process_emails(emails):
    """Clean and format emails before storing in the database."""
    processed_emails = []

    for email in emails:
        email_id = email.get("id", None)
        conversation_id = email.get("conversationId", None)
        sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")
        to_recipients = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("toRecipients", []) if "emailAddress" in recipient])
        reply_to = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("replyTo", []) if "emailAddress" in recipient])

        subject = email.get("subject", "No Subject")
        body = html_to_text(email.get("body", {}).get("content", ""))

        # Handle date formatting safely
        received_at = email.get("receivedDateTime", None)
        sent_at = email.get("sentDateTime", None)

        try:
            received_at = datetime.strptime(received_at, "%Y-%m-%dT%H:%M:%S.%fZ") if received_at else None
            sent_at = datetime.strptime(sent_at, "%Y-%m-%dT%H:%M:%S.%fZ") if sent_at else None
        except ValueError:
            received_at, sent_at = None, None

        processed_emails.append({
            "email_id": email_id,
            "conversation_id": conversation_id,
            "sender": sender,
            "recipient": to_recipients,
            "reply_to": reply_to if reply_to else None,
            "subject": subject,
            "body": body,
            "received_at": received_at,
            "sent_at": sent_at
        })

    return processed_emails

# Test processing emails
if __name__ == "__main__":
    emails = fetch_user_emails(config.USER_EMAIL)
    if emails:
        processed_emails = process_emails(emails)
        for email in processed_emails[:5]:  # Print first 5 emails
            print(email)
    else:
        print("No emails found to process.")