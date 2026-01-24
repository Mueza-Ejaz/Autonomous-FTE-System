# Recommendation Engine

**Version:** 1.0 | **Purpose:** Logic and rules for generating proactive business recommendations

---

## Overview

The Recommendation Engine transforms data insights into actionable suggestions. This document defines the rules, prioritization logic, and decision trees used to generate cost optimizations, process improvements, growth opportunities, and risk alerts.

---

## Recommendation Categories

1. **💰 Cost Optimization** - Reduce expenses, eliminate waste
2. **📈 Process Improvements** - Increase efficiency, save time
3. **🚀 Growth Opportunities** - Expand reach, increase revenue
4. **⚠️ Risk Alerts** - Mitigate threats, prevent issues

---

## 1. Cost Optimization Recommendations

### 1.1 Subscription Audit

**Purpose:** Identify unused or duplicate subscriptions for cancellation

**Detection Logic:**

```python
def detect_subscription_opportunities(financial_data, activity_data):
    opportunities = []

    for subscription in financial_data["subscriptions"]:
        vendor = subscription["vendor"]
        cost = subscription["amount"]
        last_activity = get_last_activity(vendor, activity_data)

        # Rule 1: No activity in 30+ days
        if last_activity is None or (today - last_activity).days >= 30:
            opportunities.append({
                "type": "unused_subscription",
                "service": vendor,
                "cost_monthly": cost,
                "cost_annual": cost * 12,
                "issue": f"No activity in {days_since_activity} days",
                "action": "Cancel subscription",
                "priority": calculate_priority(cost),
                "effort": "Low"
            })

        # Rule 2: Duplicate functionality
        duplicate = check_duplicate_functionality(vendor, financial_data["subscriptions"])
        if duplicate:
            opportunities.append({
                "type": "duplicate_subscription",
                "service": vendor,
                "cost_monthly": cost,
                "cost_annual": cost * 12,
                "issue": f"Duplicate functionality with {duplicate}",
                "action": "Cancel one subscription",
                "priority": "Medium",
                "effort": "Low"
            })

        # Rule 3: Price increase >20%
        historical_cost = get_historical_cost(vendor)
        if historical_cost and (cost - historical_cost) / historical_cost > 0.2:
            opportunities.append({
                "type": "price_increase",
                "service": vendor,
                "cost_monthly": cost,
                "increase": cost - historical_cost,
                "issue": f"Price increased ${cost - historical_cost} ({percentage}%)",
                "action": "Negotiate or find alternative",
                "priority": "Medium",
                "effort": "Medium"
            })

    return opportunities
```

**Subscription Patterns to Detect:**

```python
SUBSCRIPTION_PATTERNS = {
    # Software
    "adobe.com": {"name": "Adobe Creative Cloud", "category": "Design"},
    "microsoft.com": {"name": "Microsoft 365", "category": "Productivity"},
    "notion.so": {"name": "Notion", "category": "Productivity"},
    "slack.com": {"name": "Slack", "category": "Communication"},
    "zoom.us": {"name": "Zoom", "category": "Communication"},
    "dropbox.com": {"name": "Dropbox", "category": "Storage"},
    "google.com/workspace": {"name": "Google Workspace", "category": "Productivity"},

    # Marketing & Social
    "linkedin.com": {"name": "LinkedIn Premium", "category": "Marketing"},
    "mailchimp.com": {"name": "Mailchimp", "category": "Marketing"},
    "buffer.com": {"name": "Buffer", "category": "Social Media"},
    "canva.com": {"name": "Canva", "category": "Design"},

    # Development
    "github.com": {"name": "GitHub", "category": "Development"},
    "aws.amazon.com": {"name": "AWS", "category": "Cloud"},
    "heroku.com": {"name": "Heroku", "category": "Cloud"},

    # Business
    "xero.com": {"name": "Xero", "category": "Accounting"},
    "quickbooks": {"name": "QuickBooks", "category": "Accounting"},

    # Entertainment (if business expense)
    "netflix.com": {"name": "Netflix", "category": "Entertainment"},
    "spotify.com": {"name": "Spotify", "category": "Entertainment"}
}
```

**Duplicate Functionality Detection:**

