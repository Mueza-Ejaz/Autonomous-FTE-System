#!/usr/bin/env python3
"""
Health Monitor Script
Runs every 5 minutes to check system health
"""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
import psutil
import requests


# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/AI_Employee_Vault'))
LOG_DIR = VAULT_PATH / 'Logs' / 'system'
HEALTH_LOG = LOG_DIR / 'health_checks.json'
STATUS_FILE = VAULT_PATH / 'System_Status.md'

# Process monitoring
WATCHERS = {
    'gmail_watcher': '/tmp/gmail_watcher.pid',
    'whatsapp_watcher': '/tmp/whatsapp_watcher.pid',
    'linkedin_watcher': '/tmp/linkedin_watcher.pid',
    'finance_watcher': '/tmp/finance_watcher.pid',
    'filesystem_watcher': '/tmp/filesystem_watcher.pid'
}

MCP_SERVERS = {
    'email': 8,
    'xero': 8,
    'social_media': 5,
    'browser': 4
}


class HealthMonitor:
    def __init__(self):
        self.health_score = 0
        self.component_scores = {}
        self.issues = []

    def check_watcher_health(self) -> int:
        """Check all Watcher processes (30 points max)"""
        score = 0
        points_per_watcher = 6

        for watcher_name, pid_file in WATCHERS.items():
            try:
                # Check if PID file exists
                if not os.path.exists(pid_file):
                    self.issues.append(f"{watcher_name}: PID file not found")
                    continue

                # Read PID
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())

                # Check if process is running
                if psutil.pid_exists(pid):
                    # Check heartbeat (if exists)
                    heartbeat_file = f'/tmp/{watcher_name}_heartbeat'
                    if os.path.exists(heartbeat_file):
                        heartbeat_age = time.time() - os.path.getmtime(heartbeat_file)
                        if heartbeat_age > 600:  # 10 minutes
                            self.issues.append(f"{watcher_name}: Heartbeat stale ({int(heartbeat_age)}s)")
                            continue

                    score += points_per_watcher
                else:
                    self.issues.append(f"{watcher_name}: Process not running (PID: {pid})")

            except Exception as e:
                self.issues.append(f"{watcher_name}: Error checking health - {str(e)}")

        return score

    def check_mcp_health(self) -> int:
        """Check MCP Servers (25 points max)"""
        score = 0

        for server_name, points in MCP_SERVERS.items():
            try:
                # Test MCP server with simple command
                # This is a simplified check - adjust based on actual MCP setup
                result = subprocess.run(
                    ['claude-code', 'mcp', 'list'],
                    capture_output=True,
                    timeout=10,
                    text=True
                )

                if result.returncode == 0 and server_name in result.stdout:
                    score += points
                else:
                    self.issues.append(f"MCP {server_name}: Not responding")

            except subprocess.TimeoutExpired:
                self.issues.append(f"MCP {server_name}: Health check timeout")
            except Exception as e:
                self.issues.append(f"MCP {server_name}: {str(e)}")

        return score

    def check_disk_health(self) -> int:
        """Check disk space (15 points max)"""
        score = 0

        try:
            # Check system disk space
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100

            if free_percent > 20:
                score += 10  # Excellent
            elif free_percent > 10:
                score += 5   # Warning
                self.issues.append(f"Disk space warning: {free_percent:.1f}% free")
            else:
                self.issues.append(f"Disk space critical: {free_percent:.1f}% free")

            # Check log directory size
            log_size_gb = self.get_directory_size(LOG_DIR) / (1024**3)
            if log_size_gb < 5:
                score += 3
            else:
                self.issues.append(f"Log directory large: {log_size_gb:.1f}GB")

            # Check vault access
            test_file = VAULT_PATH / '.health_check_test'
            try:
                test_file.write_text('test')
                test_file.unlink()
                score += 2
            except:
                self.issues.append("Vault: Cannot write test file")

        except Exception as e:
            self.issues.append(f"Disk check error: {str(e)}")

        return score

    def check_network_health(self) -> int:
        """Check network connectivity (15 points max)"""
        score = 0

        # 1. Internet connectivity
        try:
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code == 200:
                score += 7
        except:
            self.issues.append("Network: No internet connectivity")

        # 2. API endpoints
        api_endpoints = [
            'https://www.googleapis.com',
            'https://api.twitter.com',
            'https://graph.facebook.com',
            'https://api.xero.com'
        ]

        reachable_count = 0
        for endpoint in api_endpoints:
            try:
                response = requests.head(endpoint, timeout=3)
                if response.status_code < 500:
                    reachable_count += 1
            except:
                pass

        if reachable_count >= 3:
            score += 5
        elif reachable_count > 0:
            score += 2
            self.issues.append(f"Network: Only {reachable_count}/4 APIs reachable")

        # 3. DNS resolution
        try:
            import socket
            socket.gethostbyname('www.google.com')
            score += 3
        except:
            self.issues.append("Network: DNS resolution failed")

        return score

    def check_logging_health(self) -> int:
        """Check logging system (10 points max)"""
        score = 0
        today = datetime.now().strftime('%Y-%m-%d')

        # 1. Check if logs being written
        action_log = VAULT_PATH / 'Logs' / 'actions' / f'{today}.json'
        if action_log.exists():
            age_minutes = (time.time() - action_log.stat().st_mtime) / 60
            if age_minutes < 30:  # Written in last 30 minutes
                score += 5

        # 2. Check for write errors (simplified - would check error logs)
        score += 3  # Assume no errors unless proven otherwise

        # 3. Check rotation (yesterday's log should exist)
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_log = VAULT_PATH / 'Logs' / 'actions' / f'{yesterday}.json'
        if yesterday_log.exists():
            score += 2

        return score

    def check_vault_health(self) -> int:
        """Check vault access (5 points max)"""
        score = 0

        # 1. Read access
        try:
            dashboard = VAULT_PATH / 'Dashboard.md'
            if dashboard.exists():
                dashboard.read_text()
                score += 2
        except:
            self.issues.append("Vault: Cannot read Dashboard.md")

        # 2. Write access
        try:
            test_file = VAULT_PATH / '.health_check_test'
            test_file.write_text('test')
            test_file.unlink()
            score += 2
        except:
            self.issues.append("Vault: Cannot write files")

        # 3. No lock conflicts (simplified check)
        score += 1  # Assume no locks unless detected

        return score

    def calculate_health_score(self) -> dict:
        """Calculate overall health score"""
        self.component_scores = {
            'watchers': self.check_watcher_health(),
            'mcp_servers': self.check_mcp_health(),
            'disk_space': self.check_disk_health(),
            'network': self.check_network_health(),
            'logging': self.check_logging_health(),
            'vault': self.check_vault_health()
        }

        self.health_score = sum(self.component_scores.values())

        # Determine status
        if self.health_score >= 90:
            status = 'excellent'
            status_emoji = '🟢'
        elif self.health_score >= 80:
            status = 'good'
            status_emoji = '🟡'
        elif self.health_score >= 50:
            status = 'degraded'
            status_emoji = '🟠'
        else:
            status = 'critical'
            status_emoji = '🔴'

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'health_score': self.health_score,
            'status': status,
            'status_emoji': status_emoji,
            'components': self.component_scores,
            'issues': self.issues
        }

    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total

    def log_health_check(self, result: dict):
        """Log health check result"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Append to health check log
        with open(HEALTH_LOG, 'a') as f:
            f.write(json.dumps(result) + '\n')

    def update_status_file(self, result: dict):
        """Update System_Status.md with current health"""
        status_content = f"""---
