"""
Gmail Watcher for Silver Tier AI Employee
Monitors Gmail for priority emails and creates tasks
"""
import os
import base64
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
import json

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str, token_path: str):
        super().__init__(vault_path, check_interval=120)
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self.authenticate_gmail()
        self.processed_ids = set()
        self.load_processed_ids()

        # Priority keywords
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'important', 'deadline']

    def authenticate_gmail(self):
        creds = None
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def load_processed_ids(self):
        processed_file = self.vault_path / 'Config' / 'gmail_processed.json'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                self.processed_ids = set(json.load(f))

    def save_processed_ids(self):
        processed_file = self.vault_path / 'Config' / 'gmail_processed.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def check_for_updates(self) -> list:
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for msg in messages:
                msg_id = msg['id']
                if msg_id not in self.processed_ids:
                    # Get full message
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg_id,
                        format='full'
                    ).execute()

                    # Check if priority
                    if self.is_priority_email(message):
                        new_messages.append(message)
                        self.processed_ids.add(msg_id)

            self.save_processed_ids()
            return new_messages

        except Exception as e:
            self.logger.error(f"Gmail API error: {e}")
            return []

    def is_priority_email(self, message):
        """Check if email contains priority keywords"""
        headers = {h['name'].lower(): h['value'] for h in message['payload']['headers']}
        subject = headers.get('subject', '').lower()
        from_email = headers.get('from', '').lower()

        # Check subject and sender
        for keyword in self.priority_keywords:
            if keyword in subject:
                return True

        # Important senders (clients, boss, etc.)
        important_senders = ['client', 'boss', 'ceo', 'manager', 'urgent']
        for sender in important_senders:
            if sender in from_email:
                return True

        return False

    def create_action_file(self, message) -> str:
        headers = {h['name']: h['value'] for h in message['payload']['headers']}

        # Extract email body
        body = self.get_email_body(message)

        # Create task file
        task_id = f"EMAIL_{message['id']}_{int(datetime.now().timestamp())}"
        task_file = self.needs_action / f"{task_id}.md"

        content = f"""---
type: email
message_id: {message['id']}
from: {headers.get('From', 'Unknown')}
to: {headers.get('To', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
date: {headers.get('Date', datetime.now().isoformat())}
priority: high
status: pending
thread_id: {message.get('threadId', '')}
---

# 📧 New Email Detected

## Email Details
- **From**: {headers.get('From', 'Unknown')}
- **To**: {headers.get('To', 'Unknown')}
- **Subject**: {headers.get('Subject', 'No Subject')}
- **Date**: {headers.get('Date', 'Unknown')}
- **Priority**: High (Contains keywords)

## Email Content
{body[:1000]}{'...' if len(body) > 1000 else ''}

## Suggested Actions
- [ ] Draft reply
- [ ] Forward to team
- [ ] Add to calendar
- [ ] Create task from email
- [ ] Mark as done and archive

## Processing Instructions
1. Analyze email content
2. Determine urgency
3. Draft appropriate response
4. Create approval request if needed
"""

        task_file.write_text(content)
        self.logger.info(f"Created Gmail task: {task_file.name}")
        return str(task_file)

    def get_email_body(self, message):
        """Extract email body from message"""
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = message['payload']['body'].get('data', '')
                return base64.urlsafe_b64decode(data).decode('utf-8')
        except:
            return "Could not decode email body"

        return "No body content"

def start_gmail_watcher(vault_path, credentials_file, token_file):
    """Start Gmail watcher"""
    watcher = GmailWatcher(vault_path, credentials_file, token_file)
    print("Gmail Watcher started")
    print(f"   Monitoring for priority emails")
    print(f"   Check interval: {watcher.check_interval} seconds")
    # watcher.run()  # Commented out for testing purposes

if __name__ == "__main__":
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    CREDENTIALS_FILE = "credentials.json"  # Update with actual path
    TOKEN_FILE = "token.pickle"  # Update with actual path

    start_gmail_watcher(VAULT_PATH, CREDENTIALS_FILE, TOKEN_FILE)