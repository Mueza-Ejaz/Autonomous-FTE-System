# KPI Definitions

**Version:** 1.0 | **Purpose:** Comprehensive definitions, formulas, and benchmarks for all Key Performance Indicators

---

## Overview

This document defines every KPI (Key Performance Indicator) used in CEO Briefings. Each KPI includes its purpose, calculation formula, target values, and interpretation guidelines.

---

## Financial KPIs

### Revenue Performance

#### Weekly Revenue
**Definition:** Total revenue generated in the last 7 days

**Formula:**
```python
weekly_revenue = sum(transaction.amount for transaction in transactions
                     where transaction.type == "Revenue"
                     and transaction.date >= (today - 7 days))
```

**Target:** Variable based on business model
- **Consulting:** $2,000 - $5,000 per week
- **E-Commerce:** $5,000 - $20,000 per week
- **SaaS:** $1,000 - $10,000 per week (MRR growth)

**Interpretation:**
- **Green:** ≥90% of weekly target
- **Yellow:** 70-89% of weekly target
- **Red:** <70% of weekly target

---

#### Revenue MTD (Month-to-Date)
**Definition:** Total revenue from start of month to current date

**Formula:**
```python
mtd_revenue = sum(transaction.amount for transaction in transactions
                  where transaction.type == "Revenue"
                  and transaction.date >= first_day_of_month
                  and transaction.date <= today)
```

**Target:** Set in `Vault/Business_Goals.md`
- Default: $10,000/month for small business

**Progress Calculation:**
```python
days_elapsed = (today - first_day_of_month).days
days_in_month = total_days_in_month
expected_progress = (days_elapsed / days_in_month) * 100

actual_progress = (mtd_revenue / monthly_target) * 100

on_track = actual_progress >= expected_progress * 0.9
```

**Interpretation:**
- **Green:** Actual ≥90% of expected (on track)
- **Yellow:** Actual 70-89% of expected (slightly behind)
- **Red:** Actual <70% of expected (significantly behind)

---

### Expense Management

#### Weekly Expenses
**Definition:** Total expenses incurred in the last 7 days

**Formula:**
```python
weekly_expenses = sum(transaction.amount for transaction in transactions
                      where transaction.type == "Expense"
                      and transaction.date >= (today - 7 days))
```

**Target:** Variable based on business model
- Typically 40-60% of weekly revenue target

**Interpretation:**
- **Green:** ≤50% of weekly revenue
- **Yellow:** 51-70% of weekly revenue
- **Red:** >70% of weekly revenue (margin concern)

---

#### Expense MTD
**Definition:** Total expenses from start of month to current date

**Formula:**
```python
mtd_expenses = sum(transaction.amount for transaction in transactions
                   where transaction.type == "Expense"
                   and transaction.date >= first_day_of_month
                   and transaction.date <= today)
```

**Target:** Monthly budget set in `Vault/Business_Goals.md`
- Default: $6,000/month for small business

**Interpretation:**
- **Green:** ≤100% of prorated budget
- **Yellow:** 101-120% of prorated budget
- **Red:** >120% of prorated budget

---

#### Expense by Category
**Definition:** Breakdown of expenses by category for cost analysis

**Categories (Standard):**
- Software & Subscriptions
- Marketing & Advertising
- Office & Equipment
- Professional Services
- Travel & Meals
- Banking & Fees
- Taxes & Licenses
- Other

**Formula:**
```python
category_expenses = {
    category: sum(transaction.amount for transaction in transactions
                  where transaction.category == category
                  and transaction.date >= period_start)
    for category in categories
}
```

**Target:** Category budgets (if specified in Business_Goals.md)

**Interpretation:**
- Identify top 3 expense categories
- Flag any category >30% over budget
- Look for optimization opportunities in high-spend categories

---

### Cash Flow

#### Cash Flow
**Definition:** Net revenue minus expenses (profit/loss)

