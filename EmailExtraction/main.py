from extract_emails import extract_emails
from store_emails import insert_email
from fetch_users import get_analyzable_users

def main():
    users = get_analyzable_users()

    if not users:
        print("No analyzable users found.")
        return

    for user_upn in users:
        print(f"\nFetching emails for {user_upn}...")
        emails = extract_emails(user_upn)

        if not emails:
            print("No emails found or mailbox not accessible.")
            continue

        print(f"Found {len(emails)} emails.")

        for email in emails:
            email_data = {
                "email_id": email["email_id"],
                "subject": email["subject"],
                "from": email["from"],
                "to": email["to"],
                "reply_to": email["reply_to"],
                "conversation_id": email["conversation_id"],
                "received_at": email["received_at"],
                "sent_at": email["sent_at"],
                "date_extracted": email["date_extracted"],
                "full_body": email["full_body"]
            }
            insert_email(email_data, user_upn)

    print("Finished extracting and storing emails for all analyzable users.")

if __name__ == "__main__":
    main()
