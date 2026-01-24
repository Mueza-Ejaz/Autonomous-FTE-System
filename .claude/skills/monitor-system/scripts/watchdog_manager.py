#!/usr/bin/env python3
"""
Watchdog Manager Script
Monitors critical processes and restarts them if they crash
"""

import json
import os
import subprocess
import time
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import psutil


# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/AI_Employee_Vault'))
LOG_DIR = VAULT_PATH / 'Logs' / 'system'

# Critical processes to monitor
PROCESSES = {
    'gmail_watcher': {
        'command': 'python3 watchers/gmail_watcher.py',
        'pid_file': '/tmp/gmail_watcher.pid',
        'heartbeat_file': '/tmp/gmail_watcher_heartbeat',
        'max_restarts': 3,
        'restart_window': 3600,  # 1 hour
        'critical': True
    },
    'whatsapp_watcher': {
        'command': 'python3 watchers/whatsapp_watcher.py',
        'pid_file': '/tmp/whatsapp_watcher.pid',
        'heartbeat_file': '/tmp/whatsapp_watcher_heartbeat',
        'max_restarts': 3,
        'restart_window': 3600,
        'critical': True
    },
    'linkedin_watcher': {
        'command': 'python3 watchers/linkedin_watcher.py',
        'pid_file': '/tmp/linkedin_watcher.pid',
        'heartbeat_file': '/tmp/linkedin_watcher_heartbeat',
        'max_restarts': 3,
        'restart_window': 3600,
        'critical': False
    },
    'finance_watcher': {
        'command': 'python3 watchers/finance_watcher.py',
        'pid_file': '/tmp/finance_watcher.pid',
        'heartbeat_file': '/tmp/finance_watcher_heartbeat',
        'max_restarts': 3,
        'restart_window': 3600,
        'critical': False
    },
    'filesystem_watcher': {
        'command': 'python3 watchers/filesystem_watcher.py',
        'pid_file': '/tmp/filesystem_watcher.pid',
        'heartbeat_file': '/tmp/filesystem_watcher_heartbeat',
        'max_restarts': 3,
        'restart_window': 3600,
        'critical': False
    }
}


class ProcessInfo:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.restart_attempts = []  # List of restart timestamps
        self.disabled = False
        self.last_check = None
        self.status = 'unknown'


