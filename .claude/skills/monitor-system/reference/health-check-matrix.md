# Health Check Matrix

**Version:** 1.0
**Last Updated:** 2026-01-12
**Purpose:** Comprehensive health scoring system with component weights and thresholds

---

## Health Score Overview

**Total Score: 100 points**

The health score provides a single metric (0-100) representing overall system health. It's calculated every 5 minutes by health_monitor.py.

**Health Thresholds:**
- **90-100:** Excellent (🟢 Green) - All systems operational
- **80-89:** Good (🟡 Yellow) - Minor issues, monitoring
- **50-79:** Degraded (🟠 Orange) - Auto-recovery active
- **0-49:** Critical (🔴 Red) - User intervention required

---

## Component Health Matrix

### 1. Watcher Processes (30 points)

**What's Checked:**
- All Watcher scripts are running (PID exists)
- Processes are responsive (heartbeat <10 minutes old)
- No crash/restart loops (max 2 restarts/hour)

| Check | Points | Pass Criteria | Fail Impact |
|-------|--------|---------------|-------------|
| Gmail Watcher | 6 | PID exists, heartbeat active | -6 pts |
| WhatsApp Watcher | 6 | PID exists, heartbeat active | -6 pts |
| LinkedIn Watcher | 6 | PID exists, heartbeat active | -6 pts |
| Finance Watcher | 6 | PID exists, heartbeat active | -6 pts |
| File System Watcher | 6 | PID exists, heartbeat active | -6 pts |

**Health Check Script:**
```bash
#!/bin/bash
# Check if watcher process is running and responsive

WATCHER_NAME=$1
PID_FILE="/tmp/${WATCHER_NAME}.pid"
HEARTBEAT_FILE="/tmp/${WATCHER_NAME}_heartbeat"

if [ ! -f "$PID_FILE" ]; then
  echo "FAIL: PID file not found"
  exit 1
fi

PID=$(cat $PID_FILE)

# Check if process exists
if ! ps -p $PID > /dev/null; then
  echo "FAIL: Process not running (PID: $PID)"
  exit 1
fi

# Check heartbeat (must be <10 minutes old)
if [ -f "$HEARTBEAT_FILE" ]; then
  HEARTBEAT_AGE=$(( $(date +%s) - $(stat -c %Y $HEARTBEAT_FILE) ))
  if [ $HEARTBEAT_AGE -gt 600 ]; then
    echo "FAIL: Heartbeat too old ($HEARTBEAT_AGE seconds)"
    exit 1
  fi
fi

echo "PASS: Process healthy"
exit 0
```

**Scoring Logic:**
```python
watcher_score = 0
watchers = ['gmail', 'whatsapp', 'linkedin', 'finance', 'filesystem']

for watcher in watchers:
    if check_watcher_health(watcher):
        watcher_score += 6  # Each watcher worth 6 points

return watcher_score  # Max 30 points
```

---

### 2. MCP Servers (25 points)

**What's Checked:**
- MCP server processes running
- Server responds to ping/health endpoint
- No authentication errors in last 10 minutes

| Server | Points | Pass Criteria | Fail Impact |
|--------|--------|---------------|-------------|
| Email MCP | 8 | Responding, authenticated | -8 pts |
| Xero MCP | 8 | Responding, authenticated | -8 pts |
| Social Media MCP | 5 | Responding, authenticated | -5 pts |
| Browser MCP | 4 | Responding, available | -4 pts |

**Health Check Script:**
```python
import json
import subprocess

def check_mcp_server(server_name):
    """Check if MCP server is healthy"""
    try:
        # Test MCP server with simple ping
        result = subprocess.run(
            ['claude-code', 'mcp', 'ping', server_name],
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            # Check for recent auth errors
            recent_errors = check_recent_errors(server_name, minutes=10)
            if 'auth' in recent_errors.lower():
                return False, "Authentication error"
            return True, "Healthy"
        else:
            return False, f"Server not responding: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "Health check timeout"
    except Exception as e:
        return False, f"Error: {str(e)}"
```

**Scoring Logic:**
```python
mcp_score = 0
mcp_servers = {
    'email': 8,
    'xero': 8,
    'social_media': 5,
    'browser': 4
}

for server, points in mcp_servers.items():
    healthy, message = check_mcp_server(server)
    if healthy:
        mcp_score += points

return mcp_score  # Max 25 points
```

---

### 3. Disk Space (15 points)

**What's Checked:**
- Free disk space percentage
- Log directory size
- Vault directory accessible

