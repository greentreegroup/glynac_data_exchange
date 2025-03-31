import requests

def get_all_users(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = 'https://graph.microsoft.com/v1.0/users'

    users = []
    while url:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        users.extend(data.get('value', []))
        url = data.get('@odata.nextLink')  # handle paging

    return users