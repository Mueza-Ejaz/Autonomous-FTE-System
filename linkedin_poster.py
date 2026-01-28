"""
LinkedIn Poster for Silver Tier AI Employee
Automatically posts business updates to LinkedIn
"""
import os
import schedule
import time
from datetime import datetime
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

class LinkedInPoster:
    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # LinkedIn credentials (use environment variables)
        self.username = os.getenv('LINKEDIN_EMAIL', '')
        self.password = os.getenv('LINKEDIN_PASSWORD', '')

        # Posting schedule
        self.post_times = ["09:00", "12:00", "17:00"]  # 9 AM, 12 PM, 5 PM

        # Post templates
        self.templates = self.load_templates()

    def load_templates(self):
        """Load LinkedIn post templates"""
        templates_file = self.vault_path / 'Config' / 'linkedin_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                return json.load(f)

        # Default templates
        return {
            "business_update": [
                "🚀 Just completed an amazing project! Learning so much about AI automation.",
                "📈 Excited to share our latest milestone in building autonomous AI employees!",
                "💡 Tip of the day: Automate one repetitive task this week. What will you automate?"
            ],
            "project_showcase": [
                "Building something incredible! Our AI Employee project is taking shape.",
                "From concept to reality: How we're automating business processes with AI."
            ],
            "learning_share": [
                "Just learned something new about Claude Code and MCP servers!",
                "The future of work is AI-assisted. Here's what we're building..."
            ]
        }

    def generate_post(self):
        """Generate a post using Claude or templates"""
        import random

        # For now, use random template
        template_type = random.choice(list(self.templates.keys()))
        post = random.choice(self.templates[template_type])

        # Add hashtags
        hashtags = ["#AI", "#Automation", "#ClaudeCode", "#AIEmployee", "#Tech"]
        post += "\n\n" + " ".join(hashtags[:3])

        return post

    def post_to_linkedin(self, content):
        """Post content to LinkedIn"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Set to True after testing
                    args=['--disable-blink-features=AutomationControlled']
                )

                page = browser.new_page()
                page.goto('https://www.linkedin.com')

                # Check if already logged in
                if "feed" not in page.url:
                    # Login
                    page.fill('#username', self.username)
                    page.fill('#password', self.password)
                    page.click('button[type="submit"]')
                    page.wait_for_url("**/feed/**", timeout=10000)

                # Go to create post
                page.click('button[aria-label*="Start a post"]')
                time.sleep(2)

                # Type post content
                post_box = page.locator('.ql-editor')
                post_box.click()
                post_box.fill(content)
                time.sleep(1)

                # For now, just save as draft (safety)
                # In production, you'd click post
                page.click('button[aria-label="Save as draft"]')

                # Log the action
                self.log_post(content, "draft")

                browser.close()
                return True

        except Exception as e:
            print(f"LinkedIn posting error: {e}")
            self.log_post(content, f"failed: {str(e)}")
            return False

    def log_post(self, content, status):
        """Log posting activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'content': content[:100] + "..." if len(content) > 100 else content,
            'status': status,
            'type': 'linkedin_post'
        }

        log_file = self.vault_path / 'Logs' / 'linkedin_posts.json'
        logs = []

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def run_scheduled(self):
        """Run scheduled posting"""
        print("📅 LinkedIn Poster Scheduled")

        # Schedule posts
        for post_time in self.post_times:
            schedule.every().day.at(post_time).do(self.scheduled_post)
            print(f"   Scheduled post at: {post_time}")

        # Run immediately for testing
        self.scheduled_post()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

    def scheduled_post(self):
        """Execute scheduled post"""
        print(f"[{datetime.now().strftime('%H:%M')}] Generating LinkedIn post...")

        # Generate post
        post_content = self.generate_post()

        # Post to LinkedIn
        success = self.post_to_linkedin(post_content)

        if success:
            print("✅ LinkedIn post created (saved as draft)")
        else:
            print("❌ LinkedIn post failed")

        # Update dashboard
        self.update_dashboard(post_content, success)

    def update_dashboard(self, content, success):
        """Update dashboard with LinkedIn activity"""
        dashboard = self.vault_path / 'Dashboard.md'
        if dashboard.exists():
            dash_content = dashboard.read_text()

            # Add LinkedIn update
            update_section = f"\n## 📱 LinkedIn Update\n"
            update_section += f"- **Time**: {datetime.now().strftime('%H:%M')}\n"
            update_section += f"- **Status**: {'✅ Draft created' if success else '❌ Failed'}\n"
            update_section += f"- **Content**: {content[:50]}...\n"

            # Append to dashboard
            if "LinkedIn Update" not in dash_content:
                dash_content = dash_content.replace("## Quick Stats", update_section + "\n## Quick Stats")
                dashboard.write_text(dash_content)

def start_linkedin_poster(vault_path, session_path):
    """Start LinkedIn poster"""
    poster = LinkedInPoster(vault_path, session_path)
    print("🔗 LinkedIn Poster started")
    print(f"   Scheduled times: {', '.join(poster.post_times)}")
    poster.run_scheduled()

if __name__ == "__main__":
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    SESSION_PATH = "linkedin_session"

    start_linkedin_poster(VAULT_PATH, SESSION_PATH)