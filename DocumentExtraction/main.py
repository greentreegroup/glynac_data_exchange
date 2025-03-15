from extract_documents import get_recent_files
from store_documents import store_document_activity, connect_db
import config

def main():
    """Extract document activity from SharePoint and store."""

    if not config.SITE_ID or not config.DRIVE_ID:
        print("Error: SITE_ID or DRIVE_ID is not set. Exiting...")
        return
    
    conn = connect_db()
    if not conn:
        print("Database connection failed. Exiting.")
        return

    print(f"\nUsing Site ID: {config.SITE_ID}")
    print(f"Using Drive ID: {config.DRIVE_ID}")

    print("\nFetching recent document activity...")
    document_activity = get_recent_files(config.SITE_ID, config.DRIVE_ID)

    if document_activity:
        print(f"\nTotal files retrieved: {len(document_activity)}")
        for file in document_activity:
            print(f"Activity ID: {file['Activity ID']}")
            print(f"File Name: {file['File Name']}")
            print(f"File Type: {file['File Type']}")
            print(f"User: {file['User']}")
            print(f"Timestamp: {file['Timestamp']}")
            print(f"Date Extracted: {file['Date Extracted']}\n")
            store_document_activity(conn, file)
    else:
        print("No recent document activity found.")

    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()