**Formula:**
```python
cash_flow = revenue - expenses

# Weekly
weekly_cash_flow = weekly_revenue - weekly_expenses

# MTD
mtd_cash_flow = mtd_revenue - mtd_expenses
```

**Target:**
- **Healthy:** Positive cash flow
- **Warning:** Negative but <10% of revenue
- **Critical:** Negative >10% of revenue

**Interpretation:**
- **Green:** Positive cash flow
- **Yellow:** Negative but improving trend
- **Red:** Negative and worsening trend

---

### Outstanding & Overdue

#### Outstanding Invoices
**Definition:** Total value of unpaid invoices

**Formula:**
```python
outstanding = sum(invoice.amount for invoice in invoices
                  where invoice.status == "Unpaid")

outstanding_count = count(invoices where status == "Unpaid")
```

**Target:**
- Keep outstanding <2x monthly revenue target
- No single invoice outstanding >60 days

**Interpretation:**
- **Green:** <Monthly revenue target
- **Yellow:** 1-2x monthly revenue target
- **Red:** >2x monthly revenue target

---

#### Overdue Invoices
**Definition:** Unpaid invoices past due date (typically >30 days)

**Formula:**
```python
overdue = sum(invoice.amount for invoice in invoices
              where invoice.status == "Unpaid"
              and (today - invoice.due_date).days > 30)

overdue_count = count(invoices meeting above criteria)

average_days_overdue = avg((today - invoice.due_date).days
                           for overdue invoices)
```

**Target:**
- **Ideal:** Zero overdue invoices
- **Acceptable:** <$1,000 or <2 invoices overdue
- **Critical:** >$5,000 or >5 invoices overdue

**Interpretation:**
- **Green:** 0 overdue
- **Yellow:** 1-2 overdue or <$1,000
- **Red:** 3+ overdue or >$1,000

---

### Subscription Costs

#### Monthly Subscription Total
**Definition:** Total recurring monthly subscription costs

**Detection Logic:**
```python
subscriptions = identify_recurring_expenses(
    pattern="same vendor + similar amount + monthly frequency"
)

monthly_subscription_total = sum(sub.amount for sub in subscriptions)
```

**Common Subscriptions:**
- Software: Adobe, Microsoft 365, Figma, Canva
- Cloud: AWS, Azure, Google Cloud
- Business: Xero, QuickBooks, Notion, Slack
- Marketing: LinkedIn Premium, Mailchimp, Buffer
- Entertainment: Netflix, Spotify (if business expense)

**Target:**
- Keep <10% of monthly revenue
- Regularly audit for unused subscriptions

**Interpretation:**
- Flag if >10% of monthly revenue
- Flag individual subscriptions with no recent activity

---

## Operational KPIs

### Task Management

#### Tasks Completed (Weekly)
**Definition:** Number of tasks marked complete in last 7 days

**Formula:**
```python
completed_weekly = count(tasks where completed_date >= (today - 7 days))
```

**Target:** Variable by business
- **Individual:** 5-15 tasks/week
- **Small Team:** 20-50 tasks/week

**Interpretation:**
- Compare to historical average
- Flag if <70% of historical average (productivity drop)

---

#### Task Completion Rate
**Definition:** Percentage of tasks completed vs total active + completed

**Formula:**
```python
total_tasks = active_tasks + completed_tasks
completion_rate = (completed_tasks / total_tasks) * 100
```

**Target:**
- **Excellent:** >90%
- **Good:** 80-90%
- **Fair:** 70-79%
- **Poor:** <70%

**Interpretation:**
- **Green:** >90%
- **Yellow:** 70-90%
- **Red:** <70%

---

#### Average Cycle Time
**Definition:** Average time from task creation to completion

**Formula:**
```python
cycle_times = [(task.completed_date - task.created_date).days
               for task in completed_tasks_this_period]

avg_cycle_time = sum(cycle_times) / len(cycle_times)
```

