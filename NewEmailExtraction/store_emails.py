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
SEEDED_IDS_FILE = "seeded_email_ids.json"  # File to track seeded IDs
BATCH_SIZE = 100  # Define the batch size
MAX_WORKERS = 24  # Define the number of worker threads

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
    inbox_emails = []
    sent_emails = []

    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if not file_name.endswith(".json"):
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if file_name.startswith("inbox_"):
                    inbox_emails.extend(data)
                elif file_name.startswith("sentitems_"):
                    sent_emails.extend(data)
        except Exception as e:
            logging.error(f"Error loading {file_name}: {e}")

    return {"Inbox": inbox_emails, "SentItems": sent_emails}

def load_seeded_ids():
    seeded_ids = set()
    if os.path.exists(SEEDED_IDS_FILE):
        try:
            with open(SEEDED_IDS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    seeded_ids.update(data)
                else:
                    logging.warning(f"'{SEEDED_IDS_FILE}' does not contain a list of IDs. Starting with an empty set.")
        except FileNotFoundError:
            pass  # File will be created if it doesn't exist
        except json.JSONDecodeError:
            logging.warning(f"Error decoding '{SEEDED_IDS_FILE}'. Starting with an empty set.")
    return seeded_ids

def save_seeded_ids(seeded_ids):
    existing_seeded_ids = load_seeded_ids()  # Load previously saved IDs
    updated_seeded_ids = existing_seeded_ids.union(seeded_ids)  # Combine with new IDs
    try:
        with open(SEEDED_IDS_FILE, "w") as f:
            json.dump(list(updated_seeded_ids), f, indent=2)
    except Exception as e:
        logging.error(f"Error saving seeded IDs to '{SEEDED_IDS_FILE}': {e}")

def insert_batch(batch, seeded_ids, table_name):
    conn = None
    thread_name = threading.current_thread().name
    inserted_count = 0
    batch_to_insert = []

    for email in batch:
        email_id = email.get("email_id")
        if email_id and email_id not in seeded_ids:
            batch_to_insert.append(email)

    if not batch_to_insert:
        logging.info(f"Thread: {thread_name} - No new emails to insert from this batch.")
        return

    try:
        conn = connect_db()
        with conn.cursor() as cur:
            insert_query = f"""
            INSERT INTO {table_name} (
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
            cur.executemany(insert_query, batch_to_insert)
            conn.commit()
            inserted_count = cur.rowcount
            logging.info(f"Thread: {thread_name} - Inserted {inserted_count} new emails from batch of {len(batch)}.")

            # Update the seeded IDs with the successfully inserted ones
            for email in batch_to_insert:
                if email.get("email_id"):
                    seeded_ids.add(email["email_id"])

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logging.error(f"Thread: {thread_name} - Failed to insert batch: {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Thread: {thread_name} - An unexpected error occurred during batch insertion: {e}")
    finally:
        if conn:
            conn.close()
        logging.debug(f"Thread: {thread_name} - Database connection closed.")

def main():
    logging.info("Starting email import from JSON using threads (skipping already seeded IDs)...")
    foldered_emails = load_emails_from_json(EMAIL_JSON_FOLDER)
    seeded_ids = load_seeded_ids()
    logging.info(f"Loaded {len(seeded_ids)} already seeded email IDs.")

    for folder_name, emails in foldered_emails.items():
        if not emails:
            logging.info(f"No emails found for folder: {folder_name}")
            continue

        table_name = "email_data_field_inbox" if folder_name == "Inbox" else "email_data_field_sent"
        logging.info(f"Processing {len(emails)} emails from {folder_name} folder into table '{table_name}'.")

        # Add platform + user fallback
        for email in emails:
            email["platform"] = "Outlook"
            email["user_upn"] = email.get("user_upn", "unknown@lcwmail.com")
            email["body"] = email.get("body") or email.get("full_body") or ""

        emails_to_process = [e for e in emails if e.get("email_id") and e["email_id"] not in seeded_ids]

        if not emails_to_process:
            logging.info(f"No new emails to insert for {folder_name}.")
            continue

        batches = [emails_to_process[i:i + BATCH_SIZE] for i in range(0, len(emails_to_process), BATCH_SIZE)]
        logging.info(f"{len(batches)} batches to process for {folder_name} folder.")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(insert_batch, batch, seeded_ids, table_name) for batch in batches]
            for future in futures:
                future.result()

    save_seeded_ids(seeded_ids)
    logging.info("Done with threaded email import (Inbox and SentItems).")


if __name__ == "__main__":
    main()