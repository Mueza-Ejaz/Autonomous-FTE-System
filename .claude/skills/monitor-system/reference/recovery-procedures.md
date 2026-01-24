# Recovery Procedures

**Version:** 1.0
**Last Updated:** 2026-01-12
**Purpose:** Step-by-step recovery procedures for all error types

---

## General Recovery Principles

**1. Assess Before Acting**
- Verify error is real (not transient)
- Check for cascading failures (fix root cause first)
- Review recent system changes

**2. Attempt Least Disruptive First**
- Try soft recovery (refresh, retry) before hard recovery (restart)
- Preserve state when possible
- Queue operations rather than dropping them

**3. Log Everything**
- Record all recovery attempts
- Document what worked/failed
- Track time to recovery

**4. Escalate Appropriately**
- Auto-recovery should succeed >90% of time
- Escalate only after multiple attempts
- Provide actionable information to user

**5. Verify Recovery**
- Confirm system returns to healthy state
- Resume queued operations
- Monitor for recurrence

---

## Process Recovery Procedures

### PROC_CRASH: Process Crashed

**Recovery Steps:**

```bash
# 1. Verify process is actually down
ps aux | grep <process_name>

# 2. Check for exit code/crash logs
tail -n 50 /Vault/Logs/system/$(date +%Y-%m-%d).json | grep <process_name>

# 3. Wait for exponential backoff period
# Attempt 1: 5 seconds
# Attempt 2: 10 seconds
# Attempt 3: 20 seconds

# 4. Restart process
python <watcher_script>.py &
PID=$!
echo $PID > /tmp/<process_name>.pid

# 5. Verify startup success (within 30 seconds)
sleep 5
if ps -p $PID > /dev/null; then
  echo "Process restarted successfully"
  # Log success
else
  echo "Process failed to start"
  # Increment attempt counter
  # If attempts >= 3: Escalate
fi

# 6. Resume monitoring
```

**Expected Recovery Time:** <1 minute
**Success Rate Target:** 95%

**Escalation Criteria:**
- 3 failed restart attempts
- Process starts but crashes immediately (<2 minutes)
- Missing dependencies detected

**Escalation Template:**
```markdown
---
type: system_alert
severity: high
component: <process_name>
---

## Process Restart Failed

**Process:** <process_name>
**PID:** <last_pid>
**Crash Time:** <timestamp>
**Restart Attempts:** 3
**Last Error:** <error_message>

## Manual Actions Required

1. Check process logs: `/Vault/Logs/system/`
2. Verify dependencies installed
3. Check file permissions
4. Restart manually: `python <script>.py`

**Auto-recovery disabled** for this process until resolved.
```

---

### PROC_UNRESPONSIVE: Process Frozen

**Recovery Steps:**

```bash
# 1. Verify process is unresponsive (not just slow)
# Check heartbeat file timestamp
HEARTBEAT_FILE=/tmp/<process_name>_heartbeat
LAST_HEARTBEAT=$(stat -c %Y $HEARTBEAT_FILE)
CURRENT_TIME=$(date +%s)
TIMEOUT=600  # 10 minutes

if [ $((CURRENT_TIME - LAST_HEARTBEAT)) -gt $TIMEOUT ]; then
  # 2. Attempt graceful termination
  kill -TERM $PID

  # 3. Wait 30 seconds for cleanup
  sleep 30

  # 4. Force kill if still running
  if ps -p $PID > /dev/null; then
    kill -KILL $PID
  fi

  # 5. Wait 5 seconds
  sleep 5

  # 6. Restart process (use PROC_CRASH procedure)
fi
```

**Expected Recovery Time:** <2 minutes
**Success Rate Target:** 90%

---

## API Recovery Procedures

### API_AUTH_FAILURE: Authentication Failed

**Recovery Steps:**

```python
# 1. Identify API and error type
api_name = error_data['api']  # e.g., 'gmail', 'xero', 'twitter'
status_code = error_data['status_code']  # 401

# 2. Attempt token refresh
if api_name == 'gmail':
    try:
        # Load refresh token
        creds = Credentials.from_authorized_user_file('token.json')

        # Request new access token
        creds.refresh(Request())

        # Save updated credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        # Log success
        log_recovery('API_AUTH_FAILURE', 'gmail', 'success', 'token_refresh')

        # Retry failed operation
        retry_queued_operations('gmail')

    except Exception as e:
        # 3. Token refresh failed - escalate
        escalate_auth_failure('gmail', str(e))

# 4. For OAuth2 APIs (Xero, Twitter, Facebook)
elif api_name in ['xero', 'twitter', 'facebook']:
    # Similar refresh logic
    # If refresh fails: Request user reauth

# 5. For API Key based (non-OAuth)
else:
    # Cannot auto-recover
    escalate_auth_failure(api_name, 'api_key_invalid')
```

