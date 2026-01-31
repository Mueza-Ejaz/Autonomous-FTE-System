"""
Alert System for Gold Tier
Manages system alerts, notifications, and escalation procedures.
"""

import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    SYSTEM_HEALTH = "system_health"
    BACKUP_STATUS = "backup_status"
    MCP_SERVER = "mcp_server"
    PROCESS_MONITOR = "process_monitor"
    RESOURCE_USAGE = "resource_usage"
    SECURITY_EVENT = "security_event"
    CUSTOM = "custom"


class AlertChannel(Enum):
    CONSOLE = "console"
    FILE = "file"
    EMAIL = "email"
    VAULT_ACTION = "vault_action"


class Alert:
    """Represents an alert with all necessary information"""

    def __init__(self, level: AlertLevel, alert_type: AlertType, title: str,
                 message: str, details: Dict[str, Any] = None,
                 channels: List[AlertChannel] = None):
        self.id = f"alert_{int(datetime.now().timestamp())}_{hash(title) % 10000}"
        self.level = level
        self.type = alert_type
        self.title = title
        self.message = message
        self.details = details or {}
        self.channels = channels or [AlertChannel.VAULT_ACTION, AlertChannel.FILE]
        self.timestamp = datetime.now()
        self.notified_channels = []
        self.resolved = False
        self.resolution_time = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level.value,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "channels": [channel.value for channel in self.channels],
            "timestamp": self.timestamp.isoformat(),
            "notified_channels": self.notified_channels,
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        alert = cls.__new__(cls)
        alert.id = data["id"]
        alert.level = AlertLevel(data["level"])
        alert.type = AlertType(data["type"])
        alert.title = data["title"]
        alert.message = data["message"]
        alert.details = data["details"]
        alert.channels = [AlertChannel(channel) for channel in data["channels"]]
        alert.timestamp = datetime.fromisoformat(data["timestamp"])
        alert.notified_channels = data["notified_channels"]
        alert.resolved = data["resolved"]
        alert.resolution_time = datetime.fromisoformat(data["resolution_time"]) if data["resolution_time"] else None
        return alert


