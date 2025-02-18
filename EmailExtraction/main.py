from fetch_emails import fetch_outlook_emails
from store_emails import store_emails

def main():
    print("Fetching emails...")
    emails = fetch_outlook_emails()
    print(f"Fetched {len(emails)} emails.")
    store_emails(emails)
    print(f"Stored {len(emails)} emails.")


if __name__ == "__main__":
    main()