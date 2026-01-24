# Email Categorization Guide

**Purpose:** Systematic classification of emails into business categories for appropriate handling and response template selection.

**Categories:**
1. Client Communications
2. Sales/Leads
3. Administrative
4. Internal Team
5. Spam/Low Priority

---

## Table of Contents

1. [Category Definitions](#category-definitions)
2. [Categorization Decision Tree](#categorization-decision-tree)
3. [Domain-Based Classification](#domain-based-classification)
4. [Content Pattern Matching](#content-pattern-matching)
5. [Subject Line Analysis](#subject-line-analysis)
6. [Sender Relationship Mapping](#sender-relationship-mapping)
7. [Special Cases](#special-cases)

---

## 1. Category Definitions

### Client Communications

**Definition:** Emails from active or previous clients regarding projects, services, or ongoing business relationships.

**Characteristics:**
- Sender is from known client domain
- References existing project or service
- May include: status updates, questions, change requests, feedback
- Business-critical communications

**Response Priority:** High (Normal to Urgent)

**Common Templates:**
- Project status update
- Support request response
- Client inquiry response
- Invoice request response

**Identification:**
- Check sender against Vault/Business_Goals.md active clients
- Look for project names in subject/body
- Check for previous email threads

---

### Sales/Leads

**Definition:** Emails from potential new clients inquiring about services, pricing, or availability.

**Characteristics:**
- First-time or infrequent contact
- Keywords: "interested in", "pricing", "quote", "services"
- Questions about offerings
- May request meeting or call

**Response Priority:** Medium-High (Normal, occasionally Urgent)

**Common Templates:**
- Client inquiry response
- Meeting scheduling response
- Generic professional response

**Identification:**
- Unknown sender asking about services
- Subject contains: "inquiry", "question about", "interested in"
- No previous business relationship
- Mention of competitors or alternatives

---

### Administrative

**Definition:** Business operations emails including invoices, contracts, scheduling, and routine business matters.

**Characteristics:**
- Invoicing and payment related
- Calendar and scheduling
- Document requests
- Routine business correspondence

**Response Priority:** Medium (Normal)

**Common Templates:**
- Invoice request response
- Meeting scheduling response
- Generic professional response
- Thank you email

**Identification:**
- Keywords: "invoice", "payment", "schedule", "calendar", "document"
- Administrative sender domains (accounting, HR, etc.)
- Regular business operations topics

---

### Internal Team

**Definition:** Communications from team members, partners, or internal stakeholders.

**Characteristics:**
- From team member email addresses
- Internal project discussions
- Coordination and collaboration
- May be informal tone

**Response Priority:** Medium (Normal, context-dependent)

**Common Templates:**
- Generic professional response
- Project status update
- Follow-up email

**Identification:**
- Sender is team member or partner
- Internal project references
- Collaborative language ("our", "we", "team")
- Less formal than client communications

**Note:** For solo operations (current setup), this category may be minimal.

---

### Spam/Low Priority

**Definition:** Unsolicited marketing, newsletters, automated notifications, and non-business-critical emails.

**Characteristics:**
- Marketing emails from unknown senders
- Newsletters and subscriptions
- Automated system notifications
- Social media notifications
- No action required

**Response Priority:** Low (typically no response needed)

**Action:** Archive to Vault/Done without response

**Identification:**
- Sender: noreply@, marketing@, newsletter@
- Contains unsubscribe link
- Generic greeting ("Dear valued customer")
- No personal address
- Promotional content

---

## 2. Categorization Decision Tree

```
START: Received Email

├─ Is sender automated (noreply@, automated-)?
│  ├─ YES → Check if important notification
│  │  ├─ Payment receipt, service alert → Administrative
│  │  └─ Newsletter, promo → Spam/Low Priority
│  └─ NO → Continue
│
├─ Is sender in known client list (Vault/Business_Goals.md)?
│  ├─ YES → Client Communications
│  └─ NO → Continue
│
├─ Is sender internal team/partner?
│  ├─ YES → Internal Team
│  └─ NO → Continue
│
├─ Does email ask about services/pricing?
│  ├─ YES → Sales/Leads
│  └─ NO → Continue
│
├─ Is email about invoice/payment/scheduling?
│  ├─ YES → Administrative
│  └─ NO → Continue
│
├─ Contains unsubscribe link or promotional language?
│  ├─ YES → Spam/Low Priority
│  └─ NO → Default to Sales/Leads (potential inquiry)

END: Category Assigned
```

---

## 3. Domain-Based Classification

### Client Domains

**Source:** Vault/Business_Goals.md "Active Projects" section

**How to Check:**
1. Extract sender email domain (e.g., @company.com)
2. Match against known client company names
3. Check for previous emails from same domain
4. If match → Client Communications

**Example:**
- If Vault/Business_Goals.md lists "Project Alpha - Client ABC Corp"
- Email from john@abccorp.com → Client Communications

**Update Frequency:** Weekly (as new clients onboard)

---

### Common Domain Patterns

**Marketing/Spam Indicators:**
- `@mail.{service}.com` (e.g., @mail.mailchimp.com)
- `noreply@{domain}`
- `do-not-reply@{domain}`
- `newsletter@{domain}`
- `marketing@{domain}`
- `info@{random-company}.com` (unknown)

**Administrative Services:**
- `@paypal.com`, `@stripe.com` (payment processing)
- `@xero.com` (accounting)
- `@zoom.us`, `@calendly.com` (scheduling)
- `notifications@{service}` (but verify content)

**Professional Networks:**
- `@linkedin.com` (check if personal message or notification)
- `jobs@{domain}` (typically low priority)

---

## 4. Content Pattern Matching

### Client Communications Patterns

**Keywords:**
- "project {name}"
- "our website"
- "the {service} we discussed"
- "as we agreed"
- "per our conversation"
- "following up on {project}"
- "status update"
- "change request"

**Phrases:**
- "Can you update..."
- "I noticed an issue with..."
- "When will {deliverable} be ready?"
- "Thanks for your work on..."

**Context Clues:**
- References specific deliverables
- Mentions previous meetings/calls
- Uses "our" or "we" (collaborative)
- Includes specific project details

---

### Sales/Leads Patterns

**Keywords:**
- "interested in your services"
- "looking for a {service}"
- "do you offer"
- "pricing for"
- "quote"
- "proposal"
- "can you help with"
- "need a {professional/service}"

**Phrases:**
- "I found your {website/profile/work}"
- "Can you tell me more about..."
- "What are your rates for..."
- "I'm looking to hire..."
- "Would you be available to..."

**Context Clues:**
- No previous relationship mentioned
- Asks basic service questions
- Requests information or quote
- May mention timeline/budget

---

### Administrative Patterns

**Keywords:**
- "invoice"
- "payment"
- "receipt"
- "billing"
- "schedule"
- "calendar"
- "appointment"
- "meeting time"
- "contract"
- "agreement"

**Phrases:**
- "Please send invoice for..."
- "I'd like to schedule..."
- "What's your availability..."
- "Payment has been sent"
- "Confirming our meeting..."

---

### Spam/Low Priority Patterns

**Keywords:**
- "limited time offer"
- "act now"
- "free trial"
- "unsubscribe"
- "exclusive deal"
- "congratulations"
- "winner"
- "claim your"
- "this is not spam" (ironically, usually spam)

**Phrases:**
- "Dear valued customer"
- "You've been selected"
- "Click here to"
- "Forward to a friend"
- "Prefer HTML email?"

**Formatting Clues:**
- Heavy HTML formatting
- Multiple images
- Large "Click Here" buttons
- Social media icons
- Footer with company address + unsubscribe

---

## 5. Subject Line Analysis

### Client Communications Subject Patterns

```
✓ "Project Alpha - Status Update"
✓ "Re: Website Redesign Question"
✓ "Issue with contact form"
✓ "Update to requirements for {project}"
✓ "Quick question about {deliverable}"
```

**Indicators:**
- Project names
- "Re:" or "Fwd:" (ongoing thread)
- Specific feature/deliverable names
- Company/client name in subject

---

### Sales/Leads Subject Patterns

```
✓ "Inquiry about your services"
✓ "Interested in working together"
✓ "Question about pricing"
✓ "Potential project opportunity"
✓ "Looking for a {service provider}"
```

**Indicators:**
- "inquiry", "interested", "looking for"
- Generic service mentions
- No specific project reference
- First contact indicators

---

### Administrative Subject Patterns

```
✓ "Invoice #1234"
✓ "Meeting request - {date}"
✓ "Payment confirmation"
✓ "Schedule for next week?"
✓ "Contract for signature"
```

**Indicators:**
- Document types (invoice, contract)
- Scheduling language
- Payment references
- Confirmation requests

---

### Spam Subject Patterns

```
✗ "URGENT: Claim your reward!!!"
✗ "You won't believe this..."
✗ "Newsletter: {Month} Edition"
✗ "Special offer just for you"
✗ "Re: {unrelated/random topic}"
```

**Indicators:**
- ALL CAPS
- Multiple exclamation marks
- Generic greetings
- Fake "Re:" (no previous conversation)
- Clickbait language

---

## 6. Sender Relationship Mapping

### Relationship Status Categories

**Active Client:**
- Currently working on project together
- Listed in Vault/Business_Goals.md active projects
- Regular communication pattern
- → Category: Client Communications

**Previous Client:**
- Past project completed
- No current active work
- May return for new projects
- → Category: Client Communications (or Sales/Leads for new inquiry)

**Lead (Prospect):**
- No previous business relationship
- Inquiring about services
- Not yet a client
- → Category: Sales/Leads

**Service Provider/Vendor:**
- Provides services to you (hosting, tools, etc.)
- Typically administrative communications
- → Category: Administrative

**Professional Network:**
- Colleagues, industry peers
- May be collaboration or networking
- → Category: Internal Team or Sales/Leads

**Unknown:**
- First contact, no context
- Evaluate based on content
- → Default to Sales/Leads (unless spam)

---

### Relationship Determination Process

1. **Check Email History:**
   - Search Vault/Done folder for previous emails from sender
   - If found, use same category unless context changed

2. **Check Vault/Business_Goals.md:**
   - Match sender to active projects
   - Match to client list if maintained

3. **Check Vault/Company_Handbook.md:**
   - Any defined client/partner lists
   - VIP contacts

4. **If No Match:**
   - Analyze content patterns
   - Default to appropriate category based on content

---

## 7. Special Cases

### Forwarded Emails

**Pattern:** Subject starts with "Fwd:"

**Categorization:**
- Check who forwarded (client vs. other)
- Analyze original email content
- May span multiple categories
- If from client forwarding issue → Client Communications
- If forwarding opportunity → Sales/Leads

---

### Reply Chains

**Pattern:** Subject starts with "Re:"

**Categorization:**
- Find original email in Vault/Done
- Use same category as original
- Maintains conversation continuity

**If Original Not Found:**
- Analyze current email content
- Categorize based on available information

---

### Multi-Topic Emails

**Challenge:** Email covers multiple categories

**Resolution:**
1. Identify primary purpose (what requires action)
2. Categorize based on primary topic
3. Note secondary topics in processing
4. If truly equal weight, default to higher priority category:
   - Client Communications > Sales/Leads > Administrative

**Example:**
- Client asks for status update (Client Communications)
- AND requests invoice (Administrative)
- → Categorize as Client Communications (primary relationship)

---

### Automated but Important

**Examples:**
- Payment processor notifications (successful payment)
- Service alerts (downtime, issues)
- Security alerts (login attempt, password reset)

**Categorization:**
- Despite automated sender
- Categorize by content importance
- Payment confirmation → Administrative
- Security alert → Administrative (Urgent)
- Generic newsletter → Spam/Low Priority

**Rule:** Content trumps sender type for important notifications

---

### Borderline Spam

**Challenge:** Marketing-style email from potentially legitimate source

**Evaluation Criteria:**
1. Is sender domain recognizable/professional?
2. Is there personalization (your name, specific reference)?
3. Is timing coincidental (just visited their site)?
4. Does it offer genuine value (industry insights)?

**If 3+ YES → Sales/Leads (could be legitimate outreach)**
**If mostly NO → Spam/Low Priority**

---

## Category Statistics & Refinement

### Track Category Distribution

**Goal:** Understand typical email breakdown

**Expected Distribution (Adjust based on reality):**
- Client Communications: 30-40%
- Sales/Leads: 20-30%
- Administrative: 15-25%
- Internal Team: 5-10%
- Spam/Low Priority: 20-30%

**Log to Dashboard:**
- Track category counts
- Identify trends
- Adjust categorization rules if needed

---

### Category Accuracy Validation

**Monthly Review:**
1. Sample 20 random categorized emails
2. Verify category assignment was correct
3. Calculate accuracy rate
4. Target: 90%+ accuracy

**If Accuracy Low:**
- Review misclassified emails
- Identify pattern (specific sender type, content pattern)
- Update categorization rules
- Add to pattern matching lists

---

## Integration with Processing Workflow

### Category → Template Mapping

| Category | Primary Templates | Priority Range |
|----------|------------------|----------------|
| Client Communications | Project Status, Support Request, Client Inquiry | Normal-Urgent |
| Sales/Leads | Client Inquiry, Meeting Scheduling | Normal-Urgent |
| Administrative | Invoice Request, Meeting Scheduling, Generic | Normal |
| Internal Team | Generic Professional, Project Status | Normal |
| Spam/Low Priority | None (Archive) | Low |

### Category → Action Mapping

| Category | Standard Action | Approval Required |
|----------|----------------|-------------------|
| Client Communications | Draft response | Yes (All) |
| Sales/Leads | Draft response | Yes (All) |
| Administrative | Draft response or Archive | Yes (if response) |
| Internal Team | Draft response | Yes (All) |
| Spam/Low Priority | Archive to Vault/Done | No |

---

## Quick Reference Checklist

**To Categorize an Email:**

- [ ] Check if sender is automated (noreply@, etc.)
  - If YES → Administrative or Spam based on content
- [ ] Check if sender is known client
  - If YES → Client Communications
- [ ] Check if asking about services/pricing
  - If YES → Sales/Leads
- [ ] Check if about invoice/payment/scheduling
  - If YES → Administrative
- [ ] Check for unsubscribe link or promo language
  - If YES → Spam/Low Priority
- [ ] If none above → Default to Sales/Leads

**Final Verification:**
- [ ] Category makes sense for content
- [ ] Priority aligns with category
- [ ] Appropriate template identified
- [ ] Action is clear (respond vs. archive)

---

## Example Categorizations

**Example 1:**
```yaml
From: john@activeclient.com
Subject: Project Alpha - Question about timeline
Content: "Hi, when will the homepage redesign be complete?"

Category: Client Communications ✓
Priority: Normal
Template: Project Status Update
```

**Example 2:**
```yaml
From: sarah@newcompany.com
Subject: Interested in your web design services
Content: "I'm looking for a developer for our new site..."

Category: Sales/Leads ✓
Priority: Normal
Template: Client Inquiry Response
```

**Example 3:**
```yaml
From: noreply@newsletter.com
Subject: Your Monthly Marketing Tips
Content: "Here are 10 tips to improve your marketing..."

Category: Spam/Low Priority ✓
Priority: Low
Action: Archive (no response)
```

---

**Last Updated:** 2026-01-11
**Status:** Ready for implementation
**Accuracy Target:** 90%+
**Review Frequency:** Monthly