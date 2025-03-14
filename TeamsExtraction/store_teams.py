import psycopg2
import config

def connect_db():
    """Connect to the PostgreSQL database and return a connection."""
    return psycopg2.connect(
        host=config.DB_HOST,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT
    )

def store_messages_in_db(messages):
    """Insert extracted messages into the database."""
    conn = connect_db()
    cursor = conn.cursor()

    for msg in messages:
        try:
            cursor.execute("""
                INSERT INTO teams_data (chat_id, from_user, channel_name, message, thread_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO NOTHING;
            """, (
                msg["Chat ID"],
                msg["From"],
                msg["Channel"],
                msg["Message"],
                msg["Thread ID"],
                msg["Timestamp"]
            ))
        except Exception as e:
            print(f"Error inserting message {msg['Chat ID']}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
