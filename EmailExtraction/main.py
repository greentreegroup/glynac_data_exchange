from extract_emails import extract_emails
import config

def main():
    """Extract and display user emails."""
    user_email = config.USER_EMAIL
    if not user_email:
        print("Error: USER_EMAIL is not set.")
        return

    print(f"\nFetching emails for {user_email}...")
    emails = extract_emails(user_email)

    if not emails:
        print("No emails found.")
        return

    print(f"Found {len(emails)} emails.")

    for email in emails[:5]:  # Limit output for testing
        print(f"\nEmail ID: {email['Email ID']}")
        print(f"Subject: {email['Subject']}")
        print(f"From: {email['From']}")
        print(f"To: {email['To']}")
        print(f"Reply-To: {email['Reply-To']}")
        print(f"Conversation ID: {email['Conversation ID']}")
        print(f"Received At: {email['Received At']} | Sent At: {email['Sent At']}")
        print(f"Date Extracted: {email['Date Extracted']}")
        print(f"Body: {email['Body'][:50]}...\n")  # Limit body preview for testing

    # Store emails into database

if __name__ == "__main__":
    main()
