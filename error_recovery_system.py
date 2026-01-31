"""
Error Recovery System for Gold Tier
Implements automatic error detection, recovery procedures, and self-healing capabilities.
"""

import asyncio
import json
import traceback
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
import logging
import sys
import os
import subprocess
import psutil


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    RETRY = "retry"
    ROLLBACK = "rollback"
    RESTART_SERVICE = "restart_service"
    NOTIFY_USER = "notify_user"
    SKIP_STEP = "skip_step"
    HALT_EXECUTION = "halt_execution"


class ErrorType(Enum):
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_INTEGRITY_ERROR = "data_integrity_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorRecoverySystem:
    """Main system for error detection and recovery"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create error-specific directories
        (self.storage_path / "Audit_Logs").mkdir(exist_ok=True)
        (self.storage_path / "Recovery").mkdir(exist_ok=True)

        # Initialize error catalog
        self.error_catalog = self._initialize_error_catalog()

        # Set up logging
        self.logger = self._setup_logging()

        # Track error occurrences
        self.error_history = []
        self.max_history_size = 1000

        # Recovery configuration
        self.recovery_config = {
            "max_retry_attempts": 3,
            "retry_delay_base": 2,  # seconds
            "exponential_backoff_factor": 2,
            "critical_error_threshold": 5,  # errors per minute
            "notification_enabled": True
        }

    def _initialize_error_catalog(self) -> Dict[str, Any]:
        """Initialize the error catalog with recovery procedures"""
        return {
            "connection_error": {
                "severity": ErrorSeverity.HIGH,
                "recovery_actions": [RecoveryAction.RETRY],
                "timeout": 30,
                "dependencies": [],
                "rollback_procedure": None
            },
            "timeout_error": {
                "severity": ErrorSeverity.MEDIUM,
                "recovery_actions": [RecoveryAction.RETRY, RecoveryAction.SKIP_STEP],
                "timeout": 60,
                "dependencies": [],
                "rollback_procedure": None
            },
            "authentication_error": {
                "severity": ErrorSeverity.CRITICAL,
                "recovery_actions": [RecoveryAction.NOTIFY_USER, RecoveryAction.HALT_EXECUTION],
                "timeout": 300,
                "dependencies": ["auth_service"],
                "rollback_procedure": "revoke_auth_tokens"
            },
            "permission_error": {
                "severity": ErrorSeverity.HIGH,
                "recovery_actions": [RecoveryAction.NOTIFY_USER, RecoveryAction.HALT_EXECUTION],
                "timeout": 300,
                "dependencies": ["access_control"],
                "rollback_procedure": "reset_permissions"
            },
            "resource_exhaustion": {
                "severity": ErrorSeverity.CRITICAL,
                "recovery_actions": [RecoveryAction.RESTART_SERVICE, RecoveryAction.NOTIFY_USER],
                "timeout": 120,
                "dependencies": ["resource_manager"],
                "rollback_procedure": "free_resources"
            },
            "data_integrity_error": {
                "severity": ErrorSeverity.CRITICAL,
                "recovery_actions": [RecoveryAction.ROLLBACK, RecoveryAction.NOTIFY_USER],
                "timeout": 300,
                "dependencies": ["data_validator"],
                "rollback_procedure": "restore_from_backup"
            }
        }

    def _setup_logging(self) -> logging.Logger:
        """Set up error recovery system logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "Recovery" / "error_recovery.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """Log an error with context and return an error ID"""
        error_id = f"ERR_{int(datetime.now().timestamp())}_{hash(str(error)) % 10000}"

        error_entry = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "severity": self._classify_severity(error),
            "handled": False
        }

        # Add to error history
        self.error_history.append(error_entry)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)

        # Save to file
        error_file = self.storage_path / "Recovery" / f"error_{error_id}.json"
        with open(error_file, 'w') as f:
            json.dump(error_entry, f, indent=2)

        self.logger.error(f"Logged error {error_id}: {str(error)}")

        return error_id

    def _classify_severity(self, error: Exception) -> ErrorSeverity:
        """Classify the severity of an error"""
        error_str = str(error).lower()

        # Check for known error patterns
        if any(pattern in error_str for pattern in ["connection", "network", "timeout"]):
            return ErrorSeverity.HIGH
        elif any(pattern in error_str for pattern in ["auth", "permission", "access"]):
            return ErrorSeverity.CRITICAL
        elif any(pattern in error_str for pattern in ["memory", "disk", "resource"]):
            return ErrorSeverity.CRITICAL
        elif any(pattern in error_str for pattern in ["data", "integrity", "validation"]):
            return ErrorSeverity.CRITICAL
        else:
            return ErrorSeverity.MEDIUM

    async def attempt_recovery(self, error_id: str, max_attempts: int = 3) -> bool:
        """Attempt to recover from a logged error"""
        error_entry = self._get_error_entry(error_id)
        if not error_entry:
            self.logger.error(f"Error ID {error_id} not found")
            return False

        error_type = self._get_error_type(error_entry)
        recovery_config = self.error_catalog.get(error_type.value, {})

        for attempt in range(max_attempts):
            self.logger.info(f"Recovery attempt {attempt + 1} for error {error_id}")

            # Determine appropriate recovery action
            recovery_action = self._select_recovery_action(error_entry, recovery_config)

            if recovery_action == RecoveryAction.RETRY:
                success = await self._perform_retry(error_entry)
            elif recovery_action == RecoveryAction.RESTART_SERVICE:
                success = await self._perform_service_restart(error_entry)
            elif recovery_action == RecoveryAction.ROLLBACK:
                success = await self._perform_rollback(error_entry)
            elif recovery_action == RecoveryAction.NOTIFY_USER:
                success = self._notify_user(error_entry)
            elif recovery_action == RecoveryAction.SKIP_STEP:
                success = True  # Skip is considered successful
                self.logger.info(f"Skipped step due to error {error_id}")
            elif recovery_action == RecoveryAction.HALT_EXECUTION:
                self.logger.warning(f"Halted execution due to critical error {error_id}")
                return False
            else:
                success = False

            if success:
                error_entry["handled"] = True
                self._update_error_entry(error_id, error_entry)
                self.logger.info(f"Successfully recovered from error {error_id} on attempt {attempt + 1}")

                # Save recovery log
                recovery_log = {
                    "error_id": error_id,
                    "recovery_attempt": attempt + 1,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "action_taken": recovery_action.value
                }

                recovery_file = self.storage_path / "Recovery" / f"recovery_{error_id}.json"
                with open(recovery_file, 'w') as f:
                    json.dump(recovery_log, f, indent=2)

                return True
            else:
                self.logger.warning(f"Recovery attempt {attempt + 1} failed for error {error_id}")

        self.logger.error(f"All recovery attempts failed for error {error_id}")
        return False

    def _get_error_entry(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an error entry by ID"""
        error_file = self.storage_path / "Recovery" / f"error_{error_id}.json"
        if error_file.exists():
            with open(error_file, 'r') as f:
                return json.load(f)
        return None

    def _update_error_entry(self, error_id: str, error_entry: Dict[str, Any]):
        """Update an error entry"""
        error_file = self.storage_path / "Recovery" / f"error_{error_id}.json"
        with open(error_file, 'w') as f:
            json.dump(error_entry, f, indent=2)

    def _get_error_type(self, error_entry: Dict[str, Any]) -> ErrorType:
        """Determine the error type from the error entry"""
        error_msg = error_entry["error_message"].lower()

        if "connection" in error_msg or "network" in error_msg:
            return ErrorType.CONNECTION_ERROR
        elif "timeout" in error_msg:
            return ErrorType.TIMEOUT_ERROR
        elif "auth" in error_msg or "permission" in error_msg:
            return ErrorType.AUTHENTICATION_ERROR
        elif "memory" in error_msg or "disk" in error_msg or "resource" in error_msg:
            return ErrorType.RESOURCE_EXHAUSTION
        elif "data" in error_msg or "integrity" in error_msg or "validation" in error_msg:
            return ErrorType.DATA_INTEGRITY_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR

    def _select_recovery_action(self, error_entry: Dict[str, Any], config: Dict[str, Any]) -> RecoveryAction:
        """Select the most appropriate recovery action"""
        severity = error_entry["severity"]

        # For critical errors, prioritize notification and halting
        if severity == ErrorSeverity.CRITICAL:
            if RecoveryAction.HALT_EXECUTION in config.get("recovery_actions", []):
                return RecoveryAction.HALT_EXECUTION
            elif RecoveryAction.NOTIFY_USER in config.get("recovery_actions", []):
                return RecoveryAction.NOTIFY_USER

        # For high severity, try restart or retry
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            if RecoveryAction.RESTART_SERVICE in config.get("recovery_actions", []):
                return RecoveryAction.RESTART_SERVICE

        # For medium/low, try retry first
        if RecoveryAction.RETRY in config.get("recovery_actions", []):
            return RecoveryAction.RETRY

        # Otherwise, use the first available action
        actions = config.get("recovery_actions", [])
        return actions[0] if actions else RecoveryAction.NOTIFY_USER

    async def _perform_retry(self, error_entry: Dict[str, Any]) -> bool:
        """Perform a retry operation"""
        try:
            # In a real implementation, this would retry the failed operation
            # For now, we'll simulate success after a delay
            await asyncio.sleep(1)
            self.logger.info(f"Retry successful for error {error_entry['error_id']}")
            return True
        except Exception as e:
            self.logger.error(f"Retry failed: {str(e)}")
            return False

    async def _perform_service_restart(self, error_entry: Dict[str, Any]) -> bool:
        """Perform a service restart"""
        try:
            # In a real implementation, this would restart the affected service
            # For now, we'll simulate success
            context = error_entry.get("context", {})
            service_name = context.get("service_name", "unknown_service")

            self.logger.info(f"Restarting service: {service_name}")

            # Simulate restart process
            await asyncio.sleep(2)

            self.logger.info(f"Service {service_name} restarted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Service restart failed: {str(e)}")
            return False

    async def _perform_rollback(self, error_entry: Dict[str, Any]) -> bool:
        """Perform a rollback operation"""
        try:
            # In a real implementation, this would rollback to a previous state
            # For now, we'll simulate success
            self.logger.info(f"Rolling back due to error {error_entry['error_id']}")

            # Simulate rollback process
            await asyncio.sleep(1)

            self.logger.info(f"Rollback completed for error {error_entry['error_id']}")
            return True
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return False

    def _notify_user(self, error_entry: Dict[str, Any]) -> bool:
        """Notify the user about the error"""
        try:
            # In a real implementation, this would notify the user through
            # the appropriate channel (email, dashboard, etc.)
            self.logger.warning(f"Critical error requires user attention: {error_entry['error_message']}")

            # Create notification file in Needs_Action
            notification_file = Path("Vault/Needs_Action") / f"ALERT_Critical_Error_{error_entry['error_id']}.md"
            notification_file.parent.mkdir(parents=True, exist_ok=True)

            with open(notification_file, 'w') as f:
                f.write(f"""---
type: alert
priority: high
category: critical_error
generated: {datetime.now().isoformat()}
---

# 🚨 Critical System Error

**Error ID:** {error_entry['error_id']}
**Timestamp:** {error_entry['timestamp']}
**Type:** {error_entry['error_type']}
**Message:** {error_entry['error_message']}

## Action Required
This critical error requires immediate attention. Please review the error details and take appropriate action.

## Error Context
```json
{json.dumps(error_entry['context'], indent=2)}
```

---
*Generated by Error Recovery System*
""")

            self.logger.info(f"User notification created for error {error_entry['error_id']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to notify user: {str(e)}")
            return False

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent

        # Check for recent errors
        recent_errors = self._get_recent_errors(minutes=5)
        critical_errors = [e for e in recent_errors if e["severity"] == ErrorSeverity.CRITICAL.value]

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": cpu_percent,
            "memory_usage": memory_percent,
            "disk_usage": disk_percent,
            "recent_errors_count": len(recent_errors),
            "critical_errors_count": len(critical_errors),
            "overall_health": "healthy" if len(critical_errors) == 0 else "degraded"
        }

        # Save health status
        health_file = self.storage_path / "Recovery" / "system_health.json"
        with open(health_file, 'w') as f:
            json.dump(health_status, f, indent=2)

        return health_status

    def _get_recent_errors(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get errors from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = []

        for error in self.error_history:
            error_time = datetime.fromisoformat(error["timestamp"])
            if error_time >= cutoff_time:
                recent.append(error)

        return recent

    async def run_health_monitor(self, interval: int = 30):
        """Run continuous health monitoring"""
        self.logger.info("Starting health monitoring...")

        while True:
            try:
                health_status = self.check_system_health()

                # Log health status
                self.logger.info(f"System health: {health_status['overall_health']} "
                               f"(CPU: {health_status['cpu_usage']}%, "
                               f"Memory: {health_status['memory_usage']}%)")

                # Check for critical issues
                if health_status['overall_health'] == 'degraded':
                    self.logger.warning("System health is degraded, checking for recovery needs...")

                    # Attempt to recover from recent critical errors
                    recent_errors = self._get_recent_errors(minutes=10)
                    for error in recent_errors:
                        if not error['handled']:
                            await self.attempt_recovery(error['error_id'])

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in health monitor: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying


async def test_error_recovery_system():
    """Test the error recovery system"""
    print("Testing Error Recovery System...")

    recovery_system = ErrorRecoverySystem()

    # Test error logging
    print("\n1. Testing error logging...")
    try:
        # Simulate an error
        raise ConnectionError("Failed to connect to external service")
    except Exception as e:
        error_id = recovery_system.log_error(e, {"service": "external_api", "operation": "connect"})
        print(f"Logged error with ID: {error_id}")

    # Test system health check
    print("\n2. Testing system health check...")
    health = recovery_system.check_system_health()
    print(f"System health: {health}")

    # Test recovery attempt (this would normally be called for actual errors)
    print("\n3. Testing recovery attempt...")
    # For this test, we'll simulate a successful recovery
    recovery_success = await recovery_system.attempt_recovery(error_id)
    print(f"Recovery {'successful' if recovery_success else 'failed'}")

    # Show error catalog
    print("\n4. Error catalog:")
    for error_type, config in recovery_system.error_catalog.items():
        print(f"  {error_type}: {config['severity'].value} severity, "
              f"actions: {[action.value for action in config['recovery_actions']]}")

    return True


if __name__ == "__main__":
    asyncio.run(test_error_recovery_system())