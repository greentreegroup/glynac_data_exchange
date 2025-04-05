import psycopg2
import config

def connect_db():
    """Establish connection to PostgreSQL database."""
    try:
        return psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            sslmode="prefer"
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def store_team_event(conn, event):
    """Insert a Dropbox team activity log event into the database."""
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO dropbox_team_events (
            event_id, timestamp, event_type, asset_type,
            name, path, actor_name, actor_email
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO UPDATE SET
            timestamp = EXCLUDED.timestamp,
            event_type = EXCLUDED.event_type,
            asset_type = EXCLUDED.asset_type,
            name = EXCLUDED.name,
            path = EXCLUDED.path,
            actor_name = EXCLUDED.actor_name,
            actor_email = EXCLUDED.actor_email;
        """
        cursor.execute(insert_query, (
            event.get("event_id"),
            event.get("timestamp"),
            event.get("event_type"),
            event.get("asset_type"),
            event.get("name"),
            event.get("path"),
            event.get("actor_name"),
            event.get("actor_email")
        ))
        print(f"Stored event: {event.get('name')} — {event.get('event_id')}")

def insert_team_events(event_list):
    """Insert a list of Dropbox team events into the DB."""
    conn = connect_db()
    if not conn:
        print("Unable to connect to the database.")
        return

    try:
        for event in event_list:
            store_team_event(conn, event)

        conn.commit()
        print(f"Inserted or updated {len(event_list)} Dropbox team event(s) into the database.")

    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")

    finally:
        conn.close()