**Target:** Depends on task complexity
- **Simple tasks:** 1-3 days
- **Medium tasks:** 3-7 days
- **Complex projects:** 14-30 days

**Interpretation:**
- Compare to expected duration (if specified)
- Flag if actual >150% of expected
- Look for trends (increasing = bottleneck)

---

#### Overdue Tasks
**Definition:** Tasks past their due date that are still active

**Formula:**
```python
overdue_tasks = count(tasks where status == "Active"
                      and due_date < today)

# By priority
overdue_high = count(overdue_tasks where priority == "High")
overdue_medium = count(overdue_tasks where priority == "Medium")
overdue_low = count(overdue_tasks where priority == "Low")
```

**Target:**
- **Ideal:** 0 overdue high-priority tasks
- **Acceptable:** 0 high, <3 medium
- **Critical:** Any high-priority overdue

**Interpretation:**
- **Green:** 0 high-priority overdue
- **Yellow:** 1 high or 3+ medium overdue
- **Red:** 2+ high-priority overdue

---

### Email Performance

#### Emails Processed (Weekly)
**Definition:** Number of emails handled in last 7 days

**Formula:**
```python
processed_weekly = count(emails where processed_date >= (today - 7 days))
```

**Target:** Variable
- Compare to historical average
- No specific target (depends on business volume)

**Interpretation:**
- Track trends, not absolutes
- Flag if significant deviation from average (±30%)

---

#### Average Response Time
**Definition:** Average time from email received to email processed/responded

**Formula:**
```python
response_times = [(email.processed_date - email.received_date).total_seconds() / 3600
                  for email in processed_emails_this_period]

avg_response_time = sum(response_times) / len(response_times)  # in hours
```

**Target:**
- **Excellent:** <4 hours
- **Good:** <24 hours
- **Fair:** <48 hours
- **Poor:** >48 hours

**Interpretation:**
- **Green:** <24 hours
- **Yellow:** 24-48 hours
- **Red:** >48 hours

**Note:** Business context matters - B2B may have 24-48h acceptable

---

#### Response Time Breakdown
**Definition:** Distribution of response times for trend analysis

**Buckets:**
```python
response_time_breakdown = {
    "under_1h": count(emails where response_time < 1),
    "1_to_4h": count(emails where 1 <= response_time < 4),
    "4_to_24h": count(emails where 4 <= response_time < 24),
    "over_24h": count(emails where response_time >= 24)
}
```

**Ideal Distribution:**
- Under 1h: 10-20%
- 1-4h: 30-40%
- 4-24h: 40-50%
- Over 24h: <10%

**Interpretation:**
- If >30% over 24h → capacity or prioritization issue
- If >50% under 4h → excellent responsiveness

---

#### Pending High-Priority Emails
**Definition:** Urgent emails not yet processed

**Formula:**
```python
pending_high_priority = count(emails where status == "Pending"
                              and priority == "High")
```

**Target:**
- **Ideal:** 0
- **Acceptable:** <2
- **Critical:** ≥3

**Interpretation:**
- **Green:** 0
- **Yellow:** 1-2
- **Red:** 3+

---

## Social Media KPIs

### Publishing Metrics

#### Posts Published (Weekly)
**Definition:** Total posts published across all platforms in last 7 days

**Formula:**
```python
# Per platform
linkedin_posts = count(posts where platform == "LinkedIn"
                       and published_date >= (today - 7 days))

# Similarly for Facebook, Instagram, Twitter

total_posts = linkedin_posts + facebook_posts + instagram_posts + twitter_posts
```

**Target:** Set in `Vault/Business_Goals.md`
- **Typical:** 7-14 posts/week across all platforms
  - LinkedIn: 2-3/week
  - Facebook: 1-2/week
  - Instagram: 2-3/week
  - Twitter: 3-7/week

**Interpretation:**
- **Green:** ≥90% of scheduled posts published
- **Yellow:** 70-89% of scheduled posts published
- **Red:** <70% of scheduled posts published

---

