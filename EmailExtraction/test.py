from datetime import datetime

mock_api_response = [
    {
        "Email ID": "email_001",
        "Subject": "Project Kickoff",
        "From": "john.doe@company.com",
        "To": "jane.smith@company.com",
        "Reply-To": "john.doe@company.com",
        "Conversation ID": "conv_001",
        "Received At": "2025-03-12T09:30:00Z",
        "Sent At": "2025-03-12T09:28:00Z",
        "Date Extracted": datetime.utcnow().isoformat(),
        "Body": "Excited to kick off the new project today!",
        "InReplyTo": None  # No previous message
    },
    {
        "Email ID": "email_002",
        "Subject": "Re: Project Kickoff",
        "From": "jane.smith@company.com",
        "To": "john.doe@company.com",
        "Reply-To": "jane.smith@company.com",
        "Conversation ID": "conv_001",
        "Received At": "2025-03-12T09:45:00Z",
        "Sent At": "2025-03-12T09:43:00Z",
        "Date Extracted": datetime.utcnow().isoformat(),
        "Body": "Thanks for the update! Looking forward to it.",
        "InReplyTo": "email_001"  # Replying to first email
    },
    {
        "Email ID": "email_003",
        "Subject": "Re: Project Kickoff",
        "From": "john.doe@company.com",
        "To": "jane.smith@company.com",
        "Reply-To": "john.doe@company.com",
        "Conversation ID": "conv_001",
        "Received At": "2025-03-12T10:00:00Z",
        "Sent At": "2025-03-12T09:58:00Z",
        "Date Extracted": datetime.utcnow().isoformat(),
        "Body": "Great! Let's schedule a call this afternoon.",
        "InReplyTo": "email_002"  # Replying to second email
    },
    {
        "Email ID": "email_004",
        "Subject": "Team Meeting Invitation",
        "From": "hr@company.com",
        "To": "jane.smith@company.com",
        "Reply-To": "hr@company.com",
        "Conversation ID": "conv_002",
        "Received At": "2025-03-12T11:15:00Z",
        "Sent At": "2025-03-12T11:10:00Z",
        "Date Extracted": datetime.utcnow().isoformat(),
        "Body": "You're invited to a team meeting on Friday at 2 PM.",
        "InReplyTo": None  # New email, not a reply
    },
    {
        "Email ID": "email_005",
        "Subject": "Reminder: Weekly Check-In",
        "From": "teamlead@company.com",
        "To": "john.doe@company.com",
        "Reply-To": "teamlead@company.com",
        "Conversation ID": "conv_003",
        "Received At": "2025-03-12T14:00:00Z",
        "Sent At": "2025-03-12T13:55:00Z",
        "Date Extracted": datetime.utcnow().isoformat(),
        "Body": "Just a reminder about our weekly check-in meeting.",
        "InReplyTo": None  # New email, not a reply
    }
]
