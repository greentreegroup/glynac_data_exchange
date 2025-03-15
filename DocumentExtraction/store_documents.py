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

def store_document_activity(conn, file_data):
    """Insert document activity data into the database."""
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO document_activity (
                activity_id, file_name, file_type, user_name, 
                timestamp, date_extracted
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (activity_id) DO NOTHING;
            """
            cursor.execute(insert_query, (
                file_data["Activity ID"], file_data["File Name"], 
                file_data["File Type"], file_data["User"], 
                file_data["Timestamp"], file_data["Date Extracted"]
            ))
            conn.commit()
            print(f"File activity stored: {file_data['File Name']}")
    except Exception as e:
        conn.rollback()  # Prevent transaction issues
        print(f"Error inserting document activity: {e}")
