Personal AI Employee Hackathon - Bronze Tier Implementation Guide
Project Context & Goal
You are my personal AI assistant helping me build a Bronze Tier Autonomous AI Employee as per the "Personal AI Employee Hackathon" documentation. This is Phase 1 (P1) of the project. Please create a branch named P1-Bronze-Tier and work exclusively in this branch. I will merge it to main later.

COMPLETE IMPLEMENTATION PLAN FOR BRONZE TIER
Step 1: Project Setup & Initialization
1. Create and switch to new branch: `P1-Bronze-Tier`
2. Initialize project structure in D:\Autonomous-FTE-System\
3. Create Obsidian vault: "AI_Employee_Vault"
4. Verify Claude CLI installation and setup

Step 2: Core Directory Structure
Create these folders in the vault:
/AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Needs_Action/
├── Plans/
├── Approved/
├── Rejected/
├── Pending_Approval/
├── Done/
├── Logs/
├── Skills/          # For storing Agent Skills
└── Config/

Step 3: Essential Configuration Files
Create Company_Handbook.md:

---
type: handbook
version: 1.0
created: 2026-01-07
---

# Company Rules of Engagement

## Communication Rules
1. Always be polite in all communications
2. Use formal language for business emails
3. Flag any payment request over $500 for approval
4. Never share sensitive information without approval

## Business Hours
- Primary: 9 AM - 6 PM
- Emergency: 24/7 for urgent matters

## Approval Thresholds
- Payments: > $500
- Email replies to new clients: Always
- Social media posts: Always
- File deletions: Always

Create Dashboard.md:
---
type: dashboard
last_updated: 2026-01-07
status: active
---

# AI Employee Dashboard

## System Status
- ✅ Claude Code: Running
- ✅ Obsidian Vault: Active
- 🔄 Watchers: Starting

## Recent Activities
- No activities yet

## Pending Actions
- No pending actions

## Quick Stats
- Tasks Processed: 0
- Approvals Needed: 0
- Errors: 0

Step 4: Create File System Watcher (First Watcher)
Create filesystem_watcher.py:
"""
Bronze Tier - File System Watcher
Watches a folder for new files and creates tasks
"""
import os
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileDropHandler(FileSystemEventHandler):
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(exist_ok=True)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('FileWatcher')
    
    def on_created(self, event):
        if not event.is_directory:
            source = Path(event.src_path)
            if source.suffix in ['.txt', '.pdf', '.doc', '.docx', '.md']:
                # Create task file
                task_id = f"FILE_{int(time.time())}_{source.name}"
                task_file = self.needs_action / f"{task_id}.md"
                
                content = f"""---
type: file_drop
original_name: {source.name}
source_path: {str(source)}
size: {source.stat().st_size} bytes
detected: {time.strftime('%Y-%m-%d %H:%M:%S')}
priority: medium
status: pending
---

# New File Detected: {source.name}

## File Information
- **Name**: {source.name}
- **Type**: {source.suffix}
- **Size**: {source.stat().st_size} bytes
- **Location**: {str(source)}

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file
- [ ] Move to appropriate folder
- [ ] Notify user about file

## Processing Instructions
1. Read the file content
2. Determine what type of file it is
3. Decide appropriate action
4. Create a plan in /Plans/ folder
"""
                task_file.write_text(content)
                self.logger.info(f"Created task for new file: {source.name}")
                
                # Copy file to vault for processing
                vault_copy = self.needs_action / source.name
                shutil.copy2(source, vault_copy)

