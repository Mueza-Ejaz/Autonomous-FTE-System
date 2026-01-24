# Audit Log Schema

**Version:** 1.0
**Last Updated:** 2026-01-12
**Purpose:** Comprehensive logging schema with retention policies and analysis guidelines

---

## Overview

All AI Employee actions must be logged in structured JSON format. This provides:
- Complete audit trail of all system activities
- Debugging information for errors
- Business intelligence data
- Compliance documentation
- Security monitoring

**Logging Principles:**
1. **Log everything** - Every action, decision, and error
2. **Structured data** - Always JSON, never plain text
3. **Consistent schema** - Use standard fields
4. **Privacy aware** - Redact sensitive data
5. **Performance conscious** - Async logging, no blocking

---

## Log Directory Structure

```
Vault/Logs/
├── actions/                    # All AI actions
│   ├── 2026-01-12.json
│   ├── 2026-01-11.json
│   └── archives/              # Compressed old logs
│       ├── 2025-12.tar.gz
│       └── 2025-11.tar.gz
├── system/                     # System health & errors
│   ├── health_checks.json     # Continuous health log
│   ├── incidents/
│   │   ├── 2026-01-12.json
│   │   └── archives/
│   └── archives/
├── financial/                  # Financial transactions
│   ├── 2026-01.json
│   └── archives/
└── security/                   # Auth, access, sensitive ops
    ├── 2026-01.json
    └── archives/
```

---

## Standard Log Entry Format

**Base Schema (all log entries must have these fields):**

```json
{
  "timestamp": "2026-01-12T10:30:00.123Z",
  "log_type": "action|system|financial|security",
  "event_type": "specific_event_name",
  "severity": "low|medium|high|critical",
  "actor": "claude_code|watcher|mcp_server|user",
  "status": "success|failed|pending|in_progress",
  "metadata": {}
}
```

**Field Definitions:**
- `timestamp`: ISO 8601 format with milliseconds, UTC timezone
- `log_type`: Category of log (routes to correct log file)
- `event_type`: Specific event identifier (see taxonomy below)
- `severity`: Impact level (for filtering and alerting)
- `actor`: What/who performed the action
- `status`: Outcome of the action
- `metadata`: Event-specific additional data

---

## Log Type Schemas

### 1. Action Logs (actions/YYYY-MM-DD.json)

**Purpose:** Record all AI actions (emails, posts, file operations, etc.)

**Schema:**
```json
{
  "timestamp": "2026-01-12T10:30:00.123Z",
  "log_type": "action",
  "event_type": "email_sent|post_created|file_processed|task_completed",
  "severity": "low",
  "actor": "claude_code",
  "status": "success",
  "action_category": "communication|social_media|file_ops|task_mgmt",
  "target": "recipient@example.com",
  "skill_used": "process-emails",
  "approval_required": true,
  "approval_status": "approved|rejected|pending",
  "approved_by": "human",
  "cost_estimate": 0.025,
  "metadata": {
    "subject": "Invoice #12345",
    "attachments": ["invoice.pdf"],
    "trigger": "gmail_watcher",
    "processing_time_ms": 1234
  }
}
```

**Example - Email Sent:**
```json
{
  "timestamp": "2026-01-12T14:23:15.678Z",
  "log_type": "action",
  "event_type": "email_sent",
  "severity": "low",
  "actor": "claude_code",
  "status": "success",
  "action_category": "communication",
  "target": "client@example.com",
  "skill_used": "process-emails",
  "approval_required": true,
  "approval_status": "approved",
  "approved_by": "human",
  "cost_estimate": 0.02,
  "metadata": {
    "subject": "Re: Project Update",
    "attachments": [],
    "trigger": "gmail_watcher",
    "processing_time_ms": 2341,
    "email_id": "MSG_12345"
  }
}
```

