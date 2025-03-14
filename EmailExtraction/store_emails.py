import psycopg2
import config

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

def insert_email(conn, email_data):
    """Insert email data into the database."""
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO email_data (email_id, subject, sender_email, recipient_email, reply_to, 
                                    conversation_id, received_at, sent_at, date_extracted, response_time, body)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email_id) DO NOTHING;
            """
            cursor.execute(insert_query, (
                email_data["email_id"], email_data["subject"], email_data["sender_email"],
                email_data["recipient_email"], email_data["reply_to"], email_data["conversation_id"],
                email_data["received_at"], email_data["sent_at"], email_data["date_extracted"],
                email_data["response_time"], email_data["body"]
            ))
            conn.commit()
            print("Data inserted successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")
