import psycopg2
import config

def store_users_in_db(users):
    conn = psycopg2.connect(
        host=config.DB_HOST,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        sslmode='require'
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lcw_users (
            user_principal_name TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            analyze_ok TEXT
        )
    """)

    excluded_users = {
        "c.adams@lcwmail.com", 
        "n.barile@lcwmail.com", 
        "a.wicksbowles@lcwmail.com",
        "r.parrilla@lcwmail.com"
    }

    for user in users:
        name = user.get('displayName')
        email = user.get('mail') or user.get('userPrincipalName')
        upn = user.get('userPrincipalName')

        analyze_ok = 'N' if upn in excluded_users else 'Y'

        cursor.execute("""
            INSERT INTO lcw_users (
                user_principal_name,
                name,
                email,
                analyze_ok
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_principal_name) DO UPDATE
            SET name = EXCLUDED.name,
                email = EXCLUDED.email,
                analyze_ok = EXCLUDED.analyze_ok
        """, (upn, name, email, analyze_ok))

    conn.commit()
    cursor.close()
    conn.close()