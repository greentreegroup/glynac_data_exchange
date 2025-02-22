import requests
from auth_token import get_access_token
import config

ACCESS_TOKEN = get_access_token()
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_user_id(target_email_or_upn):
    """Retrieve a user's ID by searching all users in the tenant."""
    url = f"{config.GRAPH_API_ENDPOINT}/users"
    response = requests.get(url, headers=HEADERS)

    print(f"Fetching all users to find: {target_email_or_upn}")
    print(f"Response Code: {response.status_code}")

    if response.status_code == 200:
        users = response.json().get("value", [])
        for user in users:
            user_email = user.get("mail")
            if user_email and user_email.lower() == target_email_or_upn.lower():
                print(f"Found User ID: {user['id']} for {target_email_or_upn}")
                return user['id']
        print(f"No user found with email: {target_email_or_upn}")
        return None
    else:
        print(f"Error fetching users: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # email/username of the user to fetch
    target_email_or_upn = config.USER_UPN

    # Fetch the correct user ID
    user_id = get_user_id(target_email_or_upn)
