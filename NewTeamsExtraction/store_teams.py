import os
import json
import psycopg2
import config

TEAMS_JSON_FOLDER = "teams_json"

def connect_db():
    return psycopg2.connect(
        host=config.DB_HOST,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT,
        sslmode="require"
    )

def load_messages_from_json(folder):
    all_messages = []
    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    all_messages.extend(data)
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
    return all_messages

def batch_insert_messages(messages, conn):
    if not messages:
        print("No messages to insert.")
        return

    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO chat_data_field_test (
            platform,
            chat_id,
            chat_from,
            channel,
            message,
            thread_id,
            timestamp,
            mentioned_users,
            date_extracted
        )
        VALUES (%(platform)s, %(chat_id)s, %(chat_from)s, %(channel)s,
                %(message)s, %(thread_id)s, %(timestamp)s,
                %(mentioned_users)s, %(date_extracted)s)
        ON CONFLICT (chat_id) DO NOTHING;
        """
        try:
            cur.executemany(insert_query, messages)
            conn.commit()
            print(f"Inserted {len(messages)} messages into database.")
        except Exception as e:
            conn.rollback()
            print(f"Failed to insert messages: {e}")


def main():
    print("Starting Teams message import from JSON...")
    conn = connect_db()
    messages = load_messages_from_json(TEAMS_JSON_FOLDER)
    batch_insert_messages(messages, conn)
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()