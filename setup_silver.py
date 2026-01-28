"""
Silver Tier Setup Script
Run this after Bronze is complete
"""
import os
import sys
import json
from pathlib import Path

def setup_silver_tier():
    print("=" * 60)
    print("UPGRADING TO SILVER TIER")
    print("=" * 60)

    vault_path = Path("D:/Autonomous-FTE-System/AI_Employee_Vault")

    # 1. Create Silver configuration
    print("\n1. Creating Silver configuration...")
    config_file = vault_path / 'Config' / 'silver_config.json'
    if not config_file.exists():
        config_file.write_text(json.dumps({
            "version": "2.0",
            "tier": "silver"
        }, indent=2))
        print(f"   Created: {config_file}")
    else:
        print(f"   Config already exists: {config_file}")

    # 2. Create additional directories
    print("\n2. Creating Silver directories...")
    silver_dirs = [
        'Social_Media',
        'Email_Drafts',
        'Client_Communications',
        'Business_Reports',
        'Scheduled_Tasks',
        'In_Progress'
    ]

    for dir_name in silver_dirs:
        (vault_path / dir_name).mkdir(exist_ok=True)
        print(f"   Created: {dir_name}/")

    # 3. Create LinkedIn templates
    print("\n3. Creating LinkedIn templates...")
    templates = {
        "business_update": [
            "Just completed an amazing project! Learning so much about AI automation.",
            "Excited to share our latest milestone in building autonomous AI employees!",
            "Tip of the day: Automate one repetitive task this week. What will you automate?"
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

    templates_file = vault_path / 'Config' / 'linkedin_templates.json'
    if not templates_file.exists():
        templates_file.write_text(json.dumps(templates, indent=2))
        print(f"   Created: {templates_file}")
    else:
        print(f"   Templates already exist: {templates_file}")

    # 4. Update .env file for Silver
    print("\n4. Updating environment variables...")
    env_file = Path("D:/Autonomous-FTE-System/.env")
    if env_file.exists():
        env_content = env_file.read_text()

        # Add Silver-specific variables
        silver_vars = """

# SILVER TIER CONFIGURATION
# Gmail API
GMAIL_CREDENTIALS=credentials.json
GMAIL_TOKEN_PATH=D:/Autonomous-FTE-System/AI_Employee_Vault/Config/gmail_token.pickle

# WhatsApp
WHATSAPP_SESSION_PATH=D:/Autonomous-FTE-System/AI_Employee_Vault/Config/whatsapp_session

# LinkedIn
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password_here

# Email SMTP
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
"""

        if "# SILVER TIER CONFIGURATION" not in env_content:
            env_file.write_text(env_content + silver_vars)
            print("   Added Silver tier variables")
        else:
            print("   Silver variables already exist")

    # 5. Create setup instructions
    print("\n5. Creating setup instructions...")
    readme_file = vault_path / 'README_SILVER.md'
    readme_content = """# SILVER TIER SETUP GUIDE

## New Features Added:
**3 Watchers**: Filesystem + Gmail + WhatsApp
**Email MCP Server**: Send/draft emails
**LinkedIn Automation**: Scheduled posting
**Enhanced Scheduling**: Daily briefing, automated tasks
**Multi-platform Communication**: Email, WhatsApp, LinkedIn

## Setup Steps:

### 1. Gmail API Setup:
1. Go to https://console.cloud.google.com
2. Create project → Enable Gmail API
3. Create OAuth 2.0 credentials → Download credentials.json
4. Place in project root as `credentials.json`

### 2. WhatsApp Setup:
1. Install Playwright: `playwright install chromium`
2. First run will require WhatsApp Web login
3. Session will be saved automatically

### 3. LinkedIn Setup:
1. Add LinkedIn credentials to .env file
2. First run will require login
3. Posts will be saved as drafts initially

### 4. Email SMTP Setup:
1. Enable 2FA on your Gmail
2. Generate App Password
3. Add to .env file

## Running Silver Tier:
```bash
# Start Silver orchestrator
python orchestrator_silver.py

# Or start individual components:
python gmail_watcher.py
python whatsapp_watcher.py
python linkedin_poster.py
python email_mcp_server.py
```

## Testing:
- Send test email to yourself
- Send WhatsApp message with "invoice" keyword
- Drop file in Drop_Folder
- Check LinkedIn drafts

## Security Notes:
- All sensitive actions require approval
- Dry run mode enabled by default
- All actions logged
- API keys in .env (never commit)
"""

    readme_file.write_text(readme_content)
    print(f"   Created: {readme_file}")

    # 6. Final message
    print("\n" + "=" * 60)
    print("SILVER TIER UPGRADE COMPLETE!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Update .env file with your credentials")
    print("2. Run: python orchestrator_silver.py")
    print("3. Test all watchers individually")
    print("4. Check Dashboard.md for status")
    print("\nBranch: P2-Silver-Tier")
    print("All code is in Silver branch, ready for testing.")

if __name__ == "__main__":
    setup_silver_tier()