def start_file_watcher(vault_path, watch_folder):
    """Start watching a folder for new files"""
    event_handler = FileDropHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    
    try:
        print(f"📁 File Watcher started. Monitoring: {watch_folder}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Configure these paths
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    WATCH_FOLDER = "D:/Autonomous-FTE-System/Drop_Folder"
    
    # Create watch folder if it doesn't exist
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    
    print("Starting File System Watcher...")
    print(f"Vault: {VAULT_PATH}")
    print(f"Watch Folder: {WATCH_FOLDER}")
    print("Drop files in the watch folder to trigger tasks.")
    
    start_file_watcher(VAULT_PATH, WATCH_FOLDER)

Step 5: Create Orchestrator Script
Create orchestrator.py:
"""
Bronze Tier - Main Orchestrator
Coordinates between watchers, Claude, and MCP servers
"""
import os
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

class BronzeOrchestrator:
    def __init__(self, vault_path):
        self.vault = Path(vault_path)
        self.setup_directories()
        self.load_config()
        
    def setup_directories(self):
        """Ensure all required directories exist"""
        dirs = ['Needs_Action', 'Plans', 'Approved', 'Rejected', 
                'Pending_Approval', 'Done', 'Logs']
        for dir_name in dirs:
            (self.vault / dir_name).mkdir(exist_ok=True)
    
    def load_config(self):
        """Load configuration"""
        config_file = self.vault / 'Config' / 'system_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "claude_path": "claude",
                "check_interval": 60,
                "max_iterations": 5,
                "dry_run": True
            }
    
    def check_needs_action(self):
        """Check for new items in Needs_Action"""
        needs_action = self.vault / 'Needs_Action'
        items = list(needs_action.glob('*.md'))
        return items
    
    def process_with_claude(self, task_file):
        """Process a task using Claude Code"""
        try:
            # Create a prompt for Claude
            prompt = self.create_claude_prompt(task_file)
            
            # Run Claude Code
            cmd = [
                self.config['claude_path'],
                "process-task",
                "--prompt", prompt,
                "--vault", str(self.vault),
                "--output", str(self.vault / 'Plans' / f'plan_{task_file.stem}.md')
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log the result
            self.log_action({
                'timestamp': datetime.now().isoformat(),
                'action': 'claude_processing',
                'task': task_file.name,
                'success': result.returncode == 0,
                'output': result.stdout[:500]  # First 500 chars
            })
            
            return result.returncode == 0
            
        except Exception as e:
            self.log_error(f"Claude processing failed: {e}")
            return False
    
    def create_claude_prompt(self, task_file):
        """Create prompt for Claude based on task file"""
        content = task_file.read_text()
        
        prompt = f"""You are my AI Employee (Bronze Tier). Process this task:

{content}

## Instructions:
1. Read the task carefully
2. Create a step-by-step plan in /Plans/ folder
3. If action is needed, create approval request in /Pending_Approval/
4. Update Dashboard.md with status
5. Use appropriate skills if needed

## Available Skills (from D:\Autonomous-FTE-System\.claude\skills):
- file_processor: Read/write files
- text_analyzer: Analyze text content
- task_planner: Create task plans
- email_drafter: Draft email responses
- data_extractor: Extract data from files

## Rules from Company_Handbook.md:
- Always be professional
- Flag payments over $500
- Get approval for external communications

Create a detailed plan now."""
        return prompt
    
    def log_action(self, data):
        """Log actions to JSON log file"""
        log_dir = self.vault / 'Logs'
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'{today}.json'
        
        # Read existing logs or create new
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(data)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def log_error(self, message):
        """Log error messages"""
        error_log = self.vault / 'Logs' / 'errors.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(error_log, 'a') as f:
            f.write(f"[{timestamp}] ERROR: {message}\n")
    
    def update_dashboard(self):
        """Update the main dashboard"""
        dashboard = self.vault / 'Dashboard.md'
        
        # Count tasks
        needs_action = len(list((self.vault / 'Needs_Action').glob('*.md')))
        pending = len(list((self.vault / 'Pending_Approval').glob('*.md')))
        done = len(list((self.vault / 'Done').glob('*.md')))
        
        content = f"""---
type: dashboard
last_updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: active
---

# AI Employee Dashboard (Bronze Tier)

## System Status
- ✅ Claude Code: Running
- ✅ Obsidian Vault: Active
- 🔄 File Watcher: Monitoring
- 📊 Orchestrator: Active

## Task Summary
- **Needs Action**: {needs_action}
- **Pending Approval**: {pending}
- **Completed Tasks**: {done}

## Recent Activities
{self.get_recent_activities()}

## Quick Stats
- Tasks Processed: {done}
- Approvals Needed: {pending}
- System Uptime: {self.get_uptime()}

---
*Last updated automatically by AI Employee*
"""
        dashboard.write_text(content)
    
    def get_recent_activities(self):
        """Get recent activities from logs"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = self.vault / 'Logs' / f'{today}.json'
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                
                # Get last 5 activities
                recent = logs[-5:] if len(logs) > 5 else logs
                activities = []
                
                for log in recent:
                    timestamp = log.get('timestamp', '')
                    action = log.get('action', '')
                    activities.append(f"- {timestamp}: {action}")
                
                return '\n'.join(activities)
        except:
            pass
        
        return "- No activities logged yet"
    
    def get_uptime(self):
        """Calculate system uptime"""
        start_time = getattr(self, '_start_time', datetime.now())
        uptime = datetime.now() - start_time
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def run(self):
        """Main orchestration loop"""
        print("🚀 Starting Bronze Tier Orchestrator")
        print(f"📂 Vault: {self.vault}")
        print("⏰ Check interval: 60 seconds")
        print("=" * 50)
        
        self._start_time = datetime.now()
        
        try:
            while True:
                # Check for new tasks
                tasks = self.check_needs_action()
                
                if tasks:
                    print(f"📋 Found {len(tasks)} task(s) to process")
                    
                    for task in tasks:
                        print(f"  Processing: {task.name}")
                        success = self.process_with_claude(task)
                        
                        if success:
                            # Move to Done folder
                            done_file = self.vault / 'Done' / task.name
                            task.rename(done_file)
                            print(f"  ✅ Moved to Done: {task.name}")
                
                # Update dashboard
                self.update_dashboard()
                
                # Wait before next check
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            print("\n🛑 Orchestrator stopped by user")
        except Exception as e:
            print(f"❌ Error in orchestrator: {e}")
            self.log_error(f"Orchestrator crashed: {e}")

if __name__ == "__main__":
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    orchestrator = BronzeOrchestrator(VAULT_PATH)
    orchestrator.run()

Step 6: Create Installation & Setup Script
Create setup_bronze.py:
"""
Bronze Tier Setup Script
Run this first to set up the environment
"""
import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    checks = [
        ("Python 3.13+", "python --version"),
        ("Node.js v24+", "node --version"),
        ("Git", "git --version"),
        ("Claude CLI", "claude --version")
    ]
    
    all_ok = True
    for name, cmd in checks:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {name}: {result.stdout.strip()}")
            else:
                print(f"  ❌ {name}: Not found")
                all_ok = False
        except:
            print(f"  ❌ {name}: Not found")
            all_ok = False
    
    return all_ok

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    packages = [
        "watchdog",
        "python-dotenv",
        "playwright"
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    # Install Playwright browsers
    print("  Installing Playwright browsers...")
    subprocess.run([sys.executable, "-m", "playwright", "install"])

def setup_vault():
    """Set up the Obsidian vault structure"""
    print("🏗️ Setting up vault structure...")
    
    vault_path = Path("D:/Autonomous-FTE-System/AI_Employee_Vault")
    
    # Create main directories
    dirs = [
        vault_path,
        vault_path / "Config",
        vault_path / "Skills",
        vault_path / "Drop_Folder",  # For file watcher
        vault_path / "MCP_Servers"
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")
    
    # Create .gitignore
    gitignore = vault_path / ".gitignore"
    gitignore.write_text("""
# Secrets
.env
*.key
*.pem
credentials.json
token.json

# System files
.DS_Store
Thumbs.db
__pycache__/
*.pyc

# Logs
logs/
*.log

# Temporary files
temp/
tmp/
    """)
    
    print("  Created .gitignore")

def create_environment_file():
    """Create .env file template"""
    print("🔐 Creating environment template...")
    
    env_template = """# AI Employee Configuration
# NEVER commit this file to Git!

# Claude Configuration
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet

# Paths
VAULT_PATH=D:/Autonomous-FTE-System/AI_Employee_Vault
DROP_FOLDER=D:/Autonomous-FTE-System/AI_Employee_Vault/Drop_Folder

# System Settings
DRY_RUN=true
CHECK_INTERVAL=60
MAX_ITERATIONS=5

# Security
ENCRYPTION_KEY=your_encryption_key_here

# Add your API keys below:
# GMAIL_API_KEY=
# BANK_API_TOKEN=
# WHATSAPP_SESSION_PATH=
"""
    
    env_file = Path("D:/Autonomous-FTE-System/.env")
    env_file.write_text(env_template)
    
    print(f"  Created: {env_file}")
    print("  ⚠️  REMEMBER: Fill in your actual API keys!")

def setup_git():
    """Initialize Git repository"""
    print("🔧 Setting up Git...")
    
    repo_path = Path("D:/Autonomous-FTE-System")
    
    # Initialize if not already a repo
    if not (repo_path / ".git").exists():
        subprocess.run(["git", "init"], cwd=repo_path)
        print("  Initialized Git repository")
    
    # Create bronze tier branch
    subprocess.run(["git", "checkout", "-b", "P1-Bronze-Tier"], cwd=repo_path)
    print("  Created and switched to branch: P1-Bronze-Tier")

def main():
    print("=" * 60)
    print("Personal AI Employee - Bronze Tier Setup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Some prerequisites are missing.")
        print("Please install them before continuing.")
        return
    
    # Install dependencies
    install_dependencies()
    
    # Setup vault
    setup_vault()
    
    # Create environment file
    create_environment_file()
    
    # Setup Git
    setup_git()
    
    print("\n" + "=" * 60)
    print("✅ Bronze Tier Setup Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Edit D:/Autonomous-FTE-System/.env and add your API keys")
    print("2. Review the created files in AI_Employee_Vault")
    print("3. Run: python orchestrator.py")
    print("4. Drop files in Drop_Folder to test the system")
    print("\nYour branch: P1-Bronze-Tier")
    print("All work is isolated in this branch.")

if __name__ == "__main__":
    main()

Step 7: Create README for Bronze Tier
Create README_BRONZE.md:
# Personal AI Employee - Bronze Tier

## Overview
This is the Bronze Tier implementation of the Autonomous AI Employee system. It provides basic automation capabilities with one watcher, Claude Code integration, and file-based task management.

## Features
- ✅ File system watcher for automatic task creation
- ✅ Claude Code integration for task processing
- ✅ Obsidian vault as knowledge base and dashboard
- ✅ Basic human-in-the-loop approval system
- ✅ Automated logging and monitoring
- ✅ Skill-based task execution

## Directory Structure
D:/Autonomous-FTE-System/
├── AI_Employee_Vault/ # Obsidian vault
│ ├── Dashboard.md # Live status dashboard
│ ├── Company_Handbook.md # Rules and guidelines
│ ├── Needs_Action/ # New tasks detected
│ ├── Plans/ # Task plans created by Claude
│ ├── Pending_Approval/ # Actions needing approval
│ ├── Approved/ # Approved actions
│ ├── Rejected/ # Rejected actions
│ ├── Done/ # Completed tasks
│ ├── Logs/ # System logs
│ └── Skills/ # Agent skills
├── .claude/skills/ # Claude skills directory
├── orchestrator.py # Main coordination script
├── filesystem_watcher.py # File watcher
└── setup_bronze.py # Setup script


## Setup Instructions

1. **Run the setup script:**
   ```bash
   python setup_bronze.py

2. Configure environment variables:
- Edit D:/Autonomous-FTE-System/.env
- Add your Claude API key and other credentials

3. Start the system:
# Terminal 1 - Start file watcher
python filesystem_watcher.py

# Terminal 2 - Start orchestrator
python orchestrator.py

4. Test the system:
- Drop a file in AI_Employee_Vault/Drop_Folder/
- Watch Claude process it automatically
- Check Dashboard.md for updates

Available Skills:
The system can use skills from D:\Autonomous-FTE-System\.claude\skills:
- file_processor: Read and write files
- text_analyzer: Analyze text content
- task_planner: Create detailed task plans
- email_drafter: Draft email responses
- data_extractor: Extract structured data

How It Works:
Detection: File watcher monitors Drop_Folder
Task Creation: Creates .md file in Needs_Action
Processing: Orchestrator triggers Claude to process
Planning: Claude creates plan in /Plans/
Approval: If needed, creates approval request
Execution: After approval, actions are taken
Completion: Files moved to /Done/, dashboard updated

Bronze Tier Requirements Met:
One watcher script (File System Watcher)
Basic task processing with Claude Code
One MCP server (filesystem built-in)
Dashboard.md updates automatically
All AI functionality as Agent Skills
Human-in-the-loop for approvals

Next Steps (Silver Tier):
Add Gmail and WhatsApp watchers
Implement email sending via MCP
Add scheduling capabilities
Create LinkedIn automation
Enhance approval workflows


### **Step 8: Usage Instructions for Claude CLI**

**When you run this with Claude CLI, use these exact commands:**

```bash
# 1. First, run setup
cd D:\Autonomous-FTE-System
python setup_bronze.py

# 2. Then start the orchestrator (in one terminal)
python orchestrator.py

# 3. In another terminal, start the file watcher
python filesystem_watcher.py

# 4. Test by dropping a file in:
D:\Autonomous-FTE-System\AI_Employee_Vault\Drop_Folder\

Key Points for Claude CLI:
Work in Branch: All code is created in P1-Bronze-Tier branch
Use Available Skills: Automatically detect and use skills from D:\Autonomous-FTE-System\.claude\skills
File-based Communication: All components communicate via markdown files in the vault
Safety First: Dry-run mode enabled by default, approvals required for actions
Log Everything: All actions logged in JSON format for audit

Expected Output:
✅ Complete Bronze Tier implementation
✅ Working file watcher that creates tasks
✅ Claude Code integration for processing
✅ Automatic dashboard updates
✅ Approval workflow for sensitive actions
✅ All code in P1-Bronze-Tier branch

Note: This implementation uses the skills you mentioned and follows the exact architecture from the hackathon document. The system is designed to be extended for Silver, Gold, and Platinum tiers later.

