#!/usr/bin/env python3
"""
Error Handler Script
Monitors logs for errors and implements recovery procedures
"""

import json
import os
import time
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
import requests


# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/AI_Employee_Vault'))
LOG_DIR = VAULT_PATH / 'Logs'
INCIDENT_LOG_DIR = LOG_DIR / 'system' / 'incidents'

# Error classification
ERROR_CATALOG = {
    'PROC_CRASH': {'severity': 'HIGH', 'category': 'process', 'max_attempts': 3},
    'PROC_UNRESPONSIVE': {'severity': 'MEDIUM', 'category': 'process', 'max_attempts': 2},
    'API_AUTH_FAILURE': {'severity': 'HIGH', 'category': 'api', 'max_attempts': 2},
    'API_RATE_LIMIT': {'severity': 'MEDIUM', 'category': 'api', 'max_attempts': 0},
    'API_TIMEOUT': {'severity': 'MEDIUM', 'category': 'api', 'max_attempts': 3},
    'NET_CONNECTION_FAILED': {'severity': 'CRITICAL', 'category': 'network', 'max_attempts': 5},
    'FS_DISK_FULL': {'severity': 'CRITICAL', 'category': 'filesystem', 'max_attempts': 1},
    'FS_VAULT_LOCKED': {'severity': 'HIGH', 'category': 'filesystem', 'max_attempts': 5},
}


