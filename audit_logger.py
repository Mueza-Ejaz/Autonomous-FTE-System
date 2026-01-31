"""
Audit Logger for Gold Tier
Comprehensive audit logging system for tracking all actions and maintaining compliance.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import hashlib
import hmac
from enum import Enum


class AuditEventType(Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    FILE_ACCESS = "file_access"
    FILE_MODIFICATION = "file_modification"
    API_CALL = "api_call"
    CONFIG_CHANGE = "config_change"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    ERROR_OCCURRED = "error_occurred"
    SECURITY_ALERT = "security_alert"


class AuditLogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogger:
    """Comprehensive audit logging system"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security/Audit_Logs"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Initialize audit log files
        self.daily_log_file = self._get_daily_log_file()

        # Encryption key for sensitive data (in a real system, this would be securely stored)
        self.encryption_key = "audit_key_default"  # This should be replaced with secure key management

        # Log retention settings
        self.retention_days = 365  # Keep logs for 1 year
        self.max_file_size_mb = 100  # Rotate files at 100MB

    def _setup_logging(self) -> logging.Logger:
        """Set up audit logger"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "audit_logger.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _get_daily_log_file(self) -> Path:
        """Get the current daily log file"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.storage_path / f"audit_log_{date_str}.jsonl"

    def _rotate_log_if_needed(self):
        """Rotate log file if it exceeds size limit"""
        if self.daily_log_file.exists() and self.daily_log_file.stat().st_size > self.max_file_size_mb * 1024 * 1024:
            # Create new log file for today
            self.daily_log_file = self._get_daily_log_file()

    def _hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data before logging"""
        return hashlib.sha256(data.encode()).hexdigest()

    def _mask_sensitive_fields(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields in event data"""
        masked_data = event_data.copy()

        sensitive_fields = [
            "password", "token", "secret", "key", "credential", "api_key",
            "access_token", "refresh_token", "private_key", "certificate"
        ]

        for key, value in masked_data.items():
            if isinstance(value, str):
                for field in sensitive_fields:
                    if field in key.lower():
                        masked_data[key] = self._hash_sensitive_data(value)

        return masked_data

    def log_event(self,
                  event_type: AuditEventType,
                  user_id: str,
                  action: str,
                  resource: str,
                  details: Dict[str, Any] = None,
                  severity: AuditLogLevel = AuditLogLevel.INFO,
                  ip_address: str = None,
                  user_agent: str = None) -> str:
        """Log an audit event"""
        self._rotate_log_if_needed()

        # Create event ID
        event_id = f"audit_{int(datetime.now().timestamp())}_{hash(action) % 10000}"

        # Prepare event data
        event_data = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "severity": severity.value,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": details.get("session_id") if details else None,
            "details": self._mask_sensitive_fields(details or {}),
            "correlation_id": details.get("correlation_id") if details else None
        }

        # Add HMAC signature for integrity
        signature = self._create_signature(event_data)
        event_data["signature"] = signature

        # Write to daily log file
        with open(self.daily_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event_data) + '\n')

        # Log to system logger as well
        self.logger.info(f"AUDIT: {event_type.value} - {user_id} - {action}")

        return event_id

    def _create_signature(self, event_data: Dict[str, Any]) -> str:
        """Create HMAC signature for event integrity"""
        # Remove signature from data to be signed (if it exists)
        data_to_sign = {k: v for k, v in event_data.items() if k != 'signature'}
        data_str = json.dumps(data_to_sign, sort_keys=True)
        signature = hmac.new(
            self.encryption_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_log_integrity(self, log_file_path: str) -> Dict[str, Any]:
        """Verify the integrity of a log file"""
        results = {
            "file_path": log_file_path,
            "verified_entries": 0,
            "invalid_entries": 0,
            "tampered_entries": [],
            "total_entries": 0
        }

        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event_data = json.loads(line)
                        results["total_entries"] += 1

                        # Verify signature
                        original_signature = event_data.get('signature')
                        if original_signature:
                            # Remove signature temporarily to verify
                            temp_data = {k: v for k, v in event_data.items() if k != 'signature'}
                            expected_signature = self._create_signature(temp_data)

                            if hmac.compare_digest(original_signature, expected_signature):
                                results["verified_entries"] += 1
                            else:
                                results["invalid_entries"] += 1
                                results["tampered_entries"].append({
                                    "line_number": line_num,
                                    "event_id": event_data.get("event_id", "unknown")
                                })
                        else:
                            results["invalid_entries"] += 1
                            results["tampered_entries"].append({
                                "line_number": line_num,
                                "event_id": event_data.get("event_id", "unknown")
                            })

                    except json.JSONDecodeError:
                        results["invalid_entries"] += 1
                        results["tampered_entries"].append({
                            "line_number": line_num,
                            "error": "Invalid JSON"
                        })

        except FileNotFoundError:
            results["error"] = f"File not found: {log_file_path}"
        except Exception as e:
            results["error"] = f"Error verifying log: {str(e)}"

        return results

    def search_events(self,
                     event_types: List[AuditEventType] = None,
                     user_id: str = None,
                     date_range: tuple = None,
                     resource: str = None,
                     severity: AuditLogLevel = None) -> List[Dict[str, Any]]:
        """Search audit events based on criteria"""
        results = []

        # Determine which log files to search
        log_files = self._get_log_files_in_range(date_range)

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            event_data = json.loads(line)

                            # Apply filters
                            if event_types and event_data.get("event_type") not in [et.value for et in event_types]:
                                continue
                            if user_id and event_data.get("user_id") != user_id:
                                continue
                            if resource and resource not in event_data.get("resource", ""):
                                continue
                            if severity and event_data.get("severity") != severity.value:
                                continue

                            # Check date range
                            if date_range:
                                event_time = datetime.fromisoformat(event_data["timestamp"])
                                if not (date_range[0] <= event_time <= date_range[1]):
                                    continue

                            results.append(event_data)

                        except json.JSONDecodeError:
                            continue

            except FileNotFoundError:
                continue

        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

    def _get_log_files_in_range(self, date_range: tuple) -> List[Path]:
        """Get log files within the specified date range"""
        if not date_range:
            # Return all log files
            return list(self.storage_path.glob("audit_log_*.jsonl"))

        start_date, end_date = date_range
        log_files = []

        # Generate date range
        current_date = start_date.date()
        while current_date <= end_date.date():
            date_str = current_date.strftime("%Y-%m-%d")
            log_file = self.storage_path / f"audit_log_{date_str}.jsonl"
            if log_file.exists():
                log_files.append(log_file)
            current_date += timedelta(days=1)

        return log_files

    def generate_compliance_report(self,
                                  start_date: datetime,
                                  end_date: datetime,
                                  report_format: str = "json") -> str:
        """Generate compliance report for the specified period"""
        events = self.search_events(date_range=(start_date, end_date))

        # Categorize events by type
        event_counts = {}
        user_activity = {}
        suspicious_activities = []

        for event in events:
            event_type = event["event_type"]
            user_id = event["user_id"]

            # Count event types
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

            # Track user activity
            if user_id not in user_activity:
                user_activity[user_id] = {"events": 0, "activities": set()}
            user_activity[user_id]["events"] += 1
            user_activity[user_id]["activities"].add(event_type)

            # Flag suspicious activities
            if event["severity"] in ["warn", "error", "critical"]:
                suspicious_activities.append(event)

        report_data = {
            "report_date": datetime.now().isoformat(),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_events": len(events),
            "event_counts": event_counts,
            "unique_users": len(user_activity),
            "user_activity": {
                uid: {"event_count": data["events"], "activities": list(data["activities"])}
                for uid, data in user_activity.items()
            },
            "suspicious_activities_count": len(suspicious_activities),
            "suspicious_activities": suspicious_activities[:10],  # Limit to first 10
            "compliance_status": "pass" if len(suspicious_activities) < len(events) * 0.05 else "fail"  # Pass if <5% suspicious
        }

        # Save report
        report_filename = f"compliance_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{report_format}"
        report_file = self.storage_path / "reports" / report_filename
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        return str(report_file)

    def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get activity summary for a specific user"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        events = self.search_events(
            user_id=user_id,
            date_range=(start_date, end_date)
        )

        # Analyze user activity
        activity_by_type = {}
        resources_accessed = set()
        daily_activity = {}

        for event in events:
            event_type = event["event_type"]
            activity_by_type[event_type] = activity_by_type.get(event_type, 0) + 1

            resource = event.get("resource", "")
            if resource:
                resources_accessed.add(resource)

            # Group by day
            day = event["timestamp"][:10]  # YYYY-MM-DD
            daily_activity[day] = daily_activity.get(day, 0) + 1

        summary = {
            "user_id": user_id,
            "period_days": days,
            "total_events": len(events),
            "activity_by_type": activity_by_type,
            "unique_resources_accessed": len(resources_accessed),
            "daily_activity_pattern": daily_activity,
            "peak_activity_day": max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None,
            "average_daily_events": len(events) / days if days > 0 else 0
        }

        return summary

    def cleanup_old_logs(self, retention_days: int = None) -> int:
        """Clean up audit logs older than retention period"""
        if retention_days is None:
            retention_days = self.retention_days

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        log_files = list(self.storage_path.glob("audit_log_*.jsonl"))

        deleted_count = 0
        for log_file in log_files:
            # Extract date from filename
            date_part = log_file.stem.split('_')[-1]  # audit_log_YYYY-MM-DD
            try:
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old audit log: {log_file}")
            except ValueError:
                # Skip files with invalid date format
                continue

        return deleted_count

    def export_logs(self,
                   start_date: datetime,
                   end_date: datetime,
                   export_format: str = "jsonl",
                   include_sensitive: bool = False) -> str:
        """Export audit logs for external analysis"""
        events = self.search_events(date_range=(start_date, end_date))

        if not include_sensitive:
            # Remove sensitive information
            for event in events:
                if "details" in event:
                    event["details"] = self._remove_sensitive_data(event["details"])

        export_filename = f"audit_export_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{export_format}"
        export_file = self.storage_path / "exports" / export_filename
        export_file.parent.mkdir(exist_ok=True)

        if export_format == "jsonl":
            with open(export_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + '\n')
        elif export_format == "json":
            with open(export_file, 'w') as f:
                json.dump(events, f, indent=2)

        self.logger.info(f"Exported {len(events)} audit events to {export_file}")
        return str(export_file)

    def _remove_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from exported logs"""
        if not isinstance(data, dict):
            return data

        cleaned_data = {}
        sensitive_keywords = ["password", "token", "secret", "key", "credential", "api_key"]

        for key, value in data.items():
            if isinstance(value, dict):
                cleaned_data[key] = self._remove_sensitive_data(value)
            elif any(keyword in key.lower() for keyword in sensitive_keywords):
                cleaned_data[key] = "[REDACTED]"
            else:
                cleaned_data[key] = value

        return cleaned_data


async def test_audit_logger():
    """Test the audit logger"""
    print("Testing Audit Logger...")

    logger = AuditLogger()

    # Test logging different types of events
    print("\n1. Logging various audit events...")

    # Log a file access event
    event1_id = logger.log_event(
        AuditEventType.FILE_ACCESS,
        "user123",
        "read",
        "Vault/Config/config.json",
        {
            "file_size": 1024,
            "session_id": "sess_abc123",
            "correlation_id": "corr_xyz789"
        },
        AuditLogLevel.INFO,
        "192.168.1.100",
        "Mozilla/5.0..."
    )
    print(f"File access event logged: {event1_id}")

    # Log a config change event
    event2_id = logger.log_event(
        AuditEventType.CONFIG_CHANGE,
        "admin456",
        "update",
        "System_Config",
        {
            "changed_field": "max_users",
            "old_value": 100,
            "new_value": 200,
            "reason": "Business growth"
        },
        AuditLogLevel.WARN,
        "192.168.1.1",
        "Admin_Tool/1.0"
    )
    print(f"Config change event logged: {event2_id}")

    # Log a security alert
    event3_id = logger.log_event(
        AuditEventType.SECURITY_ALERT,
        "system",
        "detected_unusual_activity",
        "User_Account/user123",
        {
            "activity_type": "multiple_failed_logins",
            "attempt_count": 15,
            "time_window_minutes": 10,
            "geographic_anomaly": True
        },
        AuditLogLevel.CRITICAL,
        "203.0.113.45",
        "Unknown"
    )
    print(f"Security alert logged: {event3_id}")

    # Search for events
    print("\n2. Searching for events...")
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=1)

    recent_events = logger.search_events(
        date_range=(start_date, end_date),
        severity=AuditLogLevel.INFO
    )
    print(f"Found {len(recent_events)} recent INFO events")

    # Get user activity summary
    print("\n3. Getting user activity summary...")
    user_summary = logger.get_user_activity_summary("user123", days=7)
    print(f"User activity summary: {user_summary['total_events']} events in last 7 days")

    # Generate compliance report
    print("\n4. Generating compliance report...")
    report_file = logger.generate_compliance_report(start_date, end_date)
    print(f"Compliance report generated: {report_file}")

    # Verify log integrity
    print("\n5. Verifying log integrity...")
    daily_log = logger._get_daily_log_file()
    if daily_log.exists():
        integrity_check = logger.verify_log_integrity(daily_log)
        print(f"Log integrity check: {integrity_check['verified_entries']} verified, {integrity_check['invalid_entries']} invalid")

    # Export logs
    print("\n6. Exporting logs...")
    export_file = logger.export_logs(start_date, end_date, export_format="jsonl")
    print(f"Logs exported to: {export_file}")

    # Show log cleanup capability
    print(f"\n7. Would clean up logs older than {logger.retention_days} days")

    return True


if __name__ == "__main__":
    asyncio.run(test_audit_logger())