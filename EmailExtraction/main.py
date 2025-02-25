from fetch_emails import fetch_user_emails
#from process_emails import store_emails

def main():
    print("Fetching emails...")
    emails = fetch_user_emails()
    print(f"Fetched {len(emails)} emails.")
    #store_emails(emails)
    print(f"Stored {len(emails)} emails.")


if __name__ == "__main__":
    main()