**Example - LinkedIn Post:**
```json
{
  "timestamp": "2026-01-12T09:00:00.000Z",
  "log_type": "action",
  "event_type": "post_created",
  "severity": "low",
  "actor": "claude_code",
  "status": "success",
  "action_category": "social_media",
  "target": "linkedin",
  "skill_used": "post-to-linkedin",
  "approval_required": true,
  "approval_status": "approved",
  "approved_by": "human",
  "cost_estimate": 0.015,
  "metadata": {
    "post_length": 187,
    "hashtags": ["AI", "Automation"],
    "engagement_24h": null,
    "post_id": "urn:li:share:7152..."
  }
}
```

---

### 2. System Logs (system/incidents/YYYY-MM-DD.json)

**Purpose:** Record system health, errors, recoveries

**Schema:**
```json
{
  "timestamp": "2026-01-12T10:30:00.123Z",
  "log_type": "system",
  "event_type": "process_crash|error_detected|recovery_attempt|health_check",
  "severity": "low|medium|high|critical",
  "actor": "monitor-system",
  "status": "success|failed|in_progress",
  "component": "gmail_watcher|xero_mcp|network",
  "error_code": "PROC_CRASH",
  "recovery_attempted": true,
  "recovery_method": "auto_restart",
  "recovery_attempts": 1,
  "escalated": false,
  "metadata": {
    "pid": 12345,
    "exit_code": 1,
    "last_heartbeat": "2026-01-12T10:25:00Z",
    "restart_time_ms": 5000
  }
}
```

**Example - Process Crash:**
```json
{
  "timestamp": "2026-01-12T11:47:23.456Z",
  "log_type": "system",
  "event_type": "process_crash",
  "severity": "high",
  "actor": "monitor-system",
  "status": "success",
  "component": "gmail_watcher",
  "error_code": "PROC_CRASH",
  "recovery_attempted": true,
  "recovery_method": "auto_restart",
  "recovery_attempts": 1,
  "escalated": false,
  "metadata": {
    "pid": 34567,
    "exit_code": 1,
    "last_heartbeat": "2026-01-12T11:42:00Z",
    "crash_reason": "uncaught_exception",
    "restart_time_ms": 5234,
    "new_pid": 34891
  }
}
```

**Example - Health Check:**
```json
{
  "timestamp": "2026-01-12T12:00:00.000Z",
  "log_type": "system",
  "event_type": "health_check",
  "severity": "low",
  "actor": "monitor-system",
  "status": "success",
  "component": "all",
  "health_score": 95,
  "health_status": "excellent",
  "components_healthy": 6,
  "components_degraded": 0,
  "components_failed": 0,
  "metadata": {
    "watchers": 30,
    "mcp_servers": 25,
    "disk_space": 14,
    "network": 15,
    "logging": 10,
    "vault": 5
  }
}
```

---

### 3. Financial Logs (financial/YYYY-MM.json)

**Purpose:** Record all financial operations (required 7-year retention)

**Schema:**
```json
{
  "timestamp": "2026-01-12T10:30:00.123Z",
  "log_type": "financial",
  "event_type": "transaction_synced|invoice_created|expense_categorized|payment_processed",
  "severity": "low|high",
  "actor": "claude_code",
  "status": "success|failed|pending",
  "amount": 150.00,
  "currency": "USD",
  "transaction_type": "income|expense|transfer",
  "category": "client_payment|software_subscription|contractor_fee",
  "approval_required": true,
  "approval_status": "approved",
  "metadata": {
    "source": "xero",
    "transaction_id": "TXN-12345",
    "client": "Client A",
    "invoice_number": "INV-001",
    "tax_category": "business_income"
  }
}
```

**Example - Invoice Created:**
```json
{
  "timestamp": "2026-01-12T15:30:00.000Z",
  "log_type": "financial",
  "event_type": "invoice_created",
  "severity": "low",
  "actor": "claude_code",
  "status": "success",
  "amount": 1500.00,
  "currency": "USD",
  "transaction_type": "income",
  "category": "client_payment",
  "approval_required": false,
  "approval_status": "auto_approved",
  "metadata": {
    "source": "xero",
    "invoice_id": "INV-2026-001",
    "client": "Client A",
    "client_email": "client.a@example.com",
    "due_date": "2026-01-27",
    "services": "January 2026 Consulting"
  }
}
```