```python
DUPLICATE_CHECK = {
    # If using both, one may be redundant
    ("Notion", "Obsidian"): "Note-taking overlap",
    ("Slack", "Microsoft Teams"): "Communication overlap",
    ("Dropbox", "Google Drive"): "Storage overlap",
    ("Mailchimp", "ConvertKit"): "Email marketing overlap",
    ("Xero", "QuickBooks"): "Accounting overlap",
    ("Canva", "Adobe Creative Cloud"): "Design overlap (if only basic needs)"
}
```

**Priority Calculation:**

```python
def calculate_priority(monthly_cost):
    if monthly_cost >= 100:
        return "High"  # $1,200+ annual savings
    elif monthly_cost >= 50:
        return "Medium"  # $600+ annual savings
    else:
        return "Low"  # <$600 annual savings
```

---

### 1.2 Expense Category Optimization

**Purpose:** Identify categories with optimization potential

**Detection Logic:**

```python
def detect_category_optimizations(financial_data, targets):
    opportunities = []

    for category, amount in financial_data["expenses"]["by_category"].items():
        budget = targets.get(f"{category}_budget")

        # Rule: Category 20%+ over budget
        if budget and amount > budget * 1.2:
            overrun = amount - budget
            opportunities.append({
                "type": "budget_overrun",
                "category": category,
                "budget": budget,
                "actual": amount,
                "overrun": overrun,
                "issue": f"{category} expenses 20%+ over budget",
                "action": f"Review {category} expenses, identify savings",
                "priority": "High" if overrun > 500 else "Medium",
                "effort": "Medium"
            })

        # Rule: Single large unexpected expense
        transactions = get_category_transactions(category)
        for transaction in transactions:
            if transaction.amount > 500:  # Threshold
                similar_historical = find_similar_historical(transaction)
                if not similar_historical:
                    opportunities.append({
                        "type": "unusual_expense",
                        "category": category,
                        "amount": transaction.amount,
                        "vendor": transaction.vendor,
                        "issue": f"Unusual ${transaction.amount} expense",
                        "action": "Verify expense legitimacy, consider if recurring",
                        "priority": "Medium",
                        "effort": "Low"
                    })

    return opportunities
```

---

### 1.3 Payment Terms Optimization

**Purpose:** Improve cash flow through better payment terms

**Detection Logic:**

```python
def detect_payment_term_opportunities(financial_data):
    opportunities = []

    # Rule: Multiple invoices paid immediately (could negotiate terms)
    quick_payments = [t for t in financial_data["transactions"]
                      if t.type == "Expense"
                      and (t.payment_date - t.invoice_date).days <= 1]

    if len(quick_payments) > 5 and sum(t.amount for t in quick_payments) > 2000:
        opportunities.append({
            "type": "payment_terms",
            "issue": "Multiple immediate payments to vendors",
            "amount": sum(t.amount for t in quick_payments),
            "action": "Negotiate 30-day terms to improve cash flow",
            "priority": "Medium",
            "effort": "Medium",
            "benefit": "Improved cash flow, reduced pressure"
        })

    return opportunities
```

---

## 2. Process Improvement Recommendations

### 2.1 Email Management

**Purpose:** Improve email response times and efficiency

**Detection Logic:**

```python
def detect_email_improvements(email_data, targets):
    recommendations = []

    # Rule: Average response time >target
    if email_data["avg_response_time"] > targets["email_response_target"]:
        delay = email_data["avg_response_time"] - targets["email_response_target"]

        recommendations.append({
            "type": "email_response_time",
            "current": f"{email_data['avg_response_time']} hours",
            "target": f"{targets['email_response_target']} hours",
            "issue": f"Average response time {delay} hours over target",
            "recommendation": "Schedule dedicated email processing blocks (e.g., 9 AM, 2 PM, 5 PM)",
            "expected_benefit": "Improve client satisfaction, reduce response time by 30-50%",
            "priority": "High" if delay > 24 else "Medium",
            "effort": "Low"
        })

    # Rule: High volume of emails >24h response
    if email_data["response_time_breakdown"]["over_24h"] > email_data["processed_weekly"] * 0.3:
        recommendations.append({
            "type": "email_backlog",
            "current": f"{email_data['response_time_breakdown']['over_24h']} emails >24h",
            "issue": "30%+ of emails taking >24 hours to respond",
            "recommendation": "Implement email triage system: urgent (respond same day), normal (respond within 24h), low-priority (respond within 48h)",
            "expected_benefit": "Reduce backlog, prioritize high-impact emails",
            "priority": "High",
            "effort": "Low"
        })

    return recommendations
```