#### Publishing Consistency
**Definition:** Actual posts vs scheduled posts

**Formula:**
```python
consistency_rate = (published_posts / scheduled_posts) * 100
```

**Target:**
- **Excellent:** 100% (all scheduled posts published)
- **Good:** 90-99%
- **Fair:** 80-89%
- **Poor:** <80%

**Interpretation:**
- Track for content calendar adherence
- Low consistency suggests capacity or prioritization issues

---

### Engagement Metrics

#### Total Engagement
**Definition:** Sum of all interactions across all platforms

**Formula:**
```python
# Per platform
platform_engagement = likes + comments + shares + saves

# Total
total_engagement = sum(platform_engagement for all platforms)
```

**Target:** Varies widely by audience size and industry
- Focus on engagement rate, not absolutes

**Interpretation:**
- Track trends, not absolutes
- Flag if week-over-week decrease >20%

---

#### Engagement Rate
**Definition:** Engagement per post relative to follower count

**Formula:**
```python
# Per platform
platform_engagement_rate = (platform_engagement / (posts * followers)) * 100

# Overall
overall_engagement_rate = (total_engagement / (total_posts * avg_followers)) * 100
```

**Benchmarks by Platform:**
- **LinkedIn:** 2-5% (high engagement)
- **Facebook:** 0.5-1% (low organic reach)
- **Instagram:** 1-3% (medium engagement)
- **Twitter:** 0.5-1% (low engagement)

**Target:**
- **Excellent:** Above platform benchmark
- **Good:** At platform benchmark
- **Fair:** 50-99% of benchmark
- **Poor:** <50% of benchmark

**Interpretation:**
- **Green:** ≥Benchmark
- **Yellow:** 70-99% of benchmark
- **Red:** <70% of benchmark

---

#### Engagement Breakdown
**Definition:** Distribution of engagement types

**Formula:**
```python
engagement_breakdown = {
    "likes": count(likes),
    "comments": count(comments),
    "shares": count(shares),
    "saves": count(saves)  # Instagram
}
```

**Quality Indicators:**
- **Comments:** Highest quality (active engagement)
- **Shares:** High quality (content resonated)
- **Saves:** High quality (valuable content)
- **Likes:** Lower quality (passive engagement)

**Ideal Ratio:**
- Likes: 70-80%
- Comments: 10-20%
- Shares: 5-10%
- Saves: 5-10% (Instagram)

**Interpretation:**
- High comment % → Strong community engagement
- High share % → Valuable content
- 100% likes → Content not resonating deeply

---

### Reach & Awareness

#### Reach/Impressions
**Definition:** Number of unique users who saw content

**Note:** Requires platform API access for accurate data

**Formula:**
```python
total_reach = sum(post.reach for post in posts_this_period)
avg_reach_per_post = total_reach / count(posts)
```

**Target:**
- Varies widely by follower count
- Focus on trend (increasing = good)

**Interpretation:**
- Track trend, not absolute
- Flag if declining >20% week-over-week

---

### Growth Metrics

#### Follower Growth
**Definition:** Net new followers across all platforms

**Formula:**
```python
# Per platform
follower_growth = current_followers - followers_last_week

# Percentage
follower_growth_rate = (follower_growth / followers_last_week) * 100
```

**Target:**
- **Early Stage (<1,000 followers):** 5-10%/week
- **Growth Stage (1,000-10,000):** 2-5%/week
- **Established (>10,000):** 1-3%/week

**Interpretation:**
- **Green:** Positive growth
- **Yellow:** Flat (0% growth)
- **Red:** Negative growth

---

#### Top Performing Content
**Definition:** Posts with highest engagement

**Ranking:**
```python
top_posts = sorted(posts, key=lambda p: p.engagement, reverse=True)[:3]
```

**Use Case:**
- Identify content themes that resonate
- Replicate successful formats
- Inform future content strategy

---

## Goal Achievement KPIs

### Goal Progress Percentage
**Definition:** Current progress toward goal target

