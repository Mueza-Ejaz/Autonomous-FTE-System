"""
WhatsApp Watcher for Silver Tier AI Employee
Monitors WhatsApp for business-related messages and creates tasks
"""
import os
import json
import time
from pathlib import Path
from base_watcher import BaseWatcher
from playwright.sync_api import sync_playwright
import re

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=45)
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Business keywords to watch for
        self.business_keywords = [
            'invoice', 'payment', 'order', 'quote', 'price', 'urgent',
            'meeting', 'deadline', 'project', 'delivery', 'client',
            'asap', 'important', 'issue', 'problem', 'help'
        ]

        # Priority contacts (add your contacts)
        self.priority_contacts = [
            'client', 'boss', 'manager', 'team', 'customer'
        ]

        self.processed_messages = self.load_processed()

    def load_processed(self):
        processed_file = self.vault_path / 'Config' / 'whatsapp_processed.json'
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                return set(json.load(f))
        return set()

    def save_processed(self, msg_id):
        self.processed_messages.add(msg_id)
        processed_file = self.vault_path / 'Config' / 'whatsapp_processed.json'
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_messages), f)

    def check_for_updates(self) -> list:
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com')

                # Wait for WhatsApp Web to load
                page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)
                time.sleep(5)

                # Find unread messages
                new_messages = []

                # Look for unread chats
                unread_chats = page.query_selector_all('[data-testid*="unread"]')

                for chat in unread_chats:
                    try:
                        # Get chat name and last message
                        chat.click()
                        time.sleep(1)

                        # Get contact name
                        contact_elem = page.query_selector('header span[dir="auto"]')
                        contact_name = contact_elem.inner_text() if contact_elem else "Unknown"

                        # Get last messages
                        messages = page.query_selector_all('.message-in, .message-out')
                        if messages:
                            last_msg = messages[-1]
                            msg_text = last_msg.inner_text().lower()
                            msg_time = datetime.now().isoformat()

                            # Generate unique ID
                            msg_id = f"WA_{contact_name}_{int(time.time())}"

                            if msg_id not in self.processed_messages:
                                # Check if message is business-related
                                if self.is_business_message(msg_text, contact_name):
                                    new_messages.append({
                                        'id': msg_id,
                                        'contact': contact_name,
                                        'text': msg_text,
                                        'time': msg_time,
                                        'full_text': last_msg.inner_text()
                                    })
                                    self.save_processed(msg_id)
                    except Exception as e:
                        self.logger.error(f"Error processing chat: {e}")
                        continue

                browser.close()
                return new_messages

        except Exception as e:
            self.logger.error(f"WhatsApp watcher error: {e}")
            return []

    def is_business_message(self, text, contact):
        """Check if message is business-related"""
        text_lower = text.lower()
        contact_lower = contact.lower()

        # Check keywords
        for keyword in self.business_keywords:
            if keyword in text_lower:
                return True

        # Check priority contacts
        for priority in self.priority_contacts:
            if priority in contact_lower:
                return True

        # Check for numbers (might be prices, invoice numbers)
        if re.search(r'\$\d+|\d+\$|rs\.?\s*\d+|invoice\s*#?\d+', text_lower):
            return True

        return False

    def create_action_file(self, message) -> str:
        task_id = f"WHATSAPP_{message['id']}"
        task_file = self.needs_action / f"{task_id}.md"

        content = f"""---
type: whatsapp
message_id: {message['id']}
contact: {message['contact']}
time: {message['time']}
priority: high
status: pending
platform: whatsapp
---

# 📱 WhatsApp Business Message

## Message Details
- **Contact**: {message['contact']}
- **Time**: {message['time']}
- **Platform**: WhatsApp
- **Priority**: High (Business-related)

## Message Content
{message['full_text']}

## Keywords Detected
{self.extract_keywords(message['text'])}

## Suggested Actions
- [ ] Reply to message
- [ ] Create invoice if requested
- [ ] Schedule meeting
- [ ] Add to customer database
- [ ] Follow up via email

## Processing Instructions
1. Analyze message intent
2. Draft appropriate response
3. Check if payment/invoice needed
4. Create approval request for response
"""

        task_file.write_text(content)
        self.logger.info(f"Created WhatsApp task: {task_file.name}")
        return str(task_file)

    def extract_keywords(self, text):
        found = []
        for keyword in self.business_keywords:
            if keyword in text.lower():
                found.append(keyword)
        return ", ".join(found) if found else "None detected"

def start_whatsapp_watcher(vault_path, session_path):
    """Start WhatsApp watcher"""
    watcher = WhatsAppWatcher(vault_path, session_path)
    print("WhatsApp Watcher started")
    print(f"   Monitoring for business messages")
    print(f"   Check interval: {watcher.check_interval} seconds")
    # watcher.run()  # Commented out for testing purposes

if __name__ == "__main__":
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    SESSION_PATH = "whatsapp_session"

    start_whatsapp_watcher(VAULT_PATH, SESSION_PATH)