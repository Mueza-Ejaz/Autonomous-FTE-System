# Error Catalog

**Version:** 1.0
**Last Updated:** 2026-01-12
**Purpose:** Complete taxonomy of error types with classifications and recovery strategies

---

## Error Classification System

**Severity Levels:**
- **CRITICAL:** System-wide failure, requires immediate attention
- **HIGH:** Major component failure, auto-recovery should be attempted
- **MEDIUM:** Degraded functionality, monitor and retry
- **LOW:** Minor issues, log and continue

**Categories:**
- Process Errors
- API Errors
- Network Errors
- File System Errors
- Logic Errors
- Security Errors

---

## Process Errors

### PROC_CRASH
**Severity:** HIGH
**Description:** Watcher or critical process terminated unexpectedly
**Detection:** PID not found in process list
**Recovery:** Auto-restart with exponential backoff
**Escalation:** After 3 failed restart attempts

**Example Log:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "error_type": "PROC_CRASH",
  "severity": "HIGH",
  "process_name": "gmail_watcher",
  "pid": 12345,
  "exit_code": 1,
  "last_heartbeat": "2026-01-12T10:25:00Z"
}
```

---

### PROC_UNRESPONSIVE
**Severity:** MEDIUM
**Description:** Process running but not responding to health checks
**Detection:** Heartbeat timeout (>10 minutes)
**Recovery:** Send SIGTERM, wait 30s, then SIGKILL and restart
**Escalation:** If restart fails

**Example Log:**
```json
{
  "timestamp": "2026-01-12T11:00:00Z",
  "error_type": "PROC_UNRESPONSIVE",
  "severity": "MEDIUM",
  "process_name": "whatsapp_watcher",
  "pid": 23456,
  "last_heartbeat": "2026-01-12T10:45:00Z",
  "heartbeat_timeout": 900
}
```

---

### PROC_STARTUP_FAILED
**Severity:** HIGH
**Description:** Process failed to start
**Detection:** No PID created within 30 seconds
**Recovery:** Check dependencies, verify permissions, retry
**Escalation:** After 2 failed attempts

---

## API Errors

### API_AUTH_FAILURE
**Severity:** HIGH
**Description:** API authentication failed (expired token, revoked access)
**Detection:** 401 Unauthorized response
**Recovery:** Attempt token refresh, then request user reauth
**Escalation:** If token refresh fails

**Example Log:**
```json
{
  "timestamp": "2026-01-12T12:00:00Z",
  "error_type": "API_AUTH_FAILURE",
  "severity": "HIGH",
  "api": "gmail",
  "status_code": 401,
  "error_message": "Token expired",
  "token_age_hours": 168
}
```

---

### API_RATE_LIMIT
**Severity:** MEDIUM
**Description:** API rate limit exceeded
**Detection:** 429 Too Many Requests
**Recovery:** Parse retry-after header, queue operations, wait and retry
**Escalation:** None (expected behavior)

**Example Log:**
```json
{
  "timestamp": "2026-01-12T13:00:00Z",
  "error_type": "API_RATE_LIMIT",
  "severity": "MEDIUM",
  "api": "twitter",
  "status_code": 429,
  "retry_after_seconds": 900,
  "requests_remaining": 0
}
```

---

### API_TIMEOUT
**Severity:** MEDIUM
**Description:** API request timed out
**Detection:** No response within timeout period (30s default)
**Recovery:** Retry with exponential backoff (3 attempts)
**Escalation:** After 3 failed attempts

---

### API_SERVER_ERROR
**Severity:** MEDIUM
**Description:** API returned 5xx server error
**Detection:** 500-599 status codes
**Recovery:** Retry after 1 minute (5 attempts)
**Escalation:** After 5 failed attempts or if persists >30 minutes

---

## Network Errors

### NET_CONNECTION_FAILED
**Severity:** CRITICAL
**Description:** No network connectivity
**Detection:** Cannot reach external services
**Recovery:** Queue operations, retry every 5 minutes
**Escalation:** If outage >30 minutes

**Example Log:**
```json
{
  "timestamp": "2026-01-12T14:00:00Z",
  "error_type": "NET_CONNECTION_FAILED",
  "severity": "CRITICAL",
  "test_endpoint": "https://api.anthropic.com/health",
  "error_message": "Connection timed out",
  "duration_seconds": 30
}
```

---

### NET_DNS_FAILURE
**Severity:** HIGH
**Description:** DNS resolution failed
**Detection:** Cannot resolve domain names
**Recovery:** Wait 2 minutes, retry, check /etc/hosts if persistent
**Escalation:** After 10 minutes

---

### NET_SSL_ERROR
**Severity:** HIGH
**Description:** SSL/TLS certificate validation failed
**Detection:** Certificate errors
**Recovery:** Log error, do NOT bypass validation, alert user
**Escalation:** Immediate (security issue)

---

## File System Errors

### FS_DISK_FULL
**Severity:** CRITICAL
**Description:** Disk space <10% free
**Detection:** Disk usage check
**Recovery:** Archive logs, compress files, clean temp
**Escalation:** If space still <10% after cleanup

**Example Log:**
```json
{
  "timestamp": "2026-01-12T15:00:00Z",
  "error_type": "FS_DISK_FULL",
  "severity": "CRITICAL",
  "disk_path": "/",
  "total_gb": 500,
  "used_gb": 465,
  "free_gb": 35,
  "percent_free": 7
}
```

---

### FS_PERMISSION_DENIED
**Severity:** HIGH
**Description:** Cannot read/write required file
**Detection:** Permission errors
**Recovery:** Check file permissions, attempt chmod if owned by user
**Escalation:** If permissions cannot be fixed

---

### FS_FILE_NOT_FOUND
**Severity:** MEDIUM
**Description:** Expected file does not exist
**Detection:** File read attempts
**Recovery:** Check if moved/deleted, recreate if template available
**Escalation:** If critical file (Business_Goals.md, etc.)

---

### FS_VAULT_LOCKED
**Severity:** HIGH
**Description:** Obsidian vault is locked or inaccessible
**Detection:** Cannot read Dashboard.md
**Recovery:** Wait 1 minute, retry, check Obsidian process
**Escalation:** After 5 minutes

---

## Logic Errors

### LOGIC_INVALID_DATA
**Severity:** MEDIUM
**Description:** Data validation failed
**Detection:** Parsing errors, schema validation failures
**Recovery:** Skip invalid record, log details for manual review
**Escalation:** If >20% of records invalid

**Example Log:**
```json
{
  "timestamp": "2026-01-12T16:00:00Z",
  "error_type": "LOGIC_INVALID_DATA",
  "severity": "MEDIUM",
  "data_source": "xero_transactions",
  "validation_error": "Missing required field: amount",
  "record_id": "INV-12345"
}
```

---

### LOGIC_CATEGORIZATION_FAILED
**Severity:** LOW
**Description:** Cannot auto-categorize expense/email
**Detection:** Confidence score <50%
**Recovery:** Flag for manual review, use "Uncategorized"
**Escalation:** None (human review expected)

---

### LOGIC_UNEXPECTED_STATE
**Severity:** MEDIUM
**Description:** System in unexpected state
**Detection:** State machine violations
**Recovery:** Reset to known good state, log details
**Escalation:** If cannot recover state

---

## Security Errors

### SEC_AUTH_FAILURE
**Severity:** CRITICAL
**Description:** Authentication failure for system access
**Detection:** Invalid credentials, suspicious activity
**Recovery:** Lock system, require manual reauth
**Escalation:** Immediate

**Example Log:**
```json
{
  "timestamp": "2026-01-12T17:00:00Z",
  "error_type": "SEC_AUTH_FAILURE",
  "severity": "CRITICAL",
  "service": "xero",
  "failure_count": 3,
  "source_ip": "192.168.1.100",
  "action": "system_locked"
}
```

---

### SEC_RATE_LIMIT_ABUSE
**Severity:** HIGH
**Description:** Unusual number of requests (potential compromise)
**Detection:** Requests >2x normal rate
**Recovery:** Throttle operations, log activity
**Escalation:** If persists >1 hour

---

### SEC_INVALID_APPROVAL
**Severity:** HIGH
**Description:** Approval file tampered or invalid
**Detection:** Checksum failure, missing fields
**Recovery:** Reject action, alert user
**Escalation:** Immediate

---

## Error Pattern Analysis

### Cascading Failures
**Pattern:** One error triggers multiple downstream errors
**Detection:** 5+ errors within 2 minutes
**Recovery:** Identify root cause, pause operations, fix root cause first
**Example:** Network failure → All API errors → All Watcher crashes

---

### Intermittent Failures
**Pattern:** Error appears and resolves repeatedly
**Detection:** Same error 3+ times in 1 hour with successful operations between
**Recovery:** Increase retry delays, investigate network stability
**Example:** Gmail API timeout every 15 minutes

---

### Progressive Degradation
**Pattern:** Errors increasing in frequency over time
**Detection:** Error rate doubling each hour
**Recovery:** Proactive intervention before full failure
**Example:** Disk space warnings becoming critical

---

## Recovery Priority Matrix

| Severity | Auto-Recover | Max Attempts | Escalate After | Continue Operations |
|----------|--------------|--------------|----------------|---------------------|
| CRITICAL | Yes | 2 | 5 minutes | Partial only |
| HIGH | Yes | 3 | 10 minutes | Degraded mode |
| MEDIUM | Yes | 5 | 30 minutes | Yes |
| LOW | Optional | 1 | 24 hours | Yes |

---

## False Positive Handling

**Common False Positives:**
1. Planned API maintenance (check status pages first)
2. User-initiated process stops (check /Approved folder)
3. Rate limits during high activity (expected behavior)
4. Network blips <30 seconds (transient)

**Prevention:**
- Check system announcements before escalating
- Verify error persists >1 minute before acting
- Cross-reference with other health indicators
- Maintain "known issues" list

---

## Monitoring Best Practices

1. **Trend analysis:** Track error frequency over time
2. **Error budgets:** Alert if error rate >1% of operations
3. **Root cause analysis:** Investigate recurring patterns monthly
4. **Documentation:** Update catalog when new errors discovered
5. **Testing:** Simulate errors to verify recovery works

---

**Next Steps:** Use recovery-procedures.md for step-by-step recovery actions for each error type.

**Maintenance:** Review and update monthly, add new error types as discovered, refine severity classifications based on actual impact.
