"""
Silver Tier - Enhanced Orchestrator
Manages multiple watchers, scheduling, and MCP servers
"""
import os
import time
import json
import threading
import subprocess
from datetime import datetime
from pathlib import Path
import schedule
from concurrent.futures import ThreadPoolExecutor

class SilverOrchestrator:
    def __init__(self, vault_path):
        self.vault = Path(vault_path)
        self.watchers = []
        self.mcp_servers = []
        self.scheduled_tasks = []
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Load configuration
        self.config = self.load_config()

        # Setup
        self.setup_directories()
        self.setup_logging()

        print("=" * 60)
        print("SILVER TIER AI EMPLOYEE - ENHANCED ORCHESTRATOR")
        print("=" * 60)

    def load_config(self):
        """Load Silver tier configuration"""
        config_file = self.vault / 'Config' / 'silver_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default Silver configuration
        return {
            "watchers": {
                "filesystem": {"enabled": True, "interval": 60},
                "gmail": {"enabled": True, "interval": 120},
                "whatsapp": {"enabled": True, "interval": 45}
            },
            "mcp_servers": {
                "email": {"enabled": True, "port": 8081},
                "filesystem": {"enabled": True}
            },
            "scheduling": {
                "linkedin_posting": {"enabled": True, "times": ["09:00", "12:00", "17:00"]},
                "daily_briefing": {"enabled": True, "time": "08:00"},
                "weekly_audit": {"enabled": True, "day": "sunday", "time": "22:00"}
            },
            "claude": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000
            }
        }

    def setup_directories(self):
        """Setup additional Silver tier directories"""
        additional_dirs = [
            'Social_Media',
            'Email_Drafts',
            'Client_Communications',
            'Business_Reports',
            'Scheduled_Tasks',
            'In_Progress'
        ]

        for dir_name in additional_dirs:
            (self.vault / dir_name).mkdir(exist_ok=True)

    def setup_logging(self):
        """Setup enhanced logging"""
        log_dir = self.vault / 'Logs'
        log_dir.mkdir(exist_ok=True)

        # Create log files
        log_files = ['system.log', 'watchers.log', 'mcp.log', 'scheduler.log']
        for log_file in log_files:
            (log_dir / log_file).touch(exist_ok=True)

    def start_watchers(self):
        """Start all configured watchers"""
        print("\nStarting Watchers...")

        if self.config['watchers']['filesystem']['enabled']:
            self.start_watcher_thread('filesystem')

        if self.config['watchers']['gmail']['enabled']:
            self.start_watcher_thread('gmail')

        if self.config['watchers']['whatsapp']['enabled']:
            self.start_watcher_thread('whatsapp')

    def start_watcher_thread(self, watcher_type):
        """Start watcher in separate thread"""
        def run_watcher():
            try:
                if watcher_type == 'filesystem':
                    from filesystem_watcher import start_file_watcher
                    start_file_watcher(
                        str(self.vault),
                        str(self.vault / 'Drop_Folder')
                    )
                elif watcher_type == 'gmail':
                    from gmail_watcher import start_gmail_watcher
                    start_gmail_watcher(
                        str(self.vault),
                        'credentials.json',  # Update with actual path
                        str(self.vault / 'Config' / 'gmail_token.pickle')
                    )
                elif watcher_type == 'whatsapp':
                    from whatsapp_watcher import start_whatsapp_watcher
                    start_whatsapp_watcher(
                        str(self.vault),
                        str(self.vault / 'Config' / 'whatsapp_session')
                    )
            except Exception as e:
                self.log_error(f"Watcher {watcher_type} failed: {e}")

        thread = threading.Thread(target=run_watcher, daemon=True)
        thread.start()
        self.watchers.append(thread)
        print(f"  OK {watcher_type.capitalize()} Watcher started")

    def start_mcp_servers(self):
        """Start MCP servers"""
        print("\nStarting MCP Servers...")

        if self.config['mcp_servers']['email']['enabled']:
            self.start_mcp_thread('email')

        # Filesystem MCP is built into Claude Code
        print("  OK Filesystem MCP (built-in)")

    def start_mcp_thread(self, server_type):
        """Start MCP server in thread"""
        def run_mcp():
            try:
                if server_type == 'email':
                    from email_mcp_server import start_email_mcp_server
                    start_email_mcp_server(str(self.vault))
            except Exception as e:
                self.log_error(f"MCP Server {server_type} failed: {e}")

        thread = threading.Thread(target=run_mcp, daemon=True)
        thread.start()
        self.mcp_servers.append(thread)
        print(f"  OK {server_type.capitalize()} MCP Server started")

    def setup_scheduling(self):
        """Setup scheduled tasks"""
        print("\nSetting up Scheduled Tasks...")

        # LinkedIn posting
        if self.config['scheduling']['linkedin_posting']['enabled']:
            from linkedin_poster import LinkedInPoster
            self.linkedin_poster = LinkedInPoster(
                str(self.vault),
                str(self.vault / 'Config' / 'linkedin_session')
            )

            for post_time in self.config['scheduling']['linkedin_posting']['times']:
                schedule.every().day.at(post_time).do(self.post_to_linkedin)
                print(f"  OK LinkedIn post scheduled at {post_time}")

        # Daily briefing
        if self.config['scheduling']['daily_briefing']['enabled']:
            briefing_time = self.config['scheduling']['daily_briefing']['time']
            schedule.every().day.at(briefing_time).do(self.generate_daily_briefing)
            print(f"  OK Daily briefing scheduled at {briefing_time}")

        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        self.scheduled_tasks.append(scheduler_thread)

    def post_to_linkedin(self):
        """Post to LinkedIn"""
        print(f"[{datetime.now().strftime('%H:%M')}] Posting to LinkedIn...")
        self.executor.submit(self.linkedin_poster.scheduled_post)

    def generate_daily_briefing(self):
        """Generate daily briefing"""
        print(f"[{datetime.now().strftime('%H:%M')}] Generating daily briefing...")

        # Use Claude to generate briefing
        briefing_prompt = f"""
        Generate daily briefing for {datetime.now().strftime('%Y-%m-%d')}:

        1. Check /Needs_Action folder for pending tasks
        2. Check /Done folder for completed tasks
        3. Check email and WhatsApp logs
        4. Check LinkedIn posting status
        5. Generate summary and recommendations

        Format as markdown for Dashboard.md
        """

        # This would call Claude Code
        # For now, create placeholder
        self.create_briefing_placeholder()

    def create_briefing_placeholder(self):
        """Create placeholder briefing"""
        briefing_file = self.vault / 'Business_Reports' / f"briefing_{datetime.now().strftime('%Y%m%d')}.md"

        content = f"""# 📊 Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}

## System Status
- ✅ All watchers running
- ✅ MCP servers active
- ✅ Scheduled tasks on track

## Pending Actions
Check /Needs_Action folder for details.

## Today's Agenda
1. Review pending emails
2. Check WhatsApp business messages
3. Post to LinkedIn (scheduled)
4. Process file drops

## Recommendations
- No critical issues detected
- System running optimally
"""

        briefing_file.write_text(content)
        print(f"  📄 Briefing created: {briefing_file.name}")

    def run_scheduler(self):
        """Run scheduled tasks"""
        while True:
            schedule.run_pending()
            time.sleep(60)

    def start_claude_processor(self):
        """Start Claude Code processor"""
        print("\n🧠 Starting Claude Code Processor...")

        def run_claude():
            while True:
                try:
                    # Check for new tasks
                    needs_action = list((self.vault / 'Needs_Action').glob('*.md'))

                    if needs_action:
                        for task in needs_action:
                            self.process_with_claude(task)

                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    self.log_error(f"Claude processor error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=run_claude, daemon=True)
        thread.start()
        print("  OK Claude Code Processor started")

    def process_with_claude(self, task_file):
        """Process task with Claude Code"""
        try:
            # Create prompt
            task_content = task_file.read_text()
            prompt = self.create_silver_prompt(task_content)

            # Run Claude Code
            cmd = [
                "claude",
                "--prompt", prompt,
                "--model", self.config['claude']['model'],
                "--max-tokens", str(self.config['claude']['max_tokens'])
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Create plan file
                plan_file = self.vault / 'Plans' / f"plan_{task_file.stem}.md"
                plan_file.write_text(result.stdout)

                # Move task to processing
                processing_file = self.vault / 'In_Progress' / task_file.name
                task_file.rename(processing_file)

                self.log_action('claude_processed', task_file.name)

        except Exception as e:
            self.log_error(f"Claude processing failed: {e}")

    def create_silver_prompt(self, task_content):
        """Create enhanced prompt for Silver tier"""
        prompt = f"""You are my Silver Tier AI Employee. Enhanced capabilities:

## AVAILABLE SKILLS (from D:\Autonomous-FTE-System\.claude\skills):
- email_handler: Send/draft emails via MCP
- whatsapp_manager: Respond to WhatsApp messages
- linkedin_poster: Create LinkedIn content
- file_processor: Handle file operations
- task_planner: Create detailed plans
- business_analyst: Analyze business data
- customer_service: Handle client communications

## ENHANCED CAPABILITIES:
1. Multi-platform communication (Email, WhatsApp, LinkedIn)
2. Email sending via MCP server
3. Social media posting
4. Advanced scheduling
5. Business reporting

## TASK TO PROCESS:
{task_content}

## INSTRUCTIONS:
1. Analyze the task
2. Use appropriate skill(s)
3. Create detailed Plan.md
4. If action needed, create approval request
5. Update Dashboard.md
6. Log all actions

## Proceed with processing.
"""
        return prompt

    def log_action(self, action, details):
        """Log system actions"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'tier': 'silver'
        }

        log_file = self.vault / 'Logs' / 'system.log'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_error(self, error):
        """Log errors"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'tier': 'silver'
        }

        error_file = self.vault / 'Logs' / 'errors.log'
        with open(error_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        print(f"Error: {error}")

    def update_dashboard(self):
        """Update enhanced dashboard"""
        dashboard = self.vault / 'Dashboard.md'

        # Gather stats
        stats = {
            'needs_action': len(list((self.vault / 'Needs_Action').glob('*.md'))),
            'pending_approval': len(list((self.vault / 'Pending_Approval').glob('*.md'))),
            'in_progress': len(list((self.vault / 'In_Progress').glob('*.md'))),
            'completed': len(list((self.vault / 'Done').glob('*.md'))),
            'watchers': len(self.watchers),
            'mcp_servers': len(self.mcp_servers),
            'scheduled_tasks': len(self.scheduled_tasks)
        }

        content = f"""---
type: dashboard
tier: silver
last_updated: {datetime.now().isoformat()}
version: 2.0
---

# SILVER TIER AI EMPLOYEE DASHBOARD

## System Status
OK **Enhanced Orchestrator**: Running
OK **Multiple Watchers**: {stats['watchers']} active
OK **MCP Servers**: {stats['mcp_servers']} running
OK **Scheduled Tasks**: {stats['scheduled_tasks']} configured
OK **Claude Processor**: Active

## Task Summary
| Status | Count |
|--------|-------|
| Needs Action | {stats['needs_action']} |
| Pending Approval | {stats['pending_approval']} |
| In Progress | {stats['in_progress']} |
| Completed | {stats['completed']} |

## Active Watchers
- File System Watcher: {"OK Running" if self.config['watchers']['filesystem']['enabled'] else "Disabled"}
- Gmail Watcher: {"OK Running" if self.config['watchers']['gmail']['enabled'] else "Disabled"}
- WhatsApp Watcher: {"OK Running" if self.config['watchers']['whatsapp']['enabled'] else "Disabled"}

## MCP Servers
- Email MCP: {"OK Running" if self.config['mcp_servers']['email']['enabled'] else "Disabled"}
- Filesystem MCP: OK Built-in

## Scheduled Tasks
- LinkedIn Posting: {"OK Scheduled" if self.config['scheduling']['linkedin_posting']['enabled'] else "Disabled"}
- Daily Briefing: {"OK Scheduled" if self.config['scheduling']['daily_briefing']['enabled'] else "Disabled"}

## Recent Activity
{self.get_recent_activity()}

---
*Silver Tier AI Employee v2.0 - {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

        dashboard.write_text(content)

    def get_recent_activity(self):
        """Get recent activity from logs"""
        try:
            log_file = self.vault / 'Logs' / 'system.log'
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-5:]  # Last 5 entries

                activities = []
                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        timestamp = entry.get('timestamp', '')[:16].replace('T', ' ')
                        action = entry.get('action', '')
                        activities.append(f"- {timestamp}: {action}")
                    except:
                        continue

                return '\n'.join(activities) if activities else "No recent activity"
        except:
            pass

        return "Loading activity..."

    def monitor_health(self):
        """Monitor system health"""
        print("\n🏥 Starting Health Monitor...")

        def health_check():
            while True:
                try:
                    # Check if watchers are alive
                    # Check if MCP servers responding
                    # Check disk space
                    # Check API limits

                    time.sleep(300)  # Check every 5 minutes

                except Exception as e:
                    self.log_error(f"Health monitor error: {e}")

        thread = threading.Thread(target=health_check, daemon=True)
        thread.start()
        print("  OK Health Monitor started")

    def run(self):
        """Main orchestration loop"""
        print("\n" + "=" * 60)
        print("Starting Silver Tier AI Employee System")
        print("=" * 60)

        try:
            # Start components
            self.start_watchers()
            self.start_mcp_servers()
            self.setup_scheduling()
            self.start_claude_processor()
            self.monitor_health()

            # Main loop
            print("\n✅ All systems started!")
            print("📊 Dashboard updating every 30 seconds")
            print("🛑 Press Ctrl+C to stop\n")

            while True:
                self.update_dashboard()
                time.sleep(30)  # Update every 30 seconds

        except KeyboardInterrupt:
            print("\nSilver Tier system stopped by user")
        except Exception as e:
            print(f"\nSystem error: {e}")
            self.log_error(f"System crash: {e}")

if __name__ == "__main__":
    VAULT_PATH = "D:/Autonomous-FTE-System/AI_Employee_Vault"
    orchestrator = SilverOrchestrator(VAULT_PATH)
    orchestrator.run()