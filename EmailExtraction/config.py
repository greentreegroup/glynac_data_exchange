import os

# Outlook API credentials
OUTLOOK_CLIENT_ID = os.getenv("CLIENT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OUTLOOK_TENANT_ID = os.getenv("TENANT_ID")

# Microsoft Graph API endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
GRAPH_API_ME_ENDPOINT = f"{GRAPH_API_ENDPOINT}/users/{{user_id}}"
GRAPH_API_MESSAGES_ENDPOINT = f"{GRAPH_API_ME_ENDPOINT}/messages"

# Database connection details

# OAuth Scopes for Microsoft Graph API
SCOPES = ["https://graph.microsoft.com/.default"]

# Email for fetching messages
USER_EMAIL = os.getenv("USER_EMAIL")
