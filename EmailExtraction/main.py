from extract_emails import extract_emails
from utils import calculate_response_times
from store_emails import connect_db, insert_email
import config
from test import mock_api_response

def main():
    """Extract and display user emails."""
    user_email = config.USER_EMAIL
    if not user_email:
        print("Error: USER_EMAIL is not set.")
        return

    print(f"\nFetching emails for {user_email}...")
    emails = extract_emails(user_email)
    # emails = mock_api_response  # Testing

    if not emails:
        print("No emails found.")
        return

    print(f"Found {len(emails)} emails.")

    response_times = calculate_response_times(emails)

    conn = connect_db()
    if conn is None:
        print("Database connection failed. Skipping storage.")
        return
    
    for email in emails[:5]:  # Limit output for testing
        print(f"\nEmail ID: {email['Email ID']}")
        print(f"Subject: {email['Subject']}")
        print(f"From: {email['From']}")
        #print(f"Category: {email['Category']}")
        print(f"To: {email['To']}")
        print(f"Reply-To: {email['Reply-To']}")
        print(f"Conversation ID: {email['Conversation ID']}")
        print(f"Received At: {email['Received At']} | Sent At: {email['Sent At']}")
        print(f"Date Extracted: {email['Date Extracted']}")

        matching_response = next(
            (resp for resp in response_times if resp["Reply Email ID"] == email["Email ID"]),
            None
        )

        response_time = matching_response["Response Time (minutes)"] if matching_response else None
        print(f"Response Time: {response_time} minutes" if response_time else "N/A (No reply detected)")

        print(f"Body: {email['Body'][:50]}...\n")  # Limit body preview

        # Store email data in the database
        email_data = {
            "email_id": email["Email ID"],
            "subject": email["Subject"],
            "sender_email": email["From"],
            "recipient_email": email["To"],
            "reply_to": email["Reply-To"],
            "conversation_id": email["Conversation ID"],
            "received_at": email["Received At"],
            "sent_at": email["Sent At"],
            "date_extracted": email["Date Extracted"],
            "response_time": f"{response_time} minutes" if response_time else None,
            "body": email["Body"]
        }
        insert_email(conn, email_data)

    conn.close()
    print("Database connection closed.")
    print("Finished processing and storing emails.")


if __name__ == "__main__":
    main()
