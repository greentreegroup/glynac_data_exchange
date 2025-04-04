import subprocess

def main():
    print("=== Step 1: Extracting emails in parallel and saving to JSON ===")
    subprocess.run(["python", "email_batch_extract.py"])

    print("\n=== Step 2: Loading JSON files and inserting into database ===")
    subprocess.run(["python", "store_emails.py"])

    print("\nAll steps completed.")

if __name__ == "__main__":
    main()