class ErrorHandler:
    def __init__(self):
        self.recovery_attempts = {}  # Track attempts per error
        INCIDENT_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def scan_for_errors(self, hours: int = 1) -> List[Dict]:
        """Scan recent logs for errors"""
        errors = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Check system logs
        system_log_files = list(LOG_DIR.glob('system/*.json'))
        for log_file in system_log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))

                            if entry_time > cutoff_time and entry.get('severity') in ['HIGH', 'CRITICAL']:
                                errors.append(entry)
                        except:
                            continue
            except:
                continue

        return errors

    def classify_error(self, error: Dict) -> Dict:
        """Classify error and determine recovery strategy"""
        error_code = error.get('error_code', 'UNKNOWN')

        if error_code in ERROR_CATALOG:
            return ERROR_CATALOG[error_code]
        else:
            # Unknown error - conservative approach
            return {
                'severity': 'MEDIUM',
                'category': 'unknown',
                'max_attempts': 1
            }

    def attempt_recovery(self, error: Dict) -> bool:
        """Attempt to recover from error"""
        error_type = error.get('error_code', error.get('event_type', 'UNKNOWN'))
        classification = self.classify_error(error)

        # Track attempts
        error_key = f"{error_type}_{error.get('component', 'unknown')}"
        if error_key not in self.recovery_attempts:
            self.recovery_attempts[error_key] = {'count': 0, 'last_attempt': None}

        attempt_info = self.recovery_attempts[error_key]

        # Check if we've exceeded max attempts
        if attempt_info['count'] >= classification['max_attempts']:
            self.log_event('recovery_max_attempts_exceeded', error, {
                'attempts': attempt_info['count'],
                'max_attempts': classification['max_attempts']
            })
            return False

        # Attempt recovery based on error type
        success = False
        recovery_method = None

        if classification['category'] == 'process':
            success, recovery_method = self.recover_process_error(error)
        elif classification['category'] == 'api':
            success, recovery_method = self.recover_api_error(error)
        elif classification['category'] == 'network':
            success, recovery_method = self.recover_network_error(error)
        elif classification['category'] == 'filesystem':
            success, recovery_method = self.recover_filesystem_error(error)

        # Update attempt tracking
        attempt_info['count'] += 1
        attempt_info['last_attempt'] = datetime.now(timezone.utc)

        # Log recovery attempt
        self.log_event('recovery_attempt', error, {
            'success': success,
            'method': recovery_method,
            'attempt_number': attempt_info['count'],
            'max_attempts': classification['max_attempts']
        })

        # Reset counter on success
        if success:
            attempt_info['count'] = 0

        return success

    def recover_process_error(self, error: Dict) -> tuple:
        """Recover from process errors"""
        component = error.get('component', '')

        # Wait for exponential backoff
        attempt_num = self.recovery_attempts.get(
            f"{error.get('error_code', '')}_{component}",
            {'count': 0}
        )['count']
        wait_time = min(5 * (2 ** attempt_num), 60)  # Max 60 seconds
        time.sleep(wait_time)

        # Attempt to restart process
        try:
            # This is a simplified restart - adjust based on actual process management
            script_path = f"{component}.py"
            if os.path.exists(script_path):
                subprocess.Popen(['python3', script_path])
                time.sleep(5)  # Wait for startup

                # Verify process started
                pid_file = f'/tmp/{component}.pid'
                if os.path.exists(pid_file):
                    return True, 'auto_restart'

        except Exception as e:
            self.log_event('recovery_failed', error, {'exception': str(e)})

        return False, 'auto_restart_failed'

    def recover_api_error(self, error: Dict) -> tuple:
        """Recover from API errors"""
        error_code = error.get('error_code', '')

        if error_code == 'API_AUTH_FAILURE':
            # Attempt token refresh
            api = error.get('metadata', {}).get('api', '')
            success = self.refresh_api_token(api)
            return success, 'token_refresh' if success else 'token_refresh_failed'

        elif error_code == 'API_RATE_LIMIT':
            # Queue operation for later (no immediate recovery)
            retry_after = error.get('metadata', {}).get('retry_after_seconds', 900)
            self.queue_operation(error, retry_after)
            return True, 'queued_for_retry'

        elif error_code == 'API_TIMEOUT':
            # Retry with exponential backoff
            attempt_num = self.recovery_attempts.get(
                f"API_TIMEOUT_{error.get('component', '')}",
                {'count': 0}
            )['count']
            wait_time = min(2 ** attempt_num, 30)
            time.sleep(wait_time)
            return True, 'retry_with_backoff'

        return False, 'no_recovery_method'

    def recover_network_error(self, error: Dict) -> tuple:
        """Recover from network errors"""
        # Test connectivity
        try:
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code == 200:
                return True, 'network_restored'
        except:
            pass

        # Queue operations if network still down
        self.queue_operation(error, retry_after=300)  # Retry in 5 minutes
        return False, 'network_still_down_queued'

    def recover_filesystem_error(self, error: Dict) -> tuple:
        """Recover from filesystem errors"""
        error_code = error.get('error_code', '')

        if error_code == 'FS_DISK_FULL':
            # Attempt cleanup
            freed = self.cleanup_disk_space()
            return freed > 0, f'cleanup_freed_{freed}MB'

        elif error_code == 'FS_VAULT_LOCKED':
            # Wait and retry
            time.sleep(60)
            try:
                test_file = VAULT_PATH / '.access_test'
                test_file.write_text('test')
                test_file.unlink()
                return True, 'vault_access_restored'
            except:
                return False, 'vault_still_locked'

        return False, 'no_recovery_method'

    def refresh_api_token(self, api_name: str) -> bool:
        """Attempt to refresh API token"""
        # This is a simplified implementation
        # In production, implement actual OAuth refresh logic per API
        try:
            if api_name == 'gmail':
                # Gmail token refresh logic
                # Would use google-auth library to refresh
                pass
            elif api_name == 'xero':
                # Xero token refresh logic
                pass

            return False  # Not implemented yet
        except Exception as e:
            return False

    def queue_operation(self, error: Dict, retry_after: int):
        """Queue failed operation for retry later"""
        queue_file = VAULT_PATH / 'Logs' / 'system' / 'operation_queue.json'

        operation = {
            'queued_at': datetime.now(timezone.utc).isoformat(),
            'retry_after': retry_after,
            'retry_at': (datetime.now(timezone.utc) + timedelta(seconds=retry_after)).isoformat(),
            'error': error
        }

        # Append to queue
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(queue_file, 'a') as f:
            f.write(json.dumps(operation) + '\n')

    def cleanup_disk_space(self) -> int:
        """Cleanup disk space, return MB freed"""
        freed_mb = 0

        try:
            # 1. Compress old logs
            import gzip
            import shutil

            for log_file in LOG_DIR.rglob('*.json'):
                age_days = (time.time() - log_file.stat().st_mtime) / 86400
                if age_days > 30 and not str(log_file).endswith('.gz'):
                    original_size = log_file.stat().st_size
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(f'{log_file}.gz', 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    log_file.unlink()
                    compressed_size = Path(f'{log_file}.gz').stat().st_size
                    freed_mb += (original_size - compressed_size) / (1024 * 1024)

            # 2. Clean temp files
            temp_dir = Path('/tmp')
            for temp_file in temp_dir.glob('*.tmp'):
                if temp_file.is_file():
                    size = temp_file.stat().st_size
                    temp_file.unlink()
                    freed_mb += size / (1024 * 1024)

        except Exception as e:
            self.log_event('cleanup_error', {}, {'exception': str(e)})

        return int(freed_mb)

    def escalate_error(self, error: Dict, reason: str):
        """Escalate error to user"""
        alert_file = VAULT_PATH / 'Needs_Action' / f"ALERT_ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        alert_content = f"""---
type: error_alert
severity: {error.get('severity', 'HIGH')}
error_code: {error.get('error_code', 'UNKNOWN')}
component: {error.get('component', 'unknown')}
created: {datetime.now(timezone.utc).isoformat()}
---

# ⚠️ Error Recovery Failed

**Error:** {error.get('error_code', 'Unknown Error')}
**Component:** {error.get('component', 'Unknown')}
**Escalation Reason:** {reason}

## Error Details

```json
{json.dumps(error, indent=2)}
```

## Recovery Attempts

Auto-recovery was attempted but failed. Manual intervention required.

## Recommended Actions

1. Check component logs
2. Verify service configuration
3. Restart component manually if needed
4. Review error-catalog.md for detailed recovery steps

---
*Generated by monitor-system skill*
"""

        alert_file.parent.mkdir(parents=True, exist_ok=True)
        alert_file.write_text(alert_content)

    def log_event(self, event_type: str, original_error: Dict, metadata: Dict):
        """Log recovery event"""
        today = datetime.now().strftime('%Y-%m-%d')
        incident_log = INCIDENT_LOG_DIR / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'log_type': 'system',
            'event_type': event_type,
            'severity': original_error.get('severity', 'MEDIUM'),
            'actor': 'error_handler',
            'status': metadata.get('success', False) and 'success' or 'failed',
            'original_error': original_error,
            'metadata': metadata
        }

        with open(incident_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    """Main error handling execution"""
    handler = ErrorHandler()

    # Scan for recent errors
    errors = handler.scan_for_errors(hours=1)

    if not errors:
        print("No errors detected in last hour")
        return

    print(f"Found {len(errors)} errors to process")

    # Process each error
    for error in errors:
        print(f"Processing: {error.get('error_code', 'UNKNOWN')} - {error.get('component', 'unknown')}")

        # Attempt recovery
        success = handler.attempt_recovery(error)

        if not success:
            # Check if we should escalate
            error_key = f"{error.get('error_code', '')}_{error.get('component', '')}"
            attempt_info = handler.recovery_attempts.get(error_key, {'count': 0})
            classification = handler.classify_error(error)

            if attempt_info['count'] >= classification['max_attempts']:
                print(f"  Escalating: Max recovery attempts exceeded")
                handler.escalate_error(error, 'Max recovery attempts exceeded')
            else:
                print(f"  Recovery failed: Will retry (attempt {attempt_info['count']}/{classification['max_attempts']})")
        else:
            print(f"  Recovery successful")


if __name__ == '__main__':
    main()
