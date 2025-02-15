import config


def store_emails(emails):
    #Store email data into db
    for email in emails:
        to_recipients = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("toRecipients", [])])
        reply_to = ", ".join([recipient["emailAddress"]["address"] for recipient in email.get("replyTo", [])])

        data = {
            "email_id": email["id"],
            "conversation_id": email["conversationId"],
            "sender": email["from"]["emailAddress"]["address"],
            "recipient": to_recipients,
            "reply_to": reply_to if reply_to else None,
            "subject": email["subject"],
            "full_body": email["body"]["content"],
            "received_at": email["receivedDateTime"],
            "sent_at": email["sentDateTime"]
        }

        #ADD: Store into db
        

# Test storing emails
if __name__ == "__main__":
    from fetch_emails import fetch_outlook_emails

    emails = fetch_outlook_emails()
    if emails:
        store_emails(emails)
    else:
        print("No emails found to store.")