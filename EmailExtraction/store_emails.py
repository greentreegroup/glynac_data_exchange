import psycopg2
import config

def insert_email(email_data, user_upn):
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            sslmode="require"
        )

        with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO email_data_field (
                    platform, user_upn,
                    email_id, subject, sent_from, sent_to, reply_to,
                    conversation_id, received_at, sent_at,
                    date_extracted, full_body
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email_id) DO NOTHING;
            """
            cursor.execute(insert_query, (
                "Outlook", user_upn,
                email_data["email_id"],
                email_data["subject"],
                email_data["from"],
                email_data["to"],
                email_data["reply_to"],
                email_data["conversation_id"],
                email_data["received_at"],
                email_data["sent_at"],
                email_data["date_extracted"],
                email_data["full_body"]
            ))

        conn.commit()
        conn.close()
        print(f"Inserted email {email_data['email_id']} for {user_upn}")

    except Exception as e:
        print(f"Error inserting email for {user_upn}: {e}")
        return False
