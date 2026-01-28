"""
Email MCP Server for Silver Tier AI Employee
Handles email sending via SMTP with approval workflow
"""
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime
import asyncio

class EmailMCPServer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')

    async def send_email(self, to, subject, body, attachment_path=None):
        """Send email via SMTP"""
        try:
            # Check if dry run
            if os.getenv('DRY_RUN', 'true').lower() == 'true':
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[DRY RUN] Would send email to {to}\nSubject: {subject}\nBody: {body[:100]}..."
                    }]
                }

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=Path(attachment_path).name)
                part['Content-Disposition'] = f'attachment; filename="{Path(attachment_path).name}"'
                msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            # Log the action
            self.log_email_action('sent', to, subject)

            return {
                "content": [{
                    "type": "text",
                    "text": f"✅ Email sent successfully to {to}"
                }]
            }

        except Exception as e:
            error_msg = f"❌ Failed to send email: {str(e)}"
            self.log_email_action('failed', to, subject, str(e))
            return {
                "content": [{
                    "type": "text",
                    "text": error_msg
                }]
            }

    async def draft_email(self, to, subject, body, reason="Business communication"):
        """Create email draft for approval"""
        draft_id = f"EMAIL_DRAFT_{int(asyncio.get_event_loop().time())}"
        draft_file = self.vault_path / 'Pending_Approval' / f'{draft_id}.md'

        content = f"""---
type: email_draft
draft_id: {draft_id}
to: {to}
subject: {subject}
reason: {reason}
created: {datetime.now().isoformat()}
status: pending_approval
requires_approval: yes
---

# ✉️ Email Draft - Approval Required

## Email Details
- **To**: {to}
- **Subject**: {subject}
- **Reason**: {reason}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Email Body
{body}

## To Approve
Move this file to `/Approved/` folder to send.

## To Reject
Move this file to `/Rejected/` folder.

## To Edit
Edit this file and save, then move to `/Pending_Approval/` again.
"""

        draft_file.write_text(content)

        return {
            "content": [{
                "type": "text",
                "text": f"📝 Email draft created: {draft_file.name}\nMove to /Approved/ to send."
            }]
        }

    async def check_settings(self):
        """Check email configuration"""
        config_ok = all([
            self.email_user,
            self.email_password,
            self.smtp_server
        ])

        return {
            "content": [{
                "type": "text",
                "text": f"📧 Email Configuration:\n"
                       f"- User: {'✅ Set' if self.email_user else '❌ Missing'}\n"
                       f"- SMTP Server: {self.smtp_server}:{self.smtp_port}\n"
                       f"- Configuration: {'✅ Complete' if config_ok else '❌ Incomplete'}"
            }]
        }

    def log_email_action(self, action, to, subject, error=None):
        """Log email actions"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'to': to,
            'subject': subject,
            'error': error
        }

        log_file = self.vault_path / 'Logs' / 'email_actions.json'
        logs = []

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

def start_email_mcp_server(vault_path):
    """Start email MCP server"""
    server = EmailMCPServer(vault_path)
    print("Email MCP Server started")
    print(f"   SMTP: {server.smtp_server}:{server.smtp_port}")
    # Note: Actual MCP server would run with proper MCP protocol here
    return server

if __name__ == "__main__":
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    server = start_email_mcp_server(VAULT_PATH)
    print("Email MCP Server initialized and ready to handle requests")