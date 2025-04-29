import psycopg2
import config

def get_analyzable_users():
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        sslmode="require"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_principal_name FROM lcw_users
        WHERE analyze_ok = 'Y'
    """)
    users = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return users
