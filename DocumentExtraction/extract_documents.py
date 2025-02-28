import requests
from auth_token import get_access_token
from config import GRAPH_API_ENDPOINT
from datetime import datetime

def fetch_paginated_results(url, headers):
    """Handles pagination for Graph API requests."""
    all_results = []

    while url:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching data ({response.status_code}): {response.text}")
            return []

        data = response.json()
        all_results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # Get next page if available

    return all_results

def get_files_in_folder(site_id, drive_id, folder_id, folder_name="Root"):
    """Recursively fetches all files inside a folder."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_API_ENDPOINT}/sites/{site_id}/drives/{drive_id}/items/{folder_id}/children"

    files = fetch_paginated_results(url, headers)
    all_files = []

    for item in files:
        if "folder" in item:
            print(f"Found folder: {item['name']} (Fetching files inside...)")
            all_files.extend(get_files_in_folder(site_id, drive_id, item["id"], item["name"]))
        else:
            all_files.append(item)

    return all_files

def get_recent_files(site_id, drive_id):
    """Fetches all document activity from SharePoint, including files inside folders."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_API_ENDPOINT}/sites/{site_id}/drives/{drive_id}/root/children"

    all_items = fetch_paginated_results(url, headers)
    all_files = []

    for item in all_items:
        if "folder" in item:
            print(f"Found folder: {item['name']} (Fetching files inside...)")
            all_files.extend(get_files_in_folder(site_id, drive_id, item["id"], item["name"]))
        else:
            all_files.append(item)

    extracted_data = [
        {
            "Activity ID": file.get("id", "Unknown"),
            "File Name": file.get("name", "Unknown"),
            "File Type": file.get("file", {}).get("mimeType", "Unknown"),
            "User": file.get("lastModifiedBy", {}).get("user", {}).get("displayName", "Unknown"),
            "Timestamp": file.get("lastModifiedDateTime", "Unknown"),
            "Date Extracted": datetime.utcnow().isoformat()
        }
        for file in all_files
    ]

    return extracted_data
