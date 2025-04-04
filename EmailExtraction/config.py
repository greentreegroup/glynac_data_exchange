import os

# Outlook API credentials
OUTLOOK_CLIENT_ID = os.getenv("CLIENT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Tenant ID for Microsoft Azure
TENANT_ID = os.getenv("TENANT_ID")

# Database connection details
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Microsoft Graph API endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

# OAuth Scopes for Microsoft Graph API
SCOPES = ["https://graph.microsoft.com/.default"]