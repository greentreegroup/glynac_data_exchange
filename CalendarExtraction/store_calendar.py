import psycopg2
import config
import json

DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT

def connect_db():
    """Establish connection to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            sslmode="require"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def store_calendar_event(conn, event_data):
    """Insert calendar event data into the database."""
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO calendar_events (event_id, tenant_id, organizer_name, title, description, location, attendees,
                                         virtual, start_time, end_time, date_extracted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING;
            """
            cursor.execute(insert_query, (
                event_data["Event ID"],
                event_data["Tenant ID"], event_data["Organizer"], event_data["Title"],
                event_data["Description"], event_data["Location"], json.dumps(event_data["Attendees"]),
                event_data["Virtual"], event_data["Start"], event_data["End"],
                event_data["Date Extracted"]
            ))
            conn.commit()
            print(f"Event {event_data['Event ID']} inserted successfully!")
    except Exception as e:
        print(f"Error inserting event: {e}")
