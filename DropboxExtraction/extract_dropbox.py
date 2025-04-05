import requests
import json
from auth_dropbox import get_access_token

DROPBOX_API_URL = "https://api.dropboxapi.com/2/files/list_folder"

def list_dropbox_files(path=""):
    """List and filter Dropbox file metadata from the given folder."""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "path": path,
        "recursive": True,
        "include_media_info": False,
        "include_deleted": False
    }

    response = requests.post(DROPBOX_API_URL, headers=headers, json=data)

    if response.status_code != 200:
        print(f"Error listing folder: {response.status_code}")
        print(response.text)
        return []

    all_entries = response.json().get("entries", [])

    # Keep only files (not folders)
    files = [entry for entry in all_entries if entry[".tag"] == "file"]

    # Extract and rename only relevant fields
    simplified_files = []
    for f in files:
        simplified_files.append({
            "id": f.get("id"),
            "name": f.get("name"),
            "path": f.get("path_display"),
            "size": f.get("size"),
            "modified": f.get("server_modified")
        })

    return simplified_files

def save_metadata_to_json(files, output_file="filtered_dropbox_files.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)
    print(f"Saved metadata for {len(files)} files to {output_file}")

if __name__ == "__main__":
    files = list_dropbox_files("")
    save_metadata_to_json(files)