class AlertSystem:
    """Main alert management system"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security"):
        self.storage_path = Path(storage_path)
        (self.storage_path / "Alerts").mkdir(parents=True, exist_ok=True)
        (self.storage_path / "Audit_Logs").mkdir(exist_ok=True)

        # Alert configuration
        self.alert_config = {
            "email_notifications": False,  # Disabled by default for security
            "email_smtp_server": "smtp.gmail.com",
            "email_smtp_port": 587,
            "email_username": "",
            "email_password": "",
            "email_recipients": [],
            "max_alerts_per_minute": 10,  # Rate limiting
            "alert_retention_days": 30
        }

        # Set up logging
        self.logger = self._setup_logging()

        # Track alerts
        self.active_alerts: List[Alert] = []
        self.history: List[Alert] = []
        self.alert_rate_counter = 0
        self.rate_limit_reset_time = datetime.now()

        # Load any existing alerts
        self._load_existing_alerts()

    def _setup_logging(self) -> logging.Logger:
        """Set up alert system logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "Audit_Logs" / "alert_system.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_existing_alerts(self):
        """Load any existing alerts from storage"""
        # Look for active alerts in the Alerts directory
        alert_files = list((self.storage_path / "Alerts").glob("ALERT_*.json"))

        for alert_file in alert_files:
            try:
                with open(alert_file, 'r') as f:
                    alert_data = json.load(f)
                    alert = Alert.from_dict(alert_data)
                    self.active_alerts.append(alert)
            except Exception as e:
                self.logger.error(f"Error loading alert from {alert_file}: {str(e)}")

    def create_alert(self, level: AlertLevel, alert_type: AlertType, title: str,
                     message: str, details: Dict[str, Any] = None,
                     channels: List[AlertChannel] = None) -> str:
        """Create and process a new alert"""
        # Rate limiting
        if self._is_rate_limited():
            self.logger.warning(f"Alert rate limited: {title}")
            return None

        # Create the alert
        alert = Alert(level, alert_type, title, message, details, channels)

        # Add to active alerts
        self.active_alerts.append(alert)

        # Process the alert through specified channels
        self._process_alert(alert)

        # Log the alert
        self.logger.info(f"Created alert {alert.id}: {level.value.upper()} - {title}")

        # Save alert to file
        self._save_alert(alert)

        return alert.id

    def _is_rate_limited(self) -> bool:
        """Check if alert creation is rate limited"""
        now = datetime.now()

        # Reset counter if enough time has passed
        if (now - self.rate_limit_reset_time).seconds >= 60:  # Reset every minute
            self.alert_rate_counter = 0
            self.rate_limit_reset_time = now

        # Check if we've exceeded the limit
        if self.alert_rate_counter >= self.alert_config["max_alerts_per_minute"]:
            return True

        # Increment counter
        self.alert_rate_counter += 1
        return False

    def _process_alert(self, alert: Alert):
        """Process an alert through its specified channels"""
        for channel in alert.channels:
            if channel == AlertChannel.CONSOLE:
                self._send_to_console(alert)
            elif channel == AlertChannel.FILE:
                self._send_to_file(alert)
            elif channel == AlertChannel.EMAIL and self.alert_config["email_notifications"]:
                self._send_via_email(alert)
            elif channel == AlertChannel.VAULT_ACTION:
                self._create_vault_action(alert)

    def _send_to_console(self, alert: Alert):
        """Send alert to console"""
        level_symbol = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }.get(alert.level, "📢")

        print(f"{level_symbol} [{alert.level.value.upper()}] {alert.title}")
        print(f"   Message: {alert.message}")
        if alert.details:
            print(f"   Details: {json.dumps(alert.details, indent=2)[:200]}...")  # Truncate long details

        alert.notified_channels.append("console")

    def _send_to_file(self, alert: Alert):
        """Save alert to file"""
        # Already handled by _save_alert method
        alert.notified_channels.append("file")

    def _create_vault_action(self, alert: Alert):
        """Create an action item in the Vault for critical alerts"""
        if alert.level in [AlertLevel.CRITICAL, AlertLevel.ERROR]:
            # Create a file in Needs_Action for human review
            action_file = Path("Vault/Needs_Action") / f"ALERT_{alert.type.value.upper()}_{alert.id}.md"

            with open(action_file, 'w') as f:
                f.write(f"""---
type: alert
priority: {"high" if alert.level == AlertLevel.CRITICAL else "normal"}
category: {alert.type.value}
generated: {alert.timestamp.isoformat()}
---

# {alert.level.value.upper()} Alert: {alert.title}

## Message
{alert.message}

## Details
```json
{json.dumps(alert.details, indent=2)}
```

## Action Required
{'**CRITICAL:** Immediate attention required!' if alert.level == AlertLevel.CRITICAL else 'Please review and take appropriate action.'}

---
*Generated by Alert System*
""")

            self.logger.info(f"Created vault action for alert {alert.id}: {action_file}")

        alert.notified_channels.append("vault_action")

    def _send_via_email(self, alert: Alert):
        """Send alert via email (disabled by default for security)"""
        if not self.alert_config["email_notifications"]:
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.alert_config["email_username"]
            msg['To'] = ", ".join(self.alert_config["email_recipients"])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"

            body = f"""
Alert Level: {alert.level.value.upper()}
Type: {alert.type.value}
Title: {alert.title}
Message: {alert.message}

Details:
{json.dumps(alert.details, indent=2) if alert.details else 'No additional details'}

Generated at: {alert.timestamp.isoformat()}
"""
            msg.attach(MIMEText(body, 'plain'))

            # Connect to server and send email
            server = smtplib.SMTP(self.alert_config["email_smtp_server"], self.alert_config["email_smtp_port"])
            server.starttls()
            server.login(self.alert_config["email_username"], self.alert_config["email_password"])
            server.send_message(msg)
            server.quit()

            alert.notified_channels.append("email")
            self.logger.info(f"Sent email alert: {alert.id}")
        except Exception as e:
            self.logger.error(f"Failed to send email alert {alert.id}: {str(e)}")

    def _save_alert(self, alert: Alert):
        """Save alert to persistent storage"""
        alert_file = self.storage_path / "Alerts" / f"ALERT_{alert.type.value.upper()}_{alert.id}.json"

        with open(alert_file, 'w') as f:
            json.dump(alert.to_dict(), f, indent=2)

    def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Mark an alert as resolved"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolution_time = datetime.now()

                # Update the saved file
                self._save_alert(alert)

                self.logger.info(f"Resolved alert {alert_id}: {resolution_notes}")
                return True

        # If not in active alerts, try to load from file
        alert_file = self.storage_path / "Alerts" / f"ALERT_*_{alert_id}.json"
        for file_path in (self.storage_path / "Alerts").glob(f"ALERT_*_{alert_id}.json"):
            try:
                with open(file_path, 'r') as f:
                    alert_data = json.load(f)
                    alert_data["resolved"] = True
                    alert_data["resolution_time"] = datetime.now().isoformat()

                with open(file_path, 'w') as f:
                    json.dump(alert_data, f, indent=2)

                self.logger.info(f"Resolved alert {alert_id} (from file)")
                return True
            except Exception as e:
                self.logger.error(f"Error updating resolved status for alert {alert_id}: {str(e)}")

        return False

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (non-resolved) alerts"""
        return [alert.to_dict() for alert in self.active_alerts if not alert.resolved]

    def get_alert_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get alert history for the specified number of days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_alerts = []

        # Check active alerts
        for alert in self.active_alerts:
            if alert.timestamp >= cutoff_date:
                recent_alerts.append(alert.to_dict())

        # Also check alert files
        alert_files = list((self.storage_path / "Alerts").glob("ALERT_*.json"))
        for alert_file in alert_files:
            try:
                with open(alert_file, 'r') as f:
                    alert_data = json.load(f)
                    alert_time = datetime.fromisoformat(alert_data["timestamp"])
                    if alert_time >= cutoff_date:
                        # Add to list if not already there
                        if not any(a["id"] == alert_data["id"] for a in recent_alerts):
                            recent_alerts.append(alert_data)
            except Exception as e:
                self.logger.error(f"Error reading alert history from {alert_file}: {str(e)}")

        # Sort by timestamp, newest first
        recent_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        return recent_alerts

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get a summary of alert statistics"""
        all_alerts = self.get_alert_history(days=7)  # Last week

        level_counts = {"info": 0, "warning": 0, "error": 0, "critical": 0}
        type_counts = {}
        active_count = 0

        for alert in all_alerts:
            level_counts[alert["level"]] += 1

            alert_type = alert["type"]
            if alert_type in type_counts:
                type_counts[alert_type] += 1
            else:
                type_counts[alert_type] = 1

            if not alert["resolved"]:
                active_count += 1

        return {
            "total_alerts_last_week": len(all_alerts),
            "active_alerts": active_count,
            "level_breakdown": level_counts,
            "type_breakdown": type_counts,
            "timestamp": datetime.now().isoformat()
        }

    def configure_email(self, smtp_server: str, smtp_port: int, username: str,
                       password: str, recipients: List[str]):
        """Configure email settings for alerts"""
        self.alert_config.update({
            "email_smtp_server": smtp_server,
            "email_smtp_port": smtp_port,
            "email_username": username,
            "email_password": password,
            "email_recipients": recipients,
            "email_notifications": True  # Enable after configuration
        })

        self.logger.info("Email alert configuration updated")

    def disable_email_notifications(self):
        """Disable email notifications"""
        self.alert_config["email_notifications"] = False
        self.logger.info("Email notifications disabled")

    def cleanup_old_alerts(self) -> int:
        """Remove old alert files based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.alert_config["alert_retention_days"])
        alert_files = list((self.storage_path / "Alerts").glob("ALERT_*.json"))

        deleted_count = 0
        for alert_file in alert_files:
            try:
                # Get the timestamp from the file
                with open(alert_file, 'r') as f:
                    alert_data = json.load(f)
                    file_timestamp = datetime.fromisoformat(alert_data["timestamp"])

                if file_timestamp < cutoff_date:
                    alert_file.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old alert file: {alert_file}")
            except Exception as e:
                self.logger.error(f"Error processing alert file {alert_file}: {str(e)}")

        return deleted_count

    def trigger_test_alert(self):
        """Trigger a test alert for verification"""
        self.create_alert(
            AlertLevel.INFO,
            AlertType.CUSTOM,
            "Test Alert",
            "This is a test alert to verify the alert system is functioning properly.",
            {
                "test_data": "This is sample test data",
                "system_time": datetime.now().isoformat()
            },
            [AlertChannel.CONSOLE, AlertChannel.VAULT_ACTION]
        )


async def test_alert_system():
    """Test the alert system"""
    print("Testing Alert System...")

    alert_system = AlertSystem()

    # Test creating different types of alerts
    print("\n1. Creating various alert types...")

    # Info alert
    info_id = alert_system.create_alert(
        AlertLevel.INFO,
        AlertType.SYSTEM_HEALTH,
        "System Status Check",
        "System health check completed successfully",
        {"cpu_usage": 45, "memory_usage": 60}
    )
    print(f"Info alert created: {info_id}")

    # Warning alert
    warning_id = alert_system.create_alert(
        AlertLevel.WARNING,
        AlertType.RESOURCE_USAGE,
        "High Memory Usage",
        "Memory usage is approaching warning threshold",
        {"current_usage": 85, "threshold": 80},
        [AlertChannel.VAULT_ACTION, AlertChannel.FILE]
    )
    print(f"Warning alert created: {warning_id}")

    # Critical alert
    critical_id = alert_system.create_alert(
        AlertLevel.CRITICAL,
        AlertType.MCP_SERVER,
        "MCP Server Down",
        "Email MCP server is not responding",
        {"server": "email_mcp", "port": 8068, "last_seen": "2026-01-29T10:30:00Z"},
        [AlertChannel.VAULT_ACTION, AlertChannel.CONSOLE]
    )
    print(f"Critical alert created: {critical_id}")

    # Get active alerts
    print("\n2. Getting active alerts...")
    active_alerts = alert_system.get_active_alerts()
    print(f"Active alerts count: {len(active_alerts)}")
    for alert in active_alerts:
        print(f"  - {alert['level'].upper()}: {alert['title']}")

    # Get alert history
    print("\n3. Getting alert history...")
    history = alert_system.get_alert_history(days=1)
    print(f"History count: {len(history)}")
    for alert in history[:3]:  # Show first 3
        print(f"  - {alert['timestamp'][:19]}: {alert['level'].upper()} - {alert['title']}")

    # Get alert summary
    print("\n4. Getting alert summary...")
    summary = alert_system.get_alert_summary()
    print(f"Summary: {summary}")

    # Resolve an alert
    print("\n5. Resolving an alert...")
    if warning_id:
        alert_system.resolve_alert(warning_id, "Memory usage returned to normal levels")
        print(f"Resolved alert: {warning_id}")

        # Verify it's resolved
        remaining_active = alert_system.get_active_alerts()
        print(f"Remaining active alerts: {len(remaining_active)}")

    # Trigger a test alert
    print("\n6. Triggering test alert...")
    alert_system.trigger_test_alert()

    # Show cleanup capability
    print(f"\n7. Would clean up alerts older than {alert_system.alert_config['alert_retention_days']} days")

    return True


if __name__ == "__main__":
    asyncio.run(test_alert_system())