**Formula:**
```python
progress_percentage = (current_value / target_value) * 100
```

**Example:**
- Goal: Generate $50,000 revenue in Q1
- Current (mid-Q1): $28,000
- Progress: 56%

---

### Goal Status
**Definition:** On track, at risk, or behind based on time elapsed

**Formula:**
```python
# Time-based calculation
time_elapsed = (today - goal_start_date).days
time_total = (goal_due_date - goal_start_date).days
time_elapsed_percentage = (time_elapsed / time_total) * 100

# Determine status
if progress_percentage >= time_elapsed_percentage * 0.9:
    status = "on_track"  # Within 10% of expected progress
elif progress_percentage >= time_elapsed_percentage * 0.7:
    status = "at_risk"  # 70-90% of expected progress
else:
    status = "behind"  # <70% of expected progress
```

**Status Indicators:**
- **🟢 On Track:** Progress ≥90% of time elapsed
- **🟡 At Risk:** Progress 70-89% of time elapsed (recoverable)
- **🔴 Behind:** Progress <70% of time elapsed (intervention needed)

---

### Days to Goal
**Definition:** Estimated days to reach goal at current pace

**Formula:**
```python
# Calculate velocity
days_since_start = (today - goal_start_date).days
velocity = current_value / days_since_start  # units per day

# Project to target
remaining = target_value - current_value
days_to_goal = remaining / velocity

# Compare to actual days remaining
days_remaining = (goal_due_date - today).days

on_track = days_to_goal <= days_remaining
```

---

## Business Health Scores

### Component Scores (0-100)

All component scores calculated as described in [analysis-framework.md](./analysis-framework.md).

**Dimensions:**
1. **Financial Score:** Revenue, expenses, cash flow, outstanding
2. **Operational Score:** Task completion, cycle time, email response
3. **Social Media Score:** Publishing, engagement, growth
4. **Goal Achievement Score:** Progress vs targets

---

### Overall Business Health Score
**Definition:** Weighted or unweighted average of component scores

**Formula:**
```python
# Unweighted (default)
overall_score = (financial_score + operational_score +
                 social_score + goal_score) / 4

# Weighted (optional)
overall_score = (
    financial_score * 0.40 +
    operational_score * 0.30 +
    social_score * 0.15 +
    goal_score * 0.15
)
```

**Status Mapping:**
- **90-100:** Excellent 📗
- **75-89:** Good 📗
- **60-74:** Fair 📙
- **<60:** Needs Attention 📕

---

## Benchmarks by Business Type

### Consulting/Services

| KPI | Target |
|-----|--------|
| Revenue/month | $5,000 - $20,000 |
| Profit margin | 50-70% |
| Email response | <24 hours |
| Task cycle time | 3-7 days |
| LinkedIn engagement | 3-5% |

### E-Commerce

| KPI | Target |
|-----|--------|
| Revenue/month | $10,000 - $100,000+ |
| Profit margin | 20-40% |
| Email response | <4 hours |
| Order fulfillment | 1-2 days |
| Social engagement | 2-4% (IG/FB) |

### SaaS

| KPI | Target |
|-----|--------|
| MRR growth | 10-20%/month (early) |
| Churn rate | <5%/month |
| Support response | <1 hour |
| Feature cycle | 14-30 days |
| Social engagement | 2-3% |

---

## Customization

To customize KPIs for your business, edit `Vault/Business_Goals.md`:

```markdown
## Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Monthly revenue | $10,000 | <$7,000 |
| Email response time | < 24 hours | > 48 hours |
| Task completion rate | > 90% | < 70% |
| Social posts per week | 10 | <7 |
| Social engagement rate | 3% | <2% |
```

---

*KPI Definitions Version: 1.0*
*Last Updated: 2026-01-12*
*For scoring formulas, see: [analysis-framework.md](./analysis-framework.md)*
*For recommendations, see: [recommendation-engine.md](./recommendation-engine.md)*
