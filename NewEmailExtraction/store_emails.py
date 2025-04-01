import os
import json
import psycopg2
import config

EMAIL_JSON_FOLDER = "email_json"

def connect_db():
    return psycopg2.connect(
        host=config.DB_HOST,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT
    )

def load_emails_from_json(folder):
    all_emails = []
    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    all_emails.extend(data)
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
    return all_emails

def batch_insert_emails(emails, conn):
    if not emails:
        print("No emails to insert.")
        return

    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO email_data_field (
            email_id,
            conversation_id,
            sender,
            recipient,
            reply_to,
            in_reply_to,
            subject,
            body,
            received_at,
            sent_at,
            date_extracted
        )
        VALUES (%(email_id)s, %(conversation_id)s, %(from)s, %(to)s, %(reply_to)s,
                %(in_reply_to)s, %(subject)s, %(body)s, %(received_at)s,
                %(sent_at)s, %(date_extracted)s)
        ON CONFLICT (email_id) DO NOTHING;
        """
        try:
            cur.executemany(insert_query, emails)
            conn.commit()
            print(f"Inserted {len(emails)} emails into database.")
        except Exception as e:
            conn.rollback()
            print(f"Failed to insert emails: {e}")

def main():
    print("Starting email import from JSON...")
    conn = connect_db()
    emails = load_emails_from_json(EMAIL_JSON_FOLDER)
    batch_insert_emails(emails, conn)
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()