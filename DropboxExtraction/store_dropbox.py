import json
import psycopg2
import config

def get_db_connection():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        sslmode="require"
    )

def insert_dropbox_file(cursor, file):
    """Insert or update a Dropbox file record in the database."""
    insert_query = """
    INSERT INTO dropbox_files (id, name, path, size, modified)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        path = EXCLUDED.path,
        size = EXCLUDED.size,
        modified = EXCLUDED.modified;
    """
    cursor.execute(insert_query, (
        file["id"],
        file["name"],
        file["path"],
        file["size"],
        file["modified"]
    ))

def store_metadata_from_json(json_file="filtered_dropbox_files.json"):
    """Load Dropbox metadata from JSON and insert into DB."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            files = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    if not files:
        print("No file metadata found.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for file in files:
            insert_dropbox_file(cursor, file)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Inserted or updated {len(files)} Dropbox file(s) into the database.")

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    store_metadata_from_json()
