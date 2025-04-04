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

def insert_batch(batch, seeded_ids):
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
    emails = load_emails_from_json(EMAIL_JSON_FOLDER)
    seeded_ids = load_seeded_ids()
    logging.info(f"Loaded {len(seeded_ids)} already seeded email IDs.")

    emails_to_process = [email for email in emails if email.get("email_id") and email.get("email_id") not in seeded_ids]
    logging.info(f"Found {len(emails_to_process)} new emails in JSON files to process for seeding.")

    # Add only the specified keys if needed
    for email in emails_to_process:
        email["platform"] = "Outlook"
        email["user_upn"] = email.get("user_upn", "unknown@lcwmail.com")
        email["body"] = email.get("body") or email.get("full_body") or ""

    total_emails_to_process = len(emails_to_process)
    logging.info(f"Total new emails to process: {total_emails_to_process}")

    if not emails_to_process:
        logging.info("No new emails to process for seeding.")
        return

    batches = [emails_to_process[i:i + BATCH_SIZE] for i in range(0, total_emails_to_process, BATCH_SIZE)]
    total_batches = len(batches)
    logging.info(f"Total batches to process: {total_batches} with batch size: {BATCH_SIZE}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Pass the seeded_ids set to the insert_batch function
        futures = [executor.submit(insert_batch, batch, seeded_ids) for batch in batches]
        for future in futures:
            future.result()  # Wait for all tasks to complete

    # Save the updated set of seeded IDs after the process
    save_seeded_ids(seeded_ids)
    logging.info("Done with threaded email import (skipped already seeded IDs).")

if __name__ == "__main__":
    main()