**Escalation Template:**
```markdown
---
type: auth_required
severity: high
service: <api_name>
---

## API Authentication Required

**Service:** <api_name>
**Failure Time:** <timestamp>
**Error:** Token refresh failed

## Action Required

Please re-authenticate with <service>:

1. Visit: <auth_url>
2. Authorize access
3. Move this file to /Approved when complete

Auto-recovery will resume after authentication.
```

**Expected Recovery Time:** Immediate (if refresh succeeds), or requires user action
**Success Rate Target:** 80% (auto-refresh), 100% (with user action)

---

### API_RATE_LIMIT: Rate Limit Exceeded

**Recovery Steps:**

```python
# 1. Parse rate limit headers
retry_after = response.headers.get('Retry-After', 900)  # Default 15 min
rate_limit_reset = response.headers.get('X-RateLimit-Reset')

# 2. Queue pending operations
queue_operation({
    'api': api_name,
    'operation': operation_type,
    'data': request_data,
    'retry_after': retry_after
})

# 3. Log rate limit
log_event('API_RATE_LIMIT', {
    'api': api_name,
    'retry_after': retry_after,
    'queued_operations': len(queue)
})

# 4. Continue other operations (don't block entire system)

# 5. Schedule retry
schedule_retry(api_name, retry_after)

# 6. When retry time reached, process queue
def process_queue_after_rate_limit(api_name):
    queued = get_queued_operations(api_name)
    for operation in queued:
        try:
            execute_operation(operation)
        except RateLimitError:
            # Still rate limited, extend wait
            schedule_retry(api_name, 300)  # Try again in 5 min
            break
```

**Expected Recovery Time:** Varies (typically 15 minutes)
**Success Rate Target:** 100% (expected behavior, not a failure)
**No escalation needed** (unless rate limits prevent core operations for >2 hours)

---

### API_TIMEOUT: Request Timed Out

**Recovery Steps:**

```python
# Exponential backoff with jitter
import time
import random

max_attempts = 3
base_delay = 1

for attempt in range(max_attempts):
    try:
        response = make_api_request(endpoint, data, timeout=30)
        # Success
        log_recovery('API_TIMEOUT', api_name, 'success', f'attempt_{attempt+1}')
        return response

    except TimeoutError as e:
        if attempt < max_attempts - 1:
            # Calculate delay with jitter
            delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
            log_event('API_TIMEOUT', {
                'api': api_name,
                'attempt': attempt + 1,
                'retry_in': delay
            })
            time.sleep(delay)
        else:
            # Max attempts reached - queue for later
            queue_operation({'api': api_name, 'data': data})
            log_recovery('API_TIMEOUT', api_name, 'failed', 'max_attempts')

            # If critical operation, escalate
            if is_critical_operation(operation_type):
                escalate_timeout(api_name, operation_type)
```

**Expected Recovery Time:** <30 seconds (transient), or queue for later
**Success Rate Target:** 80% (within 3 attempts)

---

## Network Recovery Procedures

### NET_CONNECTION_FAILED: Network Down

**Recovery Steps:**

```python
# 1. Verify it's truly a network issue (test multiple endpoints)
test_endpoints = [
    'https://api.anthropic.com/health',
    'https://www.google.com',
    'https://api.github.com'
]

connectivity_checks = []
for endpoint in test_endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        connectivity_checks.append(True)
    except:
        connectivity_checks.append(False)

# 2. If all fail, network is down
if not any(connectivity_checks):
    # Enter degraded mode
    set_system_state('degraded_no_network')

    # 3. Queue all outbound operations
    queue_all_pending_operations()

    # 4. Continue local operations only
    # - File processing
    # - Task organization
    # - Data analysis

    # 5. Schedule connectivity retry every 5 minutes
    schedule_connectivity_check(interval=300)

    # 6. When network restored
    def on_network_restored():
        set_system_state('operational')
        process_queued_operations()
        log_recovery('NET_CONNECTION_FAILED', 'network', 'success', 'restored')

# 7. If outage >30 minutes, escalate
if network_down_duration > 1800:
    escalate_network_outage(duration=network_down_duration)
```

**Expected Recovery Time:** Automatic when network returns
**Success Rate Target:** 100% (graceful degradation)

---

## File System Recovery Procedures

### FS_DISK_FULL: Disk Space Low