**Example - Expense Categorized:**
```json
{
  "timestamp": "2026-01-12T08:15:00.000Z",
  "log_type": "financial",
  "event_type": "expense_categorized",
  "severity": "low",
  "actor": "claude_code",
  "status": "success",
  "amount": 54.99,
  "currency": "USD",
  "transaction_type": "expense",
  "category": "software_subscription",
  "approval_required": false,
  "approval_status": "auto_approved",
  "metadata": {
    "source": "xero",
    "transaction_id": "TXN-67890",
    "vendor": "Adobe",
    "confidence": 0.95,
    "tax_deductible": true,
    "recurring": true
  }
}
```

---

### 4. Security Logs (security/YYYY-MM.json)

**Purpose:** Record authentication, authorization, sensitive operations

**Schema:**
```json
{
  "timestamp": "2026-01-12T10:30:00.123Z",
  "log_type": "security",
  "event_type": "auth_success|auth_failure|token_refresh|sensitive_action|access_denied",
  "severity": "medium|high|critical",
  "actor": "user|claude_code|external_api",
  "status": "success|failed",
  "service": "gmail|xero|twitter|facebook",
  "action": "login|token_refresh|api_call|file_access",
  "source_ip": "192.168.1.100",
  "escalated": false,
  "metadata": {
    "auth_method": "oauth2",
    "failure_reason": null,
    "action_taken": "logged_event"
  }
}
```

**Example - Token Refresh:**
```json
{
  "timestamp": "2026-01-12T16:00:00.000Z",
  "log_type": "security",
  "event_type": "token_refresh",
  "severity": "medium",
  "actor": "claude_code",
  "status": "success",
  "service": "gmail",
  "action": "token_refresh",
  "source_ip": "192.168.1.100",
  "escalated": false,
  "metadata": {
    "auth_method": "oauth2",
    "token_age_hours": 167,
    "new_expiry": "2026-01-19T16:00:00Z"
  }
}
```

**Example - Auth Failure (Critical):**
```json
{
  "timestamp": "2026-01-12T17:23:45.000Z",
  "log_type": "security",
  "event_type": "auth_failure",
  "severity": "critical",
  "actor": "external_api",
  "status": "failed",
  "service": "xero",
  "action": "api_call",
  "source_ip": "192.168.1.100",
  "escalated": true,
  "metadata": {
    "auth_method": "oauth2",
    "failure_reason": "token_expired",
    "refresh_attempted": true,
    "refresh_failed": true,
    "action_taken": "user_reauth_required"
  }
}
```

---

## Log Retention Policies

| Log Type | Active | Compressed Archive | Permanent Archive | Purpose |
|----------|--------|-------------------|-------------------|---------|
| **Actions** | 90 days | 1 year | No | Audit trail |
| **System** | 60 days | 6 months | No | Debugging |
| **Financial** | 7 years | 7 years | Yes | Legal/tax |
| **Security** | 365 days | 7 years | Yes | Compliance |

**Rotation Schedule:**
- **Daily:** Create new log file at midnight UTC
- **Weekly:** Compress logs >7 days old
- **Monthly:** Move compressed logs to archives/
- **Yearly:** Compress yearly archives (except financial)

**Rotation Script (log_aggregator.py):**
```python
# Runs daily at 00:05 UTC
def rotate_logs():
    today = datetime.now()

    # 1. Create new daily files
    for log_type in ['actions', 'system', 'security']:
        create_daily_log(log_type, today)

    # 2. Compress logs >7 days old
    cutoff_date = today - timedelta(days=7)
    for log_type in ['actions', 'system', 'security']:
        compress_old_logs(log_type, cutoff_date)

    # 3. Archive compressed logs >30 days old
    archive_cutoff = today - timedelta(days=30)
    move_to_archives(archive_cutoff)

    # 4. Financial logs (monthly rotation)
    if today.day == 1:  # First of month
        rotate_financial_logs(today)
```

---

## Log Analysis Queries

