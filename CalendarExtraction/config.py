import os

# Outlook API credentials
OUTLOOK_CLIENT_ID = os.getenv("CLIENT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OUTLOOK_TENANT_ID = os.getenv("TENANT_ID")

# Microsoft Graph API endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

# Database connection details

# OAuth Scopes for Microsoft Graph API
SCOPES = ["https://graph.microsoft.com/.default"]

# Upn for fetching messages
USER_UPN = os.getenv("USER_UPN")