| Metric | Points | Pass Criteria | Fail Impact |
|--------|--------|---------------|-------------|
| Free Space % | 10 | >20% free | -10 pts |
| Free Space % | 5 | 10-20% free (warning) | -5 pts |
| Log Size | 3 | <5GB | -3 pts |
| Vault Access | 2 | Read/write OK | -2 pts |

**Scoring Logic:**
```python
import shutil

def check_disk_health():
    score = 0

    # Check free space
    stat = shutil.disk_usage('/')
    free_percent = (stat.free / stat.total) * 100

    if free_percent > 20:
        score += 10  # Excellent
    elif free_percent > 10:
        score += 5   # Warning
    else:
        score += 0   # Critical

    # Check log directory size
    log_size_gb = get_directory_size('/Vault/Logs') / (1024**3)
    if log_size_gb < 5:
        score += 3

    # Check vault access
    try:
        with open('/Vault/.access_test', 'w') as f:
            f.write('test')
        os.remove('/Vault/.access_test')
        score += 2
    except:
        pass

    return score  # Max 15 points
```

---

### 4. Network Connectivity (15 points)

**What's Checked:**
- Internet connectivity (external ping)
- API endpoint reachability
- DNS resolution working

| Check | Points | Pass Criteria | Fail Impact |
|-------|--------|---------------|-------------|
| Internet | 7 | Can reach google.com | -7 pts |
| API Endpoints | 5 | 3+ APIs reachable | -5 pts |
| DNS | 3 | Can resolve domains | -3 pts |

**Health Check Script:**
```python
import requests
import socket

def check_network_health():
    score = 0

    # 1. Internet connectivity
    try:
        response = requests.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            score += 7
    except:
        pass

    # 2. API endpoints
    api_endpoints = [
        'https://api.anthropic.com/health',
        'https://gmail.googleapis.com',
        'https://api.twitter.com/2',
        'https://api.xero.com'
    ]

    reachable_count = 0
    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint, timeout=3)
            if response.status_code < 500:  # Any non-server error
                reachable_count += 1
        except:
            pass

    if reachable_count >= 3:
        score += 5

    # 3. DNS resolution
    try:
        socket.gethostbyname('api.anthropic.com')
        score += 3
    except:
        pass

    return score  # Max 15 points
```

---

### 5. Logging System (10 points)

**What's Checked:**
- Logs being written successfully
- No log write errors in last hour
- Log rotation working

| Check | Points | Pass Criteria | Fail Impact |
|-------|--------|---------------|-------------|
| Logs Writing | 5 | Recent log entries | -5 pts |
| No Write Errors | 3 | 0 write errors/hour | -3 pts |
| Rotation Working | 2 | Daily logs rotated | -2 pts |

**Scoring Logic:**
```python
def check_logging_health():
    score = 0
    today = datetime.now().strftime('%Y-%m-%d')

    # 1. Check if logs being written
    log_file = f'/Vault/Logs/actions/{today}.json'
    if os.path.exists(log_file):
        stat = os.stat(log_file)
        age_minutes = (time.time() - stat.st_mtime) / 60
        if age_minutes < 10:  # Written in last 10 minutes
            score += 5

    # 2. Check for write errors
    error_count = count_log_errors('FS_LOG_WRITE_ERROR', hours=1)
    if error_count == 0:
        score += 3

    # 3. Check rotation (yesterday's log should exist)
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_log = f'/Vault/Logs/actions/{yesterday}.json'
    if os.path.exists(yesterday_log):
        score += 2

    return score  # Max 10 points
```

---

### 6. Vault Access (5 points)

**What's Checked:**
- Dashboard.md readable
- Can write to vault
- Obsidian not locking files

| Check | Points | Pass Criteria | Fail Impact |
|-------|--------|---------------|-------------|
| Read Access | 2 | Can read Dashboard.md | -2 pts |
| Write Access | 2 | Can create test file | -2 pts |
| No Lock Conflicts | 1 | No locked files | -1 pt |

**Scoring Logic:**
```python
def check_vault_health():
    score = 0

    # 1. Read access
    try:
        with open('/Vault/Dashboard.md', 'r') as f:
            content = f.read()
        score += 2
    except:
        pass

    # 2. Write access
    try:
        test_file = '/Vault/.health_check_test'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        score += 2
    except:
        pass

    # 3. No lock conflicts
    locked_files = find_locked_files('/Vault/')
    if len(locked_files) == 0:
        score += 1

    return score  # Max 5 points
```

---

## Overall Health Calculation

