import requests
from auth_token import get_access_token
import config
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse
import re

def fetch_paginated_results(url, headers, max_results=30):
    all_results = []
    while url:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            print(f"API error ({response.status_code}): {error_msg}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []

        data = response.json()
        results = data.get("value", [])
        all_results.extend(results)

        if len(all_results) >= max_results:
            print(f"Reached max results limit ({max_results}) — stopping pagination.")
            break

        url = data.get("@odata.nextLink")

    return all_results

def fetch_user_emails(user_upn):
    access_token = get_access_token()
    url = f"{config.GRAPH_API_ENDPOINT}/users/{user_upn}/messages"
    headers = {"Authorization": f"Bearer {access_token}"}
    return fetch_paginated_results(url, headers, max_results=30)

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for tag in soup.find_all(True):
        tag.attrs = {}
    text = soup.get_text(separator="\n")
    text = re.sub(r'\n+', '\n', text).strip()
    return text

def extract_emails(user_upn):
    emails = fetch_user_emails(user_upn)
    processed_emails = []

    for email in emails:
        email_id = email.get("id", "N/A")
        conversation_id = email.get("conversationId", "N/A")
        sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")

        to_recipients_list = [
            recipient["emailAddress"]["address"].lower()
            for recipient in email.get("toRecipients", []) if "emailAddress" in recipient
        ]
        to_recipients = ", ".join(to_recipients_list) or "N/A"

        if user_upn.lower() not in to_recipients_list and sender.lower() != user_upn.lower():
            continue

        reply_to = ", ".join([
            r["emailAddress"]["address"] for r in email.get("replyTo", []) if "emailAddress" in r
        ]) or sender

        in_reply_to = email.get("inReplyTo", "N/A")
        subject = email.get("subject", "No Subject")
        body = html_to_text(email.get("body", {}).get("content", "No Content"))

        def parse_timestamp(timestamp):
            if not timestamp:
                return "N/A"
            try:
                return parse(timestamp).isoformat()
            except:
                return "Invalid Timestamp"

        received_at = parse_timestamp(email.get("receivedDateTime"))
        sent_at = parse_timestamp(email.get("sentDateTime"))

        processed_emails.append({
            "email_id": email_id,
            "conversation_id": conversation_id,
            "from": sender,
            "to": to_recipients,
            "reply_to": reply_to,
            "in_reply_to": in_reply_to,
            "subject": subject,
            "full_body": body,
            "received_at": received_at,
            "sent_at": sent_at,
            "date_extracted": datetime.utcnow().isoformat()
        })

    return processed_emails