### Find All Errors in Last 24 Hours
```bash
# Using jq to parse JSON logs
cat Vault/Logs/system/$(date +%Y-%m-%d).json | \
  jq 'select(.severity == "high" or .severity == "critical")'
```

### Calculate Daily Action Count by Type
```bash
cat Vault/Logs/actions/$(date +%Y-%m-%d).json | \
  jq -s 'group_by(.event_type) | map({type: .[0].event_type, count: length})'
```

### Find All Failed Approvals
```bash
cat Vault/Logs/actions/*.json | \
  jq 'select(.approval_status == "rejected")'
```

### Security Events in Last Week
```bash
find Vault/Logs/security/ -name "*.json" -mtime -7 -exec cat {} \; | \
  jq 'select(.severity == "high" or .severity == "critical")'
```

### Financial Summary for Month
```bash
cat Vault/Logs/financial/2026-01.json | \
  jq -s 'group_by(.transaction_type) | map({type: .[0].transaction_type, total: map(.amount) | add})'
```

---

## Privacy & Security Considerations

**Redact Sensitive Data:**
```python
SENSITIVE_FIELDS = [
    'password', 'token', 'secret', 'api_key',
    'ssn', 'credit_card', 'bank_account'
]

def sanitize_log_entry(entry):
    """Remove sensitive data before logging"""
    for field in SENSITIVE_FIELDS:
        if field in entry.get('metadata', {}):
            entry['metadata'][field] = '[REDACTED]'
    return entry
```

**Example:**
```json
{
  "metadata": {
    "api_key": "[REDACTED]",
    "request": "GET /api/users",
    "response_code": 200
  }
}
```

**Encryption at Rest:**
- Financial logs: Consider encrypting (GPG)
- Security logs: Encrypt before archiving
- Regular logs: Compression provides basic obfuscation

---

## Log Writing Best Practices

**1. Async Logging (Non-Blocking)**
```python
import asyncio
import aiofiles
import json

async def write_log(log_entry):
    """Write log asynchronously to not block main thread"""
    log_file = get_log_file_path(log_entry['log_type'])

    async with aiofiles.open(log_file, 'a') as f:
        await f.write(json.dumps(log_entry) + '\n')
```

**2. Structured Logging Helper**
```python
def create_log_entry(log_type, event_type, severity, actor, status, **kwargs):
    """Helper to create properly formatted log entries"""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'log_type': log_type,
        'event_type': event_type,
        'severity': severity,
        'actor': actor,
        'status': status,
        'metadata': kwargs
    }
```

**3. Error Context Logging**
```python
try:
    result = perform_action()
except Exception as e:
    log_entry = create_log_entry(
        log_type='system',
        event_type='error_detected',
        severity='high',
        actor='claude_code',
        status='failed',
        error_type=type(e).__name__,
        error_message=str(e),
        stack_trace=traceback.format_exc()
    )
    write_log(log_entry)
```

---

## Log Monitoring & Alerting

**Real-time Monitoring Patterns:**

```python
# Watch for critical errors
import pyinotify

def on_log_write(event):
    """Triggered when log file updated"""
    with open(event.pathname, 'r') as f:
        last_line = f.readlines()[-1]
        entry = json.loads(last_line)

        if entry['severity'] == 'critical':
            alert_user(entry)

# Set up file watcher
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm)
wm.add_watch('/Vault/Logs/system/', pyinotify.IN_MODIFY)
```

---

## Compliance & Audit Requirements

**For Gold Tier Completion:**
- [ ] All actions logged with complete metadata
- [ ] Financial logs retained for 7 years
- [ ] Security events logged and monitored
- [ ] Daily log rotation working
- [ ] Compression and archiving automated
- [ ] Log analysis queries documented
- [ ] Sensitive data properly redacted

**For Business Use:**
- Logs provide complete audit trail
- Can reconstruct any AI decision from logs
- Compliance with financial recordkeeping laws
- Security incident investigation capability

---

**Next Steps:** Implement logging in all skills using this schema. Use log_aggregator.py script for rotation and archiving.

**Maintenance:** Review log schemas quarterly, add new event types as needed, verify retention policies being followed.