class WatchdogManager:
    def __init__(self):
        self.processes = {name: ProcessInfo(name, config) for name, config in PROCESSES.items()}
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def is_process_running(self, process_info: ProcessInfo) -> tuple:
        """Check if process is running and responsive"""
        pid_file = process_info.config['pid_file']

        # Check if PID file exists
        if not os.path.exists(pid_file):
            return False, 'pid_file_missing'

        try:
            # Read PID
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            if not psutil.pid_exists(pid):
                return False, 'process_not_found'

            # Check if process is responsive (heartbeat)
            heartbeat_file = process_info.config.get('heartbeat_file')
            if heartbeat_file and os.path.exists(heartbeat_file):
                heartbeat_age = time.time() - os.path.getmtime(heartbeat_file)
                if heartbeat_age > 600:  # 10 minutes
                    return False, f'heartbeat_stale_{int(heartbeat_age)}s'

            return True, 'healthy'

        except Exception as e:
            return False, f'check_error_{str(e)}'

    def restart_process(self, process_info: ProcessInfo) -> bool:
        """Restart a process"""
        # Check if we've exceeded restart limits
        if not self.can_restart(process_info):
            self.log_event('restart_limit_exceeded', process_info, {
                'restart_attempts': len(process_info.restart_attempts),
                'max_restarts': process_info.config['max_restarts'],
                'window': process_info.config['restart_window']
            })
            process_info.disabled = True
            self.escalate_to_user(process_info, 'restart_limit_exceeded')
            return False

        # Clean up old PID file
        pid_file = process_info.config['pid_file']
        if os.path.exists(pid_file):
            os.remove(pid_file)

        # Calculate exponential backoff delay
        attempt_count = len(process_info.restart_attempts)
        delay = min(5 * (2 ** attempt_count), 60)  # Max 60 seconds

        self.log_event('restarting_process', process_info, {
            'attempt': attempt_count + 1,
            'delay': delay
        })

        print(f"  Waiting {delay}s before restart (attempt {attempt_count + 1})...")
        time.sleep(delay)

        try:
            # Start process
            command = process_info.config['command']
            proc = subprocess.Popen(
                command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Write PID file
            with open(pid_file, 'w') as f:
                f.write(str(proc.pid))

            # Record restart attempt
            process_info.restart_attempts.append(datetime.now(timezone.utc))

            # Wait a moment and verify it started
            time.sleep(5)

            if psutil.pid_exists(proc.pid):
                process_info.status = 'running'
                self.log_event('restart_success', process_info, {
                    'new_pid': proc.pid,
                    'attempt': attempt_count + 1
                })
                print(f"  Successfully restarted {process_info.name} (PID: {proc.pid})")
                return True
            else:
                self.log_event('restart_failed', process_info, {
                    'reason': 'process_died_immediately'
                })
                print(f"  Failed: Process died immediately after start")
                return False

        except Exception as e:
            self.log_event('restart_error', process_info, {
                'exception': str(e)
            })
            print(f"  Error restarting: {str(e)}")
            return False

    def can_restart(self, process_info: ProcessInfo) -> bool:
        """Check if we can restart based on restart limits"""
        max_restarts = process_info.config['max_restarts']
        window = process_info.config['restart_window']

        # Clean up old restart attempts outside the window
        cutoff_time = datetime.now(timezone.utc).timestamp() - window
        process_info.restart_attempts = [
            ts for ts in process_info.restart_attempts
            if ts.timestamp() > cutoff_time
        ]

        # Check if we've exceeded the limit
        return len(process_info.restart_attempts) < max_restarts

    def kill_unresponsive_process(self, process_info: ProcessInfo, pid: int) -> bool:
        """Kill an unresponsive process"""
        self.log_event('killing_unresponsive', process_info, {'pid': pid})

        try:
            # Try graceful termination first
            os.kill(pid, signal.SIGTERM)
            time.sleep(30)

            # Force kill if still running
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(5)

            return not psutil.pid_exists(pid)

        except Exception as e:
            self.log_event('kill_error', process_info, {
                'exception': str(e),
                'pid': pid
            })
            return False

    def monitor_all_processes(self):
        """Check all processes and restart if needed"""
        print(f"\nChecking processes: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        for process_info in self.processes.values():
            if process_info.disabled:
                print(f"⏸️  {process_info.name}: Disabled (manual intervention required)")
                continue

            running, status = self.is_process_running(process_info)
            process_info.last_check = datetime.now(timezone.utc)

            if running:
                print(f"✅ {process_info.name}: Healthy")
                process_info.status = 'healthy'
            else:
                print(f"❌ {process_info.name}: {status}")
                process_info.status = f'failed_{status}'

                # Attempt restart
                print(f"  Attempting restart...")
                success = self.restart_process(process_info)

                if not success and process_info.config['critical']:
                    print(f"  ⚠️  Critical process failed to restart!")

    def escalate_to_user(self, process_info: ProcessInfo, reason: str):
        """Create alert for user intervention"""
        alert_file = VAULT_PATH / 'Needs_Action' / f"ALERT_PROCESS_{process_info.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        alert_content = f"""---
type: process_alert
severity: {'critical' if process_info.config['critical'] else 'high'}
process: {process_info.name}
reason: {reason}
created: {datetime.now(timezone.utc).isoformat()}
---

# ⚠️ Process Restart Failed

**Process:** {process_info.name}
**Status:** {'Critical' if process_info.config['critical'] else 'Non-critical'}
**Reason:** {reason}

## Restart Attempts

Total attempts: {len(process_info.restart_attempts)}
Max allowed: {process_info.config['max_restarts']}

**Auto-restart has been disabled** for this process to prevent restart loops.

## Manual Recovery Steps

1. Check process logs for errors
2. Verify dependencies are installed
3. Check file permissions
4. Manually start process:
   ```bash
   {process_info.config['command']}
   ```

5. Verify process is running:
   ```bash
   cat {process_info.config['pid_file']}
   ps aux | grep $(cat {process_info.config['pid_file']})
   ```

## Re-enable Auto-restart

After resolving the issue, re-enable by removing this alert file and running:
```bash
python3 .claude/skills/monitor-system/scripts/watchdog_manager.py --enable {process_info.name}
```

---
*Generated by monitor-system skill - watchdog_manager.py*
"""

        alert_file.parent.mkdir(parents=True, exist_ok=True)
        alert_file.write_text(alert_content)
        print(f"  📧 Alert created: {alert_file.name}")

    def log_event(self, event_type: str, process_info: ProcessInfo, metadata: dict):
        """Log watchdog event"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = LOG_DIR / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'log_type': 'system',
            'event_type': event_type,
            'severity': 'high' if process_info.config['critical'] else 'medium',
            'actor': 'watchdog_manager',
            'component': process_info.name,
            'status': process_info.status,
            'metadata': metadata
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def generate_status_report(self) -> str:
        """Generate status report of all processes"""
        report = f"""# Watchdog Status Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Process Status

| Process | Status | Last Check | Restarts |
|---------|--------|------------|----------|
"""

        for name, info in self.processes.items():
            status_emoji = {
                'healthy': '✅',
                'unknown': '❓',
                'disabled': '⏸️'
            }.get(info.status.split('_')[0], '❌')

            last_check = info.last_check.strftime('%H:%M:%S') if info.last_check else 'Never'
            restart_count = len(info.restart_attempts)

            report += f"| {name} | {status_emoji} {info.status} | {last_check} | {restart_count} |\n"

        return report

    def cleanup_restart_history(self):
        """Clean up old restart attempt records"""
        for process_info in self.processes.values():
            window = process_info.config['restart_window']
            cutoff_time = datetime.now(timezone.utc).timestamp() - window

            process_info.restart_attempts = [
                ts for ts in process_info.restart_attempts
                if ts.timestamp() > cutoff_time
            ]


def main():
    """Main watchdog execution"""
    watchdog = WatchdogManager()

    # Monitor all processes
    watchdog.monitor_all_processes()

    # Cleanup old restart records
    watchdog.cleanup_restart_history()

    # Generate status report
    report = watchdog.generate_status_report()
    print("\n" + report)

    # Write report to file
    report_file = VAULT_PATH / 'System_Status_Processes.md'
    report_file.write_text(report)


def run_daemon():
    """Run watchdog as a continuous daemon"""
    print("Starting Watchdog Manager (daemon mode)")
    print("Press Ctrl+C to stop\n")

    watchdog = WatchdogManager()

    try:
        while True:
            watchdog.monitor_all_processes()
            watchdog.cleanup_restart_history()

            # Wait 5 minutes before next check
            print("\nSleeping for 5 minutes...")
            time.sleep(300)

    except KeyboardInterrupt:
        print("\n\nWatchdog Manager stopped by user")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        run_daemon()
    else:
        main()
