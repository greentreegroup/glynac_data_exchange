from extract_dropbox import list_dropbox_folder
from store_dropbox import insert_dropbox_files

def main():
    files = list_dropbox_folder("")

    if not files:
        print("No files found in Dropbox.")
        return

    print(f"Retrieved {len(files)} files from Dropbox.")

    for file_data in files:
        try:
            insert_dropbox_files(file_data)
        except Exception as e:
            print(f"Failed to insert file: {file_data.get('name', 'Unknown')} - Error: {e}")

    print("Dropbox extraction completed.")

if __name__ == "__main__":
    main()
