# Analysis Framework

**Version:** 1.0 | **Purpose:** Methodologies for data collection, performance analysis, and insight generation

---

## Overview

This framework defines how the CEO Briefing system collects data, calculates scores, identifies bottlenecks, and generates insights. All analysis is systematic, repeatable, and data-driven.

---

## Phase 1: Data Collection

### 1.1 Financial Data Collection

**Source:** `manage-accounting` skill output

**Primary File:** `Vault/Accounting/Current_Month.md`

**Data Points to Extract:**

```python
financial_data = {
    "period": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    },
    "revenue": {
        "weekly": 0.0,
        "mtd": 0.0,
        "transactions": []
    },
    "expenses": {
        "weekly": 0.0,
        "mtd": 0.0,
        "by_category": {},
        "transactions": []
    },
    "invoices": {
        "outstanding_total": 0.0,
        "outstanding_count": 0,
        "overdue_total": 0.0,
        "overdue_count": 0,
        "overdue_days": []
    },
    "subscriptions": {
        "identified": [],
        "total_monthly": 0.0
    }
}
```

**Collection Procedure:**

1. **Read Current Month Transactions**
   ```bash
   Read: Vault/Accounting/Current_Month.md
   ```

2. **Parse Transaction Format:**
   ```markdown
   ## Transactions

   ### YYYY-MM-DD - [Description]
   - Amount: $X,XXX
   - Category: [Category]
   - Type: [Revenue/Expense]
   - Status: [Paid/Pending/Overdue]
   ```

3. **Filter by Date Range:**
   - Weekly: Last 7 days from current date
   - MTD: First day of month to current date

4. **Categorize Transactions:**
   - Revenue: Type = "Revenue" or Amount > 0
   - Expenses: Type = "Expense" or Amount < 0
   - Group expenses by category

5. **Identify Subscriptions:**
   - Pattern match: recurring same amount to same vendor
   - Flag if frequency = monthly and confidence > 80%

6. **Calculate Outstanding:**
   - Parse invoices section for status = "Unpaid"
   - Check dates for overdue (>30 days)

**Error Handling:**
- If file not found → Log warning, set financial_score = N/A
- If parse error → Skip malformed entries, log issue
- If dates invalid → Use current date as fallback

---

### 1.2 Operational Data Collection

**Source:** `process-tasks` skill output

**Primary Folders:**
- `Vault/Tasks/Active/` (current tasks)
- `Vault/Done/` (completed tasks)

**Data Points to Extract:**

```python
operational_data = {
    "tasks": {
        "completed_weekly": 0,
        "completion_rate": 0.0,
        "avg_cycle_time": 0.0,
        "overdue_count": 0,
        "overdue_priority": {"high": 0, "medium": 0, "low": 0}
    },
    "bottlenecks": []
}
```

**Collection Procedure:**

1. **Scan Done Folder for Weekly Completions**
   ```bash
   Glob: Vault/Done/*.md
   Filter: Last 7 days based on file modification time or completion date in metadata
   ```

2. **Extract Task Metadata:**
   ```yaml
   ---
   title: Task name
   created: YYYY-MM-DD
   completed: YYYY-MM-DD
   priority: high|medium|low
   expected_duration: X days
   actual_duration: Y days
   ---
   ```

3. **Calculate Metrics:**
   - **Completed Weekly:** Count of completed tasks in last 7 days
   - **Cycle Time:** Average (actual_duration) for completed tasks
   - **Completion Rate:** completed / (completed + active) * 100

4. **Check for Overdue Tasks:**
   ```bash
   Glob: Vault/Tasks/Active/*.md
   Check: If due_date < current_date → overdue
   Group: By priority level
   ```

5. **Identify Bottlenecks:**
   - If actual_duration > expected_duration * 1.5 → bottleneck
   - Extract reason from task notes if available

**Error Handling:**
- If no tasks found → Set operational_score = N/A
- If metadata missing → Use file timestamps as fallback
- If duration not specified → Skip cycle time calculation

---

### 1.3 Email Data Collection

**Source:** `process-emails` skill output

**Primary Folder:** `Vault/Done/` (processed emails)

**Data Points to Extract:**

```python
email_data = {
    "processed_weekly": 0,
    "avg_response_time": 0.0,  # in hours
    "pending_high_priority": 0,
    "response_time_breakdown": {
        "under_1h": 0,
        "1_to_4h": 0,
        "4_to_24h": 0,
        "over_24h": 0
    }
}
```

**Collection Procedure:**

1. **Scan Done Folder for Processed Emails**
   ```bash
   Glob: Vault/Done/EMAIL_*.md
   Filter: Last 7 days
   ```

2. **Extract Email Metadata:**
   ```yaml
   ---
   type: email
   received: YYYY-MM-DDTHH:MM:SSZ
   processed: YYYY-MM-DDTHH:MM:SSZ
   priority: high|medium|low
   ---
   ```

3. **Calculate Response Time:**
   ```python
   response_time = processed - received  # in hours
   avg_response_time = sum(response_times) / count
   ```

4. **Check Pending High Priority:**
   ```bash
   Glob: Vault/Needs_Action/EMAIL_*.md
   Filter: priority = "high"
   Count: pending_high_priority
   ```

**Error Handling:**
- If no emails found → Set email_score = N/A
- If timestamps missing → Skip that email in average calculation
- If priority not set → Assume "medium"

---

### 1.4 Social Media Data Collection

**Sources:** All social media skills

**Primary Files:**
- `Vault/Social_Media/LinkedIn/metrics.json`
- `Vault/Social_Media/Facebook/metrics.json`
- `Vault/Social_Media/Instagram/metrics.json`
- `Vault/Social_Media/Twitter/metrics.json`

**Data Points to Extract:**

```python
social_data = {
    "linkedin": {...},
    "facebook": {...},
    "instagram": {...},
    "twitter": {...},
    "summary": {
        "total_posts": 0,
        "total_engagement": 0,
        "engagement_rate": 0.0,
        "follower_growth": 0
    }
}
```

**Standard Metrics Format (per platform):**

```json
{
  "posts_published": 0,
  "scheduled_posts": 0,
  "engagement": {
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "total": 0
  },
  "reach": 0,
  "impressions": 0,
  "followers": {
    "current": 0,
    "change": 0,
    "change_percentage": 0.0
  },
  "engagement_rate": 0.0,
  "top_posts": []
}
```

**Collection Procedure:**

1. **Read Each Platform Metrics File**
   ```bash
   Read: Vault/Social_Media/[Platform]/metrics.json
   Parse: JSON to dictionary
   ```

2. **Aggregate Cross-Platform:**
   ```python
   total_posts = sum(platform["posts_published"] for all platforms)
   total_engagement = sum(platform["engagement"]["total"] for all platforms)
   engagement_rate = total_engagement / (total_posts * avg_followers)
   ```

3. **Handle Missing Platforms:**
   - If platform file missing → Set platform data = 0, log warning
   - If Gold tier skills not yet built → Only use LinkedIn data

**Error Handling:**
- If JSON parse error → Log error, skip platform
- If metrics outdated (>48h) → Flag in briefing as stale data
- If all platforms missing → Set social_score = N/A

---

### 1.5 Business Goals Data Collection

**Source:** `Vault/Business_Goals.md`

**Data Points to Extract:**

```python
goals_data = {
    "targets": {
        "revenue_monthly": 0.0,
        "expense_budget": 0.0,
        "task_completion_target": 0.0,
        "email_response_target": 24,  # hours
        "social_posts_per_week": 0,
        "social_engagement_target": 0.0
    },
    "goals": [
        {
            "name": "Goal name",
            "target": "Description",
            "current": 0.0,
            "target_value": 100.0,
            "progress_percentage": 0.0,
            "due_date": "YYYY-MM-DD",
            "status": "on_track|at_risk|behind"
        }
    ]
}
```

**Collection Procedure:**

1. **Read Business Goals File**
   ```bash
   Read: Vault/Business_Goals.md
   ```

2. **Parse Targets Section:**
   ```markdown
   ## Q1 2026 Objectives

   ### Revenue Target
   - Monthly goal: $10,000
   - Current MTD: $4,500

   ### Key Metrics to Track
   | Metric | Target | Alert Threshold |
   |--------|--------|-----------------|
   | Client response time | < 24 hours | > 48 hours |
   ```

3. **Parse Individual Goals:**
   ```markdown
   ### Active Projects
   1. Project Alpha - Due Jan 15 - Budget $2,000
      Progress: 60% complete
   ```

4. **Calculate Progress:**
   ```python
   progress_percentage = (current_value / target_value) * 100

   # Determine status based on time elapsed
   time_elapsed_percentage = (current_date - start_date) / (due_date - start_date) * 100

   if progress_percentage >= time_elapsed_percentage * 0.9:
       status = "on_track"
   elif progress_percentage >= time_elapsed_percentage * 0.7:
       status = "at_risk"
   else:
       status = "behind"
   ```

**Error Handling:**
- If file not found → Log error, set goals_score = N/A
- If targets not specified → Use defaults or skip score
- If goals malformed → Parse what's valid, skip invalid

---

## Phase 2: Performance Scoring

### 2.1 Financial Score (0-100)

**Formula:**

```python
def calculate_financial_score(financial_data, targets):
    score = 0

    # Revenue Performance (40 points)
    revenue_percentage = financial_data["revenue"]["mtd"] / targets["revenue_monthly"]
    if revenue_percentage >= 0.9:
        score += 40  # On track or exceeding
    elif revenue_percentage >= 0.7:
        score += int(40 * revenue_percentage / 0.9)  # Partial credit
    # else: 0 points

    # Expense Control (30 points)
    expense_percentage = financial_data["expenses"]["mtd"] / targets["expense_budget"]
    if expense_percentage <= 1.0:
        score += 30  # Under budget
    elif expense_percentage <= 1.2:
        score += int(30 * (1.2 - expense_percentage) / 0.2)  # Partial credit
    # else: 0 points

    # Cash Flow Positive (20 points)
    cash_flow = financial_data["revenue"]["mtd"] - financial_data["expenses"]["mtd"]
    if cash_flow > 0:
        score += 20
    elif cash_flow > -targets["revenue_monthly"] * 0.1:  # Within 10% of revenue
        score += 10  # Partial credit
    # else: 0 points

    # No Overdue Invoices (10 points)
    if financial_data["invoices"]["overdue_count"] == 0:
        score += 10
    elif financial_data["invoices"]["overdue_count"] <= 2:
        score += 5  # Partial credit for few overdue
    # else: 0 points

    return min(score, 100)  # Cap at 100
```

**Trend Calculation:**

```python
def calculate_trend(current_score, last_week_score):
    diff = current_score - last_week_score
    if diff > 3:
        return "↗️"  # Improving
    elif diff < -3:
        return "↘️"  # Declining
    else:
        return "→"  # Stable
```

---

### 2.2 Operational Score (0-100)

**Formula:**

```python
def calculate_operational_score(operational_data, email_data, targets):
    score = 0

    # Task Completion Rate (40 points)
    if operational_data["tasks"]["completion_rate"] >= 90:
        score += 40
    elif operational_data["tasks"]["completion_rate"] >= 70:
        score += int(40 * operational_data["tasks"]["completion_rate"] / 100)
    # else: 0 points

    # Task Cycle Time (30 points)
    if "avg_cycle_time" in operational_data["tasks"]:
        # Assuming target cycle time defined in Business_Goals.md
        if operational_data["tasks"]["avg_cycle_time"] <= targets.get("avg_cycle_time", 3):
            score += 30
        elif operational_data["tasks"]["avg_cycle_time"] <= targets.get("avg_cycle_time", 3) * 1.5:
            # Partial credit if within 50% of target
            ratio = operational_data["tasks"]["avg_cycle_time"] / targets.get("avg_cycle_time", 3)
            score += int(30 * (1.5 - ratio) / 0.5)

    # Email Response Time (20 points)
    if email_data["avg_response_time"] < targets["email_response_target"]:
        score += 20
    elif email_data["avg_response_time"] < targets["email_response_target"] * 2:
        # Partial credit if under 2x target
        ratio = email_data["avg_response_time"] / targets["email_response_target"]
        score += int(20 * (2 - ratio))
    # else: 0 points

    # No Overdue High Priority Items (10 points)
    if operational_data["tasks"]["overdue_priority"]["high"] == 0 and email_data["pending_high_priority"] == 0:
        score += 10
    elif operational_data["tasks"]["overdue_priority"]["high"] <= 1:
        score += 5  # Partial credit
    # else: 0 points

    return min(score, 100)
```

---

### 2.3 Social Media Score (0-100)

**Formula:**

```python
def calculate_social_score(social_data, targets):
    score = 0

    # Posts Published vs Schedule (25 points)
    posts_ratio = social_data["summary"]["total_posts"] / targets["social_posts_per_week"]
    if posts_ratio >= 0.9:
        score += 25  # Met or exceeded schedule
    elif posts_ratio >= 0.7:
        score += int(25 * posts_ratio / 0.9)
    # else: 0 points

    # Engagement Rate (40 points)
    # Target engagement rate typically 2-5% depending on platform mix
    if social_data["summary"]["engagement_rate"] >= targets["social_engagement_target"]:
        score += 40
    elif social_data["summary"]["engagement_rate"] >= targets["social_engagement_target"] * 0.7:
        ratio = social_data["summary"]["engagement_rate"] / targets["social_engagement_target"]
        score += int(40 * ratio)
    # else: 0 points

    # Follower Growth (20 points)
    if social_data["summary"]["follower_growth"] > 0:
        score += 20  # Any positive growth
    # else: 0 points (neutral if no change)

    # Response Rate to Engagement (15 points)
    # This would require tracking comments/mentions responded to
    # For now, simplified: if engagement is high, assume response is happening
    if social_data["summary"]["total_engagement"] > 0:
        score += 15

    return min(score, 100)
```

---

### 2.4 Goal Achievement Score (0-100)

**Formula:**

```python
def calculate_goal_score(goals_data):
    if not goals_data["goals"]:
        return None  # No goals defined

    total_progress = 0
    total_weight = 0

    for goal in goals_data["goals"]:
        # Weight by priority if specified, otherwise equal weight
        weight = goal.get("priority_weight", 1.0)

        # Score based on status
        if goal["status"] == "on_track":
            goal_score = 100
        elif goal["status"] == "at_risk":
            goal_score = 70
        else:  # behind
            goal_score = max(goal["progress_percentage"], 40)  # Minimum 40 for effort

        total_progress += goal_score * weight
        total_weight += weight

    return int(total_progress / total_weight)
```

---

### 2.5 Overall Business Health Score

**Formula:**

```python
def calculate_overall_score(financial, operational, social, goals):
    # Remove None values (missing data)
    scores = [s for s in [financial, operational, social, goals] if s is not None]

    if not scores:
        return None, "insufficient_data"

    overall = sum(scores) / len(scores)

    # Determine status
    if overall >= 90:
        status = "excellent"
    elif overall >= 75:
        status = "good"
    elif overall >= 60:
        status = "fair"
    else:
        status = "needs_attention"

    return int(overall), status
```

---

## Phase 3: Bottleneck Detection

### 3.1 Process Bottlenecks

**Detection Logic:**

```python
def detect_process_bottlenecks(operational_data):
    bottlenecks = []

    for task in operational_data["completed_tasks"]:
        expected = task.get("expected_duration", 0)
        actual = task.get("actual_duration", 0)

        if expected > 0 and actual > expected * 1.5:
            delay = actual - expected

            # Classify severity
            if delay > expected:  # 100%+ delay
                severity = "critical"
            elif delay > expected * 0.5:  # 50%+ delay
                severity = "high"
            else:
                severity = "medium"

            bottleneck = {
                "task": task["title"],
                "expected": expected,
                "actual": actual,
                "delay": delay,
                "severity": severity,
                "impact": classify_impact(task),
                "root_cause": identify_root_cause(task)
            }

            bottlenecks.append(bottleneck)

    return sorted(bottlenecks, key=lambda x: severity_priority(x["severity"]))
```

**Root Cause Classification:**

```python
def identify_root_cause(task):
    # Check task notes for keywords
    notes = task.get("notes", "").lower()

    if "waiting" in notes or "blocked" in notes:
        return "Waiting on external party"
    elif "unclear" in notes or "requirements" in notes:
        return "Unclear requirements"
    elif "time" in notes or "capacity" in notes:
        return "Insufficient capacity"
    elif "technical" in notes or "bug" in notes:
        return "Technical blocker"
    else:
        return "Unknown - review task notes"
```

---

### 3.2 Financial Bottlenecks

**Detection Logic:**

```python
def detect_financial_bottlenecks(financial_data):
    bottlenecks = []

    # Overdue Invoices
    if financial_data["invoices"]["overdue_count"] > 0:
        bottlenecks.append({
            "type": "overdue_invoices",
            "severity": "high" if financial_data["invoices"]["overdue_total"] > 1000 else "medium",
            "description": f"{financial_data['invoices']['overdue_count']} invoices overdue",
            "impact": f"${financial_data['invoices']['overdue_total']} cash flow impact",
            "recommendation": "Follow up on overdue invoices, review payment terms"
        })

    # Budget Overruns
    for category, amount in financial_data["expenses"]["by_category"].items():
        budget = get_category_budget(category)  # From Business_Goals.md
        if budget and amount > budget * 1.2:
            bottlenecks.append({
                "type": "budget_overrun",
                "severity": "medium",
                "description": f"{category} expenses 20%+ over budget",
                "impact": f"${amount - budget} over budget",
                "recommendation": f"Review {category} expenses, identify savings opportunities"
            })

    return bottlenecks
```

---

### 3.3 Communication Bottlenecks

**Detection Logic:**

```python
def detect_communication_bottlenecks(email_data, social_data):
    bottlenecks = []

    # Slow Email Responses
    if email_data["avg_response_time"] > 48:
        bottlenecks.append({
            "type": "slow_email_response",
            "severity": "high",
            "description": f"Average email response time: {email_data['avg_response_time']} hours",
            "impact": "Client satisfaction at risk",
            "recommendation": "Set aside dedicated email processing time daily"
        })

    # Pending High Priority Emails
    if email_data["pending_high_priority"] > 2:
        bottlenecks.append({
            "type": "pending_high_priority_emails",
            "severity": "critical",
            "description": f"{email_data['pending_high_priority']} high-priority emails pending",
            "impact": "Urgent matters not addressed",
            "recommendation": "Process high-priority emails immediately"
        })

    return bottlenecks
```

---

## Phase 4: Trend Analysis

### 4.1 Week-over-Week Comparison

**Storage:** Maintain historical briefings in `Vault/Briefings/archives/`

**Comparison Logic:**

```python
def analyze_trends(current_data, last_week_briefing):
    trends = {}

    # Financial Trend
    trends["financial"] = {
        "revenue_change": calculate_percentage_change(
            current_data["revenue"]["weekly"],
            last_week_briefing["revenue"]["weekly"]
        ),
        "expense_change": calculate_percentage_change(
            current_data["expenses"]["weekly"],
            last_week_briefing["expenses"]["weekly"]
        ),
        "score_change": current_data["scores"]["financial"] - last_week_briefing["scores"]["financial"]
    }

    # Similar for operational, social, goals

    return trends
```

---

## Phase 5: Data Quality Checks

### 5.1 Validation Rules

**Before generating briefing, validate:**

```python
def validate_data_quality(collected_data):
    warnings = []
    errors = []

    # Check data freshness
    if collected_data["financial"]["last_sync"] > 48:  # hours
        warnings.append("Financial data >48h old - may be stale")

    # Check completeness
    if not collected_data["goals"]["targets"]:
        errors.append("Business_Goals.md not configured - cannot calculate goal scores")

    # Check consistency
    if collected_data["financial"]["revenue"]["mtd"] < collected_data["financial"]["revenue"]["weekly"]:
        errors.append("Data inconsistency: Weekly revenue exceeds MTD")

    return warnings, errors
```

**If errors present:**
- Log errors to `Vault/Logs/system/briefing_errors.log`
- Include "Data Quality Issues" section in briefing
- Set affected scores to N/A with explanation

---

## Configuration

### Default Thresholds

Can be overridden in `Vault/Business_Goals.md`:

```yaml
analysis_config:
  bottleneck_threshold: 1.5  # actual > expected * threshold
  score_trend_threshold: 3   # points change to be considered trend
  overdue_threshold: 30      # days for invoice to be overdue
  response_time_target: 24   # hours for email response
  engagement_rate_target: 0.03  # 3% engagement rate
```

---

*Framework Version: 1.0*
*Last Updated: 2026-01-12*
*For KPI definitions, see: [kpi-definitions.md](./kpi-definitions.md)*
*For recommendations logic, see: [recommendation-engine.md](./recommendation-engine.md)*
