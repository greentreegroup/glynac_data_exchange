from auth_token import get_access_token
from fetch_users import get_all_users
from store_users import store_users_in_db

def main():
    token = get_access_token()
    users = get_all_users(token)
    store_users_in_db(users)
    print(f"Imported {len(users)} users to database.")

if __name__ == "__main__":
    main()
