# Email Priority Rules

**Purpose:** Define criteria for classifying emails by priority level (urgent/normal/low) to ensure time-sensitive matters are handled appropriately.

**Priority Levels:**
- **Urgent:** Requires response within 2-4 hours
- **Normal:** Requires response within 24-48 hours
- **Low:** Can wait 3-5 days or may not need response

---

## Table of Contents

1. [Urgency Keywords](#urgency-keywords)
2. [VIP Sender List](#vip-sender-list)
3. [Subject Line Patterns](#subject-line-patterns)
4. [Content Analysis Rules](#content-analysis-rules)
5. [Time-Sensitive Indicators](#time-sensitive-indicators)
6. [Auto-Approve vs Require Approval](#auto-approve-vs-require-approval)
7. [Escalation Criteria](#escalation-criteria)
8. [Priority Scoring System](#priority-scoring-system)

---

## 1. Urgency Keywords

### Urgent Priority Keywords

**Subject Line Keywords (High Weight):**
- "urgent"
- "asap"
- "immediate"
- "emergency"
- "critical"
- "time-sensitive"
- "deadline today"
- "expires today"
- "action required"
- "final notice"
- "overdue"
- "payment due"
- "issue"
- "problem"
- "broken"
- "down"
- "not working"

**Body Content Keywords (Medium Weight):**
- "as soon as possible"
- "by end of day"
- "by COB" (close of business)
- "within 24 hours"
- "deadline"
- "time sensitive"
- "need immediately"
- "can't wait"
- "blocking"
- "holding up"
- "preventing"

**Negative Urgency Keywords (Reduce Priority):**
- "no rush"
- "when you have time"
- "at your convenience"
- "whenever possible"
- "no hurry"
- "just following up"

---

## 2. VIP Sender List

### High-Priority Senders

**Active Clients** (Urgent if contains keywords, Normal otherwise):
- Current project clients
- Revenue-generating accounts
- Long-term partners

**Update VIP List:**
- Check `Vault/Business_Goals.md` "Active Projects" section
- Sender domains matching active client companies
- Individual contacts marked as VIP in `Vault/Company_Handbook.md`

**How to Identify VIP:**
1. Check sender email domain against known client domains
2. Check sender name against client list in `Vault/Business_Goals.md`
3. Check for previous email threads with same sender
4. Flag as VIP if matches any of above

### Regular Senders (Normal Priority):
- Known contacts not currently in active project
- Previous clients
- Professional network contacts

### Unknown Senders (Normal Priority by default):
- New inquiries (potential leads)
- First-time contacts
- Unless contains urgent keywords

### Automated Senders (Low Priority):
- noreply@*
- notifications@*
- newsletter@*
- automated-*
- Service alerts
- Marketing emails

---

## 3. Subject Line Patterns

### Urgent Patterns

**Financial/Payment:**
- "Invoice #{number} overdue"
- "Payment failed"
- "Account suspended"
- "Payment required"
- "Final notice"

**Technical Issues:**
- "Site down"
- "Error on {service}"
- "Not receiving {critical function}"
- "Broken {feature}"
- "Can't access"

**Client Escalations:**
- "Escalating: {issue}"
- "Need manager"
- "Complaint about"
- "Not satisfied with"

**Deadlines:**
- "Due today"
- "Deadline: {date that's soon}"
- "Expires {today/tomorrow}"

### Normal Patterns

**Inquiries:**
- "Question about"
- "Interested in"
- "Can you help with"
- "Information on"

**Meetings:**
- "Meeting request"
- "Schedule time"
- "Available to chat?"

**General Business:**
- "Following up on"
- "Update on {project}"
- "Regarding {topic}"

### Low Patterns

**Newsletters/Marketing:**
- "Newsletter"
- "Monthly update"
- "Tips and tricks"
- "What's new"

**Automated Notifications:**
- "Receipt for"
- "Order confirmation"
- "Shipping notification"
- "Account activity"

---

## 4. Content Analysis Rules

### Urgent Content Indicators

**Multiple Exclamation Marks:**
- Presence of "!!" or "!!!" suggests urgency
- But validate with other signals (could be spam)

**All Caps Words:**
- "URGENT", "ASAP", "IMPORTANT"
- Indicates sender emphasis
- Weight: Medium (validate with context)

**Specific Deadlines:**
- "Need by 5 PM today"
- "Deadline is {date within 24 hours}"
- "Must have by {soon}"
- Weight: High

**Financial Amounts:**
- Large dollar amounts mentioned (> $1000)
- "Payment of ${amount}"
- "Invoice for ${amount}"
- Weight: Medium (check if overdue)

**Problem Descriptions:**
- "is broken"
- "doesn't work"
- "getting errors"
- "can't complete"
- Weight: High if from client, Medium if from others

### Normal Content Indicators

**Questions:**
- Standard question format
- "Can you...?"
- "Would you...?"
- "Do you...?"

**Information Sharing:**
- "FYI"
- "Thought you'd like to know"
- "Here's the update"

**Polite Language:**
- "Please"
- "Thank you"
- "Appreciate"
- Indicates non-urgent, professional communication

### Low Priority Indicators

**Unsolicited Marketing:**
- Sales pitches from unknown senders
- Generic "Dear Sir/Madam"
- Unsubscribe links

**Automated Messages:**
- "This is an automated message"
- "Do not reply to this email"
- Tracking numbers, receipts

---

## 5. Time-Sensitive Indicators

### Immediate Response Needed (Urgent)

**Same-Day Deadlines:**
- Current date mentioned in deadline
- "Today", "EOD", "COB"
- Within 4 hours

**Service Outages:**
- "Down", "Offline", "Not working"
- From active client
- Impacts their business operations

**Payment Issues:**
- Account suspension threats
- Service interruption due to payment
- Overdue invoices with cutoff date

### 24-Hour Response Window (Normal)

**Next-Day Deadlines:**
- "Tomorrow", "by end of week"
- 1-3 business days

**General Inquiries:**
- New client leads
- Service questions
- Quote requests

**Meeting Requests:**
- Scheduling requests
- Availability checks

### Flexible Timeline (Low)

**No Specific Deadline:**
- "When you get a chance"
- "No rush"
- General updates

**Informational:**
- Newsletters
- Industry updates
- Non-actionable content

---

## 6. Auto-Approve vs Require Approval

### For Silver Tier: ALL EMAILS REQUIRE APPROVAL

**Why:**
- Safety during initial implementation
- Learn patterns before automation
- Prevent costly mistakes
- Build trust in AI system

### Future Auto-Approve Criteria (Gold Tier)

**Potential Auto-Approve Categories:**
- Replies to known contacts (< 200 words)
- Template-based responses (no customization needed)
- Thank you emails
- Meeting confirmations
- Receipt acknowledgments

**Always Require Approval:**
- New contacts (first-time communication)
- Financial discussions (pricing, invoices, payments)
- Commitments (deadlines, deliverables, contracts)
- Sensitive topics (legal, HR, confidential)
- Bulk sends (> 1 recipient)
- Emails with attachments
- Urgent matters (verify urgency)

---

## 7. Escalation Criteria

### When to Flag for Human Review

**Beyond AI Capability:**
- Complex technical questions
- Negotiation required
- Emotional/sensitive content
- Conflict resolution
- Legal implications
- Strategic decisions

**Unclear Intent:**
- Ambiguous requests
- Contradictory information
- Missing critical context
- Unable to categorize

**High-Stakes:**
- Major client communications
- Large financial amounts (> $5,000)
- Contract-related
- Reputation risk

**Escalation Process:**
1. Mark email as "REQUIRES_MANUAL_REVIEW"
2. Create approval with "ESCALATED" tag
3. Flag in Dashboard with 🚨
4. Include explanation of why escalated
5. Set priority to urgent
6. Human reviews before any response

---

## 8. Priority Scoring System

### Scoring Algorithm

**Start with Base Score: 0**

**Add Points:**
- VIP sender: +30 points
- Urgent keyword in subject: +20 points
- Urgent keyword in body: +10 points each (max +30)
- Specific deadline < 24 hours: +25 points
- Financial amount > $1000: +15 points
- Known client: +10 points
- Problem/issue mentioned: +15 points
- All caps in subject: +5 points

**Subtract Points:**
- "No rush" language: -20 points
- Automated sender: -30 points
- Newsletter pattern: -40 points
- Unsubscribe link present: -35 points

**Final Priority Assignment:**
- **Score ≥ 50:** Urgent
- **Score 20-49:** Normal
- **Score < 20:** Low

### Example Scoring

**Example 1: Urgent Client Email**
```
From: johndoe@activeclient.com (VIP)
Subject: URGENT: Website down - need immediate help

Base: 0
+ VIP sender: 30
+ "URGENT" in subject: 20
+ "immediate" in subject: 10
+ Known client: 10
+ Problem ("down"): 15
= Total: 85 → URGENT ✓
```

**Example 2: Normal Inquiry**
```
From: newlead@company.com
Subject: Question about your services

Base: 0
+ (No bonuses apply)
= Total: 0 → LOW (but new lead, bump to NORMAL)
```

**Example 3: Newsletter**
```
From: newsletter@service.com
Subject: Monthly tips and updates

Base: 0
- Automated sender: -30
- Newsletter pattern: -40
= Total: -70 → LOW ✓
```

### Override Rules

**Manual Overrides (Higher Priority Than Score):**
- All emails from `Vault/Business_Goals.md` active clients: Minimum Normal
- All emails with subject containing "invoice": Minimum Normal
- All emails from unknown but with urgent keywords: Review manually
- All first-time inquiries (potential leads): Minimum Normal

---

## Priority Handling Workflows

### Urgent Priority Workflow

1. **Immediate Dashboard Flag:** Add 🚨 emoji
2. **Create Approval:** Expiration 24 hours (not 48)
3. **Notification:** Consider external alert (future: SMS, Slack)
4. **Response Template:** Use "Urgent Escalation" template
5. **Human Review:** Check approval queue frequently

### Normal Priority Workflow

1. **Standard Processing:** Follow regular categorization
2. **Create Approval:** Expiration 48 hours
3. **Dashboard Log:** Standard entry
4. **Response Template:** Match to category
5. **Review Cadence:** Check approvals daily

### Low Priority Workflow

1. **Archive Decision:** Determine if response needed
2. **If No Response Needed:** Move to `Vault/Done` with "NO_RESPONSE" tag
3. **If Response Needed:** Create approval (72-hour expiration)
4. **Batch Processing:** Handle multiple low-priority together
5. **Dashboard Log:** Minimal entry

---

## Testing Priority Classification

### Test Cases

**Test 1: Urgent Client Issue**
```yaml
from: vip@client.com
subject: Production site down - URGENT
expected: Urgent
```

**Test 2: Normal Inquiry**
```yaml
from: lead@newcompany.com
subject: Interested in your services
expected: Normal
```

**Test 3: Newsletter**
```yaml
from: noreply@newsletter.com
subject: Your monthly digest
expected: Low
```

**Test 4: Payment Request**
```yaml
from: client@company.com
subject: Invoice request for January
expected: Normal (financial + client)
```

**Test 5: Spam**
```yaml
from: marketing@randomsite.com
subject: Exclusive offer just for you!
expected: Low
```

---

## Continuous Improvement

### Review Priority Accuracy

**Monthly Audit:**
1. Review emails marked as Urgent
2. Check if urgency was accurate
3. Update keyword lists if needed
4. Adjust scoring weights

**False Positive Tracking:**
- Email marked Urgent but wasn't
- Causes: Over-sensitive keywords, spam using urgent language
- Solution: Refine scoring algorithm

**False Negative Tracking:**
- Email marked Normal/Low but was Urgent
- Causes: Missed keywords, new patterns
- Solution: Add keywords, update VIP list

### Feedback Loop

**After Each Email:**
- Human marks if priority was correct
- Log corrections to `Vault/Logs/priority-feedback.log`
- Quarterly review of feedback
- Update rules accordingly

---

## Integration with Other Components

### Company_Handbook.md
- Check for response time SLAs
- VIP client definitions
- Priority guidelines

### Business_Goals.md
- Active client list
- Revenue targets (high-value clients)
- Current projects (time-sensitive)

### Dashboard.md
- Log all priority assignments
- Track urgent email volume
- Monitor response times

---

## Quick Reference Table

| Indicator | Urgent | Normal | Low |
|-----------|--------|--------|-----|
| **VIP Sender** | ✓ + keywords | ✓ no keywords | Rare |
| **Deadline** | < 24 hours | 1-3 days | No deadline |
| **Keywords** | urgent, asap, critical | question, request, update | newsletter, tips |
| **Response Time** | 2-4 hours | 24-48 hours | 3-5 days |
| **Approval Expiration** | 24 hours | 48 hours | 72 hours |
| **Dashboard Flag** | 🚨 | Standard | Minimal |
| **Auto-Approve** | Never | Never (Silver) | Never (Silver) |

---

**Last Updated:** 2026-01-11
**Status:** Ready for implementation
**Next Review:** Monthly or after 100 emails processed