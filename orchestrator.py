"""
Bronze Tier - Main Orchestrator
Coordinates between watchers, Claude, and MCP servers
Supports Gemini API as fallback when Claude is unavailable
"""
import os
import time
import json
import subprocess
import requests
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
                "gemini_api_key": "AIzaSyAfPyOoWw0v3ysF0M_MhCd_0tHvm3dDZps",  # Gemini API key
                "fallback_to_gemini": True,
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
        """Process a task using Claude Code, with Gemini fallback"""
        try:
            # Create a prompt for Claude
            prompt = self.create_claude_prompt(task_file)

            # Try Claude first
            claude_success = self.try_claude_processing(prompt, task_file)

            if claude_success:
                return True
            elif self.config.get('fallback_to_gemini', False):
                # Fallback to Gemini API
                print("Claude unavailable, falling back to Gemini API...")
                return self.process_with_gemini(prompt, task_file)
            else:
                return False

        except Exception as e:
            self.log_error(f"Processing failed: {e}")
            # Try Gemini as fallback if Claude failed
            if self.config.get('fallback_to_gemini', False):
                print("Claude unavailable, falling back to Gemini API...")
                return self.process_with_gemini(self.create_claude_prompt(task_file), task_file)
            return False

    def try_claude_processing(self, prompt, task_file):
        """Try processing with Claude"""
        try:
            cmd = [
                self.config['claude_path'],
                "process-task",
                "--prompt", prompt,
                "--vault", str(self.vault),
                "--output", str(self.vault / 'Plans' / f'plan_{task_file.stem}.md')
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            self.log_action({
                'timestamp': datetime.now().isoformat(),
                'action': 'claude_processing',
                'task': task_file.name,
                'success': success,
                'output': result.stdout[:500] if result.stdout else 'No output'
            })

            return success
        except subprocess.TimeoutExpired:
            print("Claude processing timed out")
            return False
        except FileNotFoundError:
            print("Claude CLI not found")
            return False
        except Exception as e:
            print(f"Claude processing error: {e}")
            return False

    def process_with_gemini(self, prompt, task_file):
        """Process a task using Gemini API as fallback"""
        try:
            import google.generativeai as genai

            # Configure with the provided API key
            api_key = self.config.get('gemini_api_key', 'AIzaSyAfPyOoWw0v3ysF0M_MhCd_0tHvm3dDZps')
            genai.configure(api_key=api_key)

            # Select the model
            model = genai.GenerativeModel('gemini-pro')

            # Generate content
            response = model.generate_content(prompt)

            if response.text:
                # Save the response to a plan file
                plan_file = self.vault / 'Plans' / f'plan_{task_file.stem}_gemini.md'
                plan_file.write_text(response.text)

                self.log_action({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'gemini_processing',
                    'task': task_file.name,
                    'success': True,
                    'output': response.text[:500]  # First 500 chars
                })

                return True
            else:
                self.log_action({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'gemini_processing',
                    'task': task_file.name,
                    'success': False,
                    'output': 'No response from Gemini'
                })
                return False

        except ImportError:
            print("Google Generative AI library not installed. Install with: pip install google-generativeai")
            self.log_error("Gemini library not installed")
            return False
        except Exception as e:
            self.log_error(f"Gemini processing failed: {e}")
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

## Available Skills (from D:\\Autonomous-FTE-System\\.claude\\skills):
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
- 🤖 AI Engine: {(lambda: 'Claude/Gemini' if self.config.get('fallback_to_gemini', True) else 'Claude only')()}

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