```python
def calculate_health_score():
    """Calculate total health score (0-100)"""

    score = 0

    # 1. Watchers (30 pts)
    score += check_watcher_health()

    # 2. MCP Servers (25 pts)
    score += check_mcp_health()

    # 3. Disk Space (15 pts)
    score += check_disk_health()

    # 4. Network (15 pts)
    score += check_network_health()

    # 5. Logging (10 pts)
    score += check_logging_health()

    # 6. Vault Access (5 pts)
    score += check_vault_health()

    return min(score, 100)  # Cap at 100
```

---

## Health Status Interpretation

### 🟢 Excellent (90-100)
**Status:** All systems operational
**Actions:** None required
**Monitoring:** Standard 5-minute checks
**Example:**
- All 5 watchers running
- All 4 MCP servers responding
- 25% disk free
- All APIs reachable
- Logs writing normally

---

### 🟡 Good (80-89)
**Status:** Minor issues present
**Actions:** Monitor closely, no immediate action
**Monitoring:** Continue 5-minute checks
**Example:**
- 1 watcher temporarily offline (auto-restarting)
- 15% disk free (warning level)
- All other systems healthy

---

### 🟠 Degraded (50-79)
**Status:** Significant issues, auto-recovery active
**Actions:** Auto-recovery procedures running
**Monitoring:** Increase to 2-minute checks
**Alert User:** If persists >15 minutes
**Example:**
- 2 watchers offline
- 1 MCP server authentication failed
- 12% disk free
- Auto-recovery in progress

---

### 🔴 Critical (0-49)
**Status:** Major system failure
**Actions:** Immediate user notification required
**Monitoring:** Continuous
**Alert User:** Immediately
**Example:**
- 3+ watchers crashed
- Network connectivity lost
- <5% disk free
- Multiple MCP servers failing
- User intervention required

---

## Health Check Schedule

**Standard Operations (Health >80):**
- Check every: 5 minutes
- Log results: Every check
- Update Dashboard: Every check

**Degraded Mode (Health 50-79):**
- Check every: 2 minutes
- Log results: Every check
- Update Dashboard: Every check
- Alert after: 15 minutes degraded

**Critical Mode (Health <50):**
- Check every: 1 minute
- Log results: Every check
- Update Dashboard: Every check
- Alert immediately

---

## Health Report Format

**Dashboard Update (System_Status.md):**
```markdown
---
last_updated: 2026-01-12T10:30:00Z
health_score: 95
status: excellent
---

# System Health Report

**Overall Score:** 95/100 🟢 Excellent

## Component Status

| Component | Score | Status | Details |
|-----------|-------|--------|---------|
| Watchers | 30/30 | ✅ Healthy | All 5 running |
| MCP Servers | 25/25 | ✅ Healthy | All responding |
| Disk Space | 14/15 | ⚠️ Good | 22% free |
| Network | 15/15 | ✅ Healthy | All connected |
| Logging | 10/10 | ✅ Healthy | Writing normally |
| Vault | 5/5 | ✅ Healthy | Full access |

**Last Check:** 2026-01-12 10:30:00
**Next Check:** 2026-01-12 10:35:00
```

---

## Health Metrics Tracking

**Track these metrics for trend analysis:**
```json
{
  "timestamp": "2026-01-12T10:30:00Z",
  "health_score": 95,
  "components": {
    "watchers": {"score": 30, "max": 30, "status": "healthy"},
    "mcp_servers": {"score": 25, "max": 25, "status": "healthy"},
    "disk_space": {"score": 14, "max": 15, "status": "warning"},
    "network": {"score": 15, "max": 15, "status": "healthy"},
    "logging": {"score": 10, "max": 10, "status": "healthy"},
    "vault": {"score": 5, "max": 5, "status": "healthy"}
  },
  "degraded_duration": 0,
  "recovery_count": 0
}
```

---

## Alerting Thresholds

| Condition | Threshold | Action | Priority |
|-----------|-----------|--------|----------|
| Score drops below 80 | Instant | Log warning | Medium |
| Score below 80 for >15min | 15 min | Create alert file | High |
| Score drops below 50 | Instant | Critical alert | Critical |
| Score 0 (total failure) | Instant | Emergency notification | Emergency |
| Component at 0 for >5min | 5 min | Component-specific alert | High |

---

**Next Steps:** Use error-catalog.md to understand errors affecting health, and recovery-procedures.md to restore health.

**Maintenance:** Review health score trends weekly, adjust component weights if needed, add new components as system expands.
