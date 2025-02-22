'''
import psycopg2
from config import DB_CONFIG

def store_messages(messages):
    """Store processed messages in PostgreSQL database."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    insert_query = """
    INSERT INTO teams_messages (message_id, created_at, sender_name, body_content, thread_id)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (message_id) DO NOTHING;
    """

    for msg in messages:
        cur.execute(insert_query, (
            msg["message_id"], msg["created_at"], msg["sender_name"], msg["body_content"], msg["thread_id"]
        ))

    conn.commit()
    cur.close()
    conn.close()
'''