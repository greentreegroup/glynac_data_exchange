import os
import json
import psycopg2
import config
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

EMAIL_JSON_FOLDER = "email_json"
BATCH_SIZE = 100  # Define the batch size
MAX_WORKERS = 4  # Define the number of worker threads

def connect_db():
    return psycopg2.connect(
        host=config.DB_HOST,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT,
        sslmode="require"
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
                    logging.error(f"Error loading {file_name}: {e}")
    return all_emails

def insert_batch(batch):
    conn = None
    thread_name = threading.current_thread().name
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            insert_query = """
            INSERT INTO email_data_field_test (
                platform,
                user_upn,
                email_id,
                subject,
                sent_from,
                sent_to,
                reply_to,
                conversation_id,
                received_at,
                sent_at,
                date_extracted,
                full_body
            )
            VALUES (%(platform)s, %(user_upn)s, %(email_id)s, %(subject)s, %(from)s, %(to)s,
                    %(reply_to)s, %(conversation_id)s, %(received_at)s, %(sent_at)s,
                    %(date_extracted)s, %(body)s)
            ON CONFLICT (email_id) DO NOTHING;
            """
            cur.executemany(insert_query, batch)
            conn.commit()
            logging.info(f"Inserted {len(batch)} emails.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logging.error(f"Failed to insert batch: {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"An unexpected error occurred during batch insertion: {e}")
    finally:
        if conn:
            conn.close()
        logging.debug("Database connection closed.")

def main():
    logging.info("Starting email import from JSON using threads...")
    emails = load_emails_from_json(EMAIL_JSON_FOLDER)

    # Add only the specified keys if needed
    for email in emails:
        email["platform"] = "Outlook"
        email["user_upn"] = email.get("user_upn", "unknown@lcwmail.com")
        email["body"] = email.get("body") or email.get("full_body") or ""

    total_emails = len(emails)
    logging.info(f"Total emails loaded: {total_emails}")

    batches = [emails[i:i + BATCH_SIZE] for i in range(0, total_emails, BATCH_SIZE)]
    total_batches = len(batches)
    logging.info(f"Total batches to process: {total_batches} with batch size: {BATCH_SIZE}")

    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(insert_batch, batches)

    logging.info("Done with threaded email import.")

if __name__ == "__main__":
    main()