---

### 2.2 Task Management

**Purpose:** Improve task completion and reduce bottlenecks

**Detection Logic:**

```python
def detect_task_improvements(operational_data, targets):
    recommendations = []

    # Rule: Completion rate <90%
    if operational_data["tasks"]["completion_rate"] < 90:
        recommendations.append({
            "type": "task_completion",
            "current": f"{operational_data['tasks']['completion_rate']}%",
            "target": "90%+",
            "issue": "Task completion rate below target",
            "recommendation": "Implement weekly task review: identify blockers, reprioritize, delegate, or cancel low-value tasks",
            "expected_benefit": "Increase completion rate to 90%+, reduce task backlog",
            "priority": "Medium",
            "effort": "Low"
        })

    # Rule: Average cycle time 50%+ over expected
    if "avg_cycle_time" in operational_data["tasks"]:
        expected = targets.get("avg_cycle_time", 3)
        actual = operational_data["tasks"]["avg_cycle_time"]

        if actual > expected * 1.5:
            recommendations.append({
                "type": "task_cycle_time",
                "current": f"{actual} days",
                "expected": f"{expected} days",
                "issue": f"Tasks taking {actual - expected} days longer than expected",
                "recommendation": "Break large tasks into smaller milestones, identify recurring bottlenecks, automate repetitive work",
                "expected_benefit": f"Reduce cycle time by {(actual - expected) / actual * 100}%",
                "priority": "High",
                "effort": "Medium"
            })

    # Rule: Multiple overdue high-priority tasks
    if operational_data["tasks"]["overdue_priority"]["high"] >= 2:
        recommendations.append({
            "type": "overdue_tasks",
            "current": f"{operational_data['tasks']['overdue_priority']['high']} high-priority tasks overdue",
            "issue": "Multiple urgent tasks past due date",
            "recommendation": "Emergency task triage: Focus only on high-priority until caught up, reschedule or delegate medium/low",
            "expected_benefit": "Clear critical backlog, prevent client escalations",
            "priority": "Critical",
            "effort": "Low"
        })

    return recommendations
```

---

### 2.3 Communication Efficiency

**Purpose:** Streamline communication processes

**Detection Logic:**

```python
def detect_communication_improvements(email_data, social_data):
    recommendations = []

    # Rule: High email volume suggests need for FAQ/documentation
    if email_data["processed_weekly"] > 50:
        # Check for similar/repeated questions
        repeated = identify_repeated_email_topics(email_data)
        if repeated:
            recommendations.append({
                "type": "email_volume",
                "current": f"{email_data['processed_weekly']} emails/week",
                "issue": "High email volume with repeated questions",
                "recommendation": f"Create FAQ document for: {', '.join(repeated[:3])}. Share proactively with clients.",
                "expected_benefit": "Reduce email volume by 20-30%, save 3-5 hours/week",
                "priority": "Medium",
                "effort": "Medium"
            })

    # Rule: Low social media response to mentions
    # (Would require tracking mention responses)
    if social_data.get("mention_response_rate") and social_data["mention_response_rate"] < 80:
        recommendations.append({
            "type": "social_engagement",
            "current": f"{social_data['mention_response_rate']}% response rate",
            "issue": "Not responding to majority of social media mentions",
            "recommendation": "Set aside 15 minutes daily to respond to comments/mentions across all platforms",
            "expected_benefit": "Increase community engagement, improve brand perception",
            "priority": "Medium",
            "effort": "Low"
        })

    return recommendations
```

---

## 3. Growth Opportunity Recommendations

### 3.1 Social Media Growth

**Purpose:** Capitalize on high-performing content and engagement

**Detection Logic:**

```python
def detect_growth_opportunities(social_data, financial_data, operational_data):
    opportunities = []

    # Rule: High engagement suggests audience growth potential
    if social_data["summary"]["engagement_rate"] > 3.0:  # Above average
        opportunities.append({
            "type": "social_growth",
            "observation": f"Engagement rate {social_data['summary']['engagement_rate']}% (above {benchmark}% benchmark)",
            "opportunity": "Audience highly engaged - prime time to scale content",
            "action": "Increase posting frequency by 50% (e.g., 3 posts/week → 5 posts/week)",
            "expected_impact": "Grow followers 2-3x faster, increase lead generation",
            "investment": "2-3 hours/week additional time",
            "priority": "High",
            "timeframe": "Implement over next 2 weeks"
        })

    # Rule: One platform significantly outperforming others
    platform_performance = {
        "LinkedIn": social_data.get("linkedin", {}).get("engagement_rate", 0),
        "Facebook": social_data.get("facebook", {}).get("engagement_rate", 0),
        "Instagram": social_data.get("instagram", {}).get("engagement_rate", 0),
        "Twitter": social_data.get("twitter", {}).get("engagement_rate", 0)
    }

    top_platform = max(platform_performance, key=platform_performance.get)
    top_rate = platform_performance[top_platform]
    avg_rate = sum(platform_performance.values()) / len(platform_performance)

    if top_rate > avg_rate * 1.5:  # 50% better than average
        opportunities.append({
            "type": "platform_focus",
            "observation": f"{top_platform} engagement rate {top_rate}% vs {avg_rate}% average",
            "opportunity": f"{top_platform} audience most engaged",
            "action": f"Double down on {top_platform}: Increase to daily posting, experiment with different content formats",
            "expected_impact": "Maximize ROI on best-performing platform",
            "investment": "Reallocate time from low-performing platforms",
            "priority": "Medium",
            "timeframe": "1 month test"
        })

    return opportunities
```

---

### 3.2 Revenue Growth

**Purpose:** Identify opportunities to increase revenue

**Detection Logic:**

```python
def detect_revenue_opportunities(financial_data, operational_data):
    opportunities = []

    # Rule: Consistent revenue growth + capacity available
    if financial_data["revenue"]["trend"] == "increasing":
        if operational_data["tasks"]["completion_rate"] > 90:
            # Have capacity to take on more work
            opportunities.append({
                "type": "revenue_capacity",
                "observation": "Revenue growing AND task completion rate >90%",
                "opportunity": "Have capacity to take on additional clients",
                "action": "Increase marketing effort: boost social posts, reach out to warm leads, ask current clients for referrals",
                "expected_impact": "10-20% revenue increase within 2 months",
                "investment": "5 hours/week on business development",
                "priority": "High",
                "timeframe": "Start immediately"
            })

    # Rule: High-value clients identified
    high_value_clients = identify_high_value_clients(financial_data)
    if high_value_clients:
        opportunities.append({
            "type": "client_expansion",
            "observation": f"{len(high_value_clients)} clients account for {calculate_percentage(high_value_clients)}% of revenue",
            "opportunity": "Existing high-value clients for upsell",
            "action": f"Schedule check-in calls with: {', '.join(high_value_clients[:3])}. Ask about additional needs, offer expanded services.",
            "expected_impact": "15-25% increase from existing clients (lowest cost acquisition)",
            "investment": "3-4 hours for client calls",
            "priority": "High",
            "timeframe": "Next 2 weeks"
        })

    return opportunities
```

---

### 3.3 Efficiency Gains

**Purpose:** Identify automation and systemization opportunities

**Detection Logic:**

```python
def detect_efficiency_opportunities(operational_data, email_data, financial_data):
    opportunities = []

    # Rule: Recurring manual tasks
    recurring_tasks = identify_recurring_tasks(operational_data)
    if recurring_tasks:
        for task in recurring_tasks:
            if task["frequency"] >= 4:  # 4+ times per month
                time_spent = task["avg_duration"] * task["frequency"]
                if time_spent > 2:  # 2+ hours/month
                    opportunities.append({
                        "type": "automation",
                        "observation": f"Task '{task['name']}' performed {task['frequency']} times/month ({time_spent} hours)",
                        "opportunity": "Automate recurring manual work",
                        "action": f"Investigate automation for: {task['name']}. Options: Create skill, use tool like Zapier, or hire VA.",
                        "expected_impact": f"Save {time_spent} hours/month ({time_spent * 12} hours/year)",
                        "investment": "5-10 hours setup time",
                        "priority": "Medium",
                        "timeframe": "1 month"
                    })

    return opportunities
```

---

## 4. Risk Alert Recommendations

### 4.1 Financial Risks

**Purpose:** Flag financial threats early

**Detection Logic:**

```python
def detect_financial_risks(financial_data, targets):
    risks = []

    # Rule: Cash flow negative for 2+ consecutive weeks
    if is_cash_flow_negative_consecutive(financial_data, weeks=2):
        risks.append({
            "risk": "Negative Cash Flow Trend",
            "severity": "Critical",
            "probability": "High",
            "impact": "High",
            "description": "Cash flow negative for 2+ consecutive weeks",
            "current_status": f"${financial_data['cash_flow']['weekly']} this week",
            "mitigation": [
                "Follow up on all outstanding invoices immediately",
                "Review and reduce non-essential expenses",
                "Consider short-term credit line as safety net",
                "Accelerate new client acquisition"
            ],
            "timeline": "Act within 3 days",
            "owner": "You (CEO)"
        })

    # Rule: Revenue trending down 3+ consecutive weeks
    if financial_data["revenue"]["trend"] == "declining" and financial_data["revenue"]["trend_weeks"] >= 3:
        risks.append({
            "risk": "Revenue Decline",
            "severity": "High",
            "probability": "High",
            "impact": "High",
            "description": f"Revenue declining for {financial_data['revenue']['trend_weeks']} weeks",
            "current_status": f"Weekly revenue: ${financial_data['revenue']['weekly']} (down {financial_data['revenue']['trend_percentage']}% from peak)",
            "mitigation": [
                "Analyze root cause: Lost clients? Seasonality? Market change?",
                "Increase sales/marketing activity immediately",
                "Reach out to past clients for repeat business",
                "Consider promotional offers to stimulate demand"
            ],
            "timeline": "Start this week",
            "owner": "You (CEO)"
        })

    # Rule: Overdue invoices accumulating
    if financial_data["invoices"]["overdue_total"] > targets["revenue_monthly"] * 0.5:
        risks.append({
            "risk": "Overdue Invoice Accumulation",
            "severity": "High",
            "probability": "Medium",
            "impact": "High",
            "description": f"${financial_data['invoices']['overdue_total']} in overdue invoices (>50% of monthly revenue target)",
            "current_status": f"{financial_data['invoices']['overdue_count']} invoices overdue, average {avg_days_overdue} days",
            "mitigation": [
                "Send payment reminders immediately",
                "Call clients with >60 day overdue invoices",
                "Consider stricter payment terms for future work",
                "Evaluate if clients are credit risks"
            ],
            "timeline": "This week",
            "owner": "You (CEO)"
        })

    return risks
```

---

### 4.2 Operational Risks

**Purpose:** Flag operational threats and bottlenecks

**Detection Logic:**

```python
def detect_operational_risks(operational_data, email_data):
    risks = []

    # Rule: Task backlog growing
    if operational_data["tasks"]["active"] > operational_data["tasks"]["completed_last_month"]:
        risks.append({
            "risk": "Task Backlog Accumulation",
            "severity": "Medium",
            "probability": "High",
            "impact": "Medium",
            "description": f"{operational_data['tasks']['active']} active tasks vs {operational_data['tasks']['completed_last_month']} completed last month",
            "current_status": "Tasks accumulating faster than completion",
            "mitigation": [
                "Conduct task audit: Cancel/delegate/defer low-priority items",
                "Block time for deep work to clear backlog",
                "Consider hiring contractor for overload",
                "Evaluate if over-committed on projects"
            ],
            "timeline": "Within 1 week",
            "owner": "You (CEO)"
        })

    # Rule: Multiple high-priority items overdue
    if operational_data["tasks"]["overdue_priority"]["high"] >= 2:
        risks.append({
            "risk": "Critical Tasks Overdue",
            "severity": "Critical",
            "probability": "High",
            "impact": "High",
            "description": f"{operational_data['tasks']['overdue_priority']['high']} high-priority tasks past due",
            "current_status": "Urgent matters not being addressed",
            "mitigation": [
                "Clear calendar TODAY, focus only on overdue high-priority",
                "Communicate with affected clients about delays",
                "Determine root cause: Over-commitment? Underestimation? Distractions?",
                "Implement better task estimation and prioritization"
            ],
            "timeline": "Immediate (today)",
            "owner": "You (CEO)"
        })

    # Rule: Email response time degrading
    if email_data["avg_response_time"] > email_data.get("historical_avg", 24) * 1.5:
        risks.append({
            "risk": "Client Communication Delays",
            "severity": "Medium",
            "probability": "High",
            "impact": "Medium",
            "description": f"Email response time {email_data['avg_response_time']} hours (50%+ worse than historical average)",
            "current_status": "Client communications being delayed",
            "mitigation": [
                "Check inbox daily at set times (morning/afternoon/evening)",
                "Set up email filters to prioritize client emails",
                "Use templates for common responses to save time",
                "If overwhelmed, hire VA for email triage"
            ],
            "timeline": "This week",
            "owner": "You (CEO)"
        })

    return risks
```

---

### 4.3 Goal Risks

**Purpose:** Flag goals at risk of not being achieved

**Detection Logic:**

```python
def detect_goal_risks(goals_data):
    risks = []

    for goal in goals_data["goals"]:
        if goal["status"] == "behind":
            # Calculate how far behind
            time_elapsed_pct = calculate_time_elapsed_percentage(goal)
            progress_pct = goal["progress_percentage"]
            gap = time_elapsed_pct - progress_pct

            risks.append({
                "risk": f"Goal at Risk: {goal['name']}",
                "severity": "High" if gap > 30 else "Medium",
                "probability": "High",
                "impact": "Medium",
                "description": f"Goal {progress_pct}% complete but {time_elapsed_pct}% of time elapsed",
                "current_status": f"{gap}% behind schedule",
                "mitigation": [
                    f"Assess if goal still realistic by {goal['due_date']}",
                    "Reallocate resources/time to this goal",
                    "Break into smaller milestones for momentum",
                    "Consider revising goal target or deadline if external factors changed"
                ],
                "timeline": "This week",
                "owner": "You (CEO)"
            })

    return risks
```

---

## Prioritization Framework

### Priority Scoring

All recommendations scored on 3 dimensions:

```python
def calculate_recommendation_priority(recommendation):
    # Impact: Benefit magnitude
    impact_score = {
        "Critical": 10,
        "High": 7,
        "Medium": 4,
        "Low": 2
    }[recommendation.get("impact", "Medium")]

    # Effort: Time/cost to implement
    effort_score = {
        "Low": 8,  # Easy wins score high
        "Medium": 5,
        "High": 2   # Hard tasks score low
    }[recommendation.get("effort", "Medium")]

    # Urgency: Time-sensitivity
    urgency_score = {
        "Immediate": 10,
        "This week": 7,
        "This month": 4,
        "Quarter": 2
    }[recommendation.get("timeline", "This month")]

    # Total priority score
    priority_score = (impact_score * 0.4) + (effort_score * 0.3) + (urgency_score * 0.3)

    return priority_score
```

### Recommendation Limits

To avoid overwhelming the user, limit recommendations per briefing:

```python
RECOMMENDATION_LIMITS = {
    "cost_optimization": 3,  # Top 3 cost savings
    "process_improvement": 2,  # Top 2 processes
    "growth_opportunity": 2,  # Top 2 opportunities
    "risk_alert": 5  # All critical/high risks
}
```

---

## Output Format

### Standard Recommendation Structure

```python
recommendation = {
    "type": "cost_optimization | process_improvement | growth_opportunity | risk_alert",
    "title": "Brief title",
    "observation": "What data shows",
    "issue": "What's wrong (for problems)" or "opportunity": "What's possible (for opportunities)",
    "action": "Specific recommended action",
    "expected_benefit": "Quantified benefit (savings, time, revenue)",
    "investment": "Required time/cost",
    "priority": "Critical | High | Medium | Low",
    "effort": "Low | Medium | High",
    "timeline": "When to act"
}
```

---

*Recommendation Engine Version: 1.0*
*Last Updated: 2026-01-12*
*For analysis methods, see: [analysis-framework.md](./analysis-framework.md)*
*For KPIs, see: [kpi-definitions.md](./kpi-definitions.md)*