**Recovery Steps:**

```bash
#!/bin/bash
# Automated disk space cleanup

# 1. Check current disk usage
DISK_FREE_PERCENT=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $DISK_FREE_PERCENT -gt 90 ]; then
  echo "Disk space critical: ${DISK_FREE_PERCENT}% used"

  # 2. Archive old logs (>30 days)
  find /Vault/Logs -name "*.json" -mtime +30 -exec gzip {} \;

  # 3. Move archives to archive folder
  find /Vault/Logs -name "*.json.gz" -mtime +7 -exec mv {} /Vault/Logs/archives/ \;

  # 4. Clean temp directories
  rm -rf /tmp/*.tmp
  rm -rf /Vault/.trash/*

  # 5. Compress old briefings
  find /Vault/Briefings -name "*.md" -mtime +90 -exec gzip {} \;

  # 6. Check space again
  DISK_FREE_AFTER=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
  SPACE_FREED=$((DISK_FREE_PERCENT - DISK_FREE_AFTER))

  if [ $DISK_FREE_AFTER -lt 90 ]; then
    echo "Cleanup successful: Freed ${SPACE_FREED}% disk space"
    log_recovery "FS_DISK_FULL" "filesystem" "success" "freed_${SPACE_FREED}pct"
  else
    echo "Cleanup insufficient: Still ${DISK_FREE_AFTER}% used"
    escalate_disk_full $DISK_FREE_AFTER
  fi
fi
```

**Expected Recovery Time:** <5 minutes
**Success Rate Target:** 85% (auto-cleanup sufficient)

**Escalation Criteria:**
- Still <10% free after cleanup
- Critical system files at risk
- Cannot write logs

---

### FS_VAULT_LOCKED: Vault Inaccessible

**Recovery Steps:**

```python
# 1. Check if Obsidian is running and has vault open
import psutil

obsidian_running = False
for proc in psutil.process_iter(['name']):
    if 'obsidian' in proc.info['name'].lower():
        obsidian_running = True
        break

# 2. If Obsidian running, vault might be locked
if obsidian_running:
    # Wait 1 minute for user to close file
    log_event('FS_VAULT_LOCKED', {'reason': 'obsidian_open', 'action': 'waiting'})
    time.sleep(60)

    # Retry access
    try:
        with open('/Vault/Dashboard.md', 'r') as f:
            content = f.read()
        # Success
        log_recovery('FS_VAULT_LOCKED', 'vault', 'success', 'access_restored')
    except:
        # Still locked after 1 minute
        if attempt_count < 5:
            # Try again
            schedule_retry('vault_access', 60)
        else:
            # Escalate
            escalate_vault_locked()

# 3. If Obsidian not running, check permissions
else:
    import os
    try:
        # Test read permission
        with open('/Vault/Dashboard.md', 'r') as f:
            pass
        # Test write permission
        test_file = '/Vault/.access_test'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)

    except PermissionError:
        escalate_permissions_issue('/Vault/')
```

**Expected Recovery Time:** 1-5 minutes
**Success Rate Target:** 90%

---

## Recovery Verification Checklist

After any recovery, verify:

- [ ] Component shows healthy in health check
- [ ] Queued operations processed successfully
- [ ] No immediate re-occurrence of error
- [ ] Logs show successful recovery
- [ ] Dependent systems functioning
- [ ] Health score improved

---

## Escalation Guidelines

**When to Escalate:**
1. Auto-recovery fails after max attempts
2. Critical system component affected
3. Security-related errors
4. Data integrity at risk
5. Multiple cascading failures
6. Error pattern not in catalog

**How to Escalate:**
1. Create alert file in /Needs_Action/
2. Include error details and recovery attempts
3. Provide actionable next steps
4. Log escalation event
5. Disable auto-recovery for that component (if dangerous)

**Escalation Response Time Expectations:**
- CRITICAL: Immediate notification
- HIGH: Within 1 hour
- MEDIUM: Within 4 hours
- LOW: Next business day

---

## Recovery Metrics

**Track these metrics monthly:**
- Total errors by type
- Auto-recovery success rate
- Average time to recovery
- Escalation rate
- False positive rate
- System uptime percentage

**Target Metrics:**
- Auto-recovery success: >90%
- Mean time to recovery: <5 minutes
- Escalation rate: <10% of errors
- System uptime: >99%

---

**Next Steps:** Use health-check-matrix.md for health monitoring and audit-log-schema.md for logging recovered events.

**Maintenance:** Test recovery procedures quarterly, update based on actual recovery outcomes, add new procedures as new integrations added.
