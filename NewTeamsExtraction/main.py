import subprocess

def main():
    print("=== Step 1: Extracting Teams messages and saving to JSON ===")
    subprocess.run(["python", "teams_batch_extract.py"])

    print("\n=== Step 2: Inserting messages into database ===")
    subprocess.run(["python", "store_teams.py"])

    print("\nAll steps completed.")

if __name__ == "__main__":
    main()