last_updated: {result['timestamp']}
health_score: {result['health_score']}
status: {result['status']}
---

# System Health Report

**Overall Score:** {result['health_score']}/100 {result['status_emoji']} {result['status'].title()}

## Component Status

| Component | Score | Max | Status |
|-----------|-------|-----|--------|
| Watchers | {result['components']['watchers']} | 30 | {'✅' if result['components']['watchers'] >= 24 else '⚠️'} |
| MCP Servers | {result['components']['mcp_servers']} | 25 | {'✅' if result['components']['mcp_servers'] >= 20 else '⚠️'} |
| Disk Space | {result['components']['disk_space']} | 15 | {'✅' if result['components']['disk_space'] >= 12 else '⚠️'} |
| Network | {result['components']['network']} | 15 | {'✅' if result['components']['network'] >= 12 else '⚠️'} |
| Logging | {result['components']['logging']} | 10 | {'✅' if result['components']['logging'] >= 8 else '⚠️'} |
| Vault | {result['components']['vault']} | 5 | {'✅' if result['components']['vault'] >= 4 else '⚠️'} |

## Issues Detected

"""
        if result['issues']:
            for issue in result['issues']:
                status_content += f"- ⚠️ {issue}\n"
        else:
            status_content += "No issues detected. All systems operational.\n"

        status_content += f"""
**Last Check:** {result['timestamp']}
**Next Check:** ~5 minutes

---
*Generated by monitor-system skill*
"""

        STATUS_FILE.write_text(status_content)

    def create_alert_if_needed(self, result: dict):
        """Create alert file if health is critical"""
        if result['health_score'] < 50:
            alert_file = VAULT_PATH / 'Needs_Action' / f"ALERT_CRITICAL_HEALTH_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            alert_content = f"""---
type: system_alert
severity: critical
health_score: {result['health_score']}
created: {result['timestamp']}
---

# 🔴 CRITICAL: System Health Alert

**Health Score:** {result['health_score']}/100

## Critical Issues

"""
            for issue in result['issues']:
                alert_content += f"- {issue}\n"

            alert_content += """
## Immediate Actions Required

1. Review issues above
2. Check system logs: `/Vault/Logs/system/`
3. Restart failed processes if needed
4. Investigate root cause

**Auto-recovery may be in progress.** Check logs for recovery attempts.
"""

            alert_file.parent.mkdir(parents=True, exist_ok=True)
            alert_file.write_text(alert_content)


def main():
    """Main health check execution"""
    monitor = HealthMonitor()
    result = monitor.calculate_health_score()

    # Log the result
    monitor.log_health_check(result)

    # Update status file
    monitor.update_status_file(result)

    # Create alert if critical
    monitor.create_alert_if_needed(result)

    # Print summary
    print(f"Health Check Complete: {result['health_score']}/100 ({result['status']})")
    if result['issues']:
        print(f"Issues detected: {len(result['issues'])}")
        for issue in result['issues']:
            print(f"  - {issue}")


if __name__ == '__main__':
    main()
