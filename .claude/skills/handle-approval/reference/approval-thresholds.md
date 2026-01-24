# Approval Thresholds

This document defines what actions require human approval vs. what can be auto-approved by the AI Employee.

**Last Updated:** 2026-01-11
**Review Frequency:** Monthly

---

## Email Actions

### Auto-Approve
- ✅ Replies to known contacts (in Vault/Company_Handbook.md contact list)
- ✅ Responses < 200 words to familiar senders
- ✅ Email categorization and filing
- ✅ Drafting emails (not sending, just creating drafts)
- ✅ Reading and summarizing emails

### Require Approval
- 🔒 **All emails to new/unknown contacts**
- 🔒 Emails with attachments (any size)
- 🔒 Bulk email sends (>1 recipient in TO/CC)
- 🔒 Emails > 200 words
- 🔒 Replies containing sensitive information (pricing, contracts, etc.)
- 🔒 Forward actions to external domains
- 🔒 Emails mentioning payments or financial details

**Rationale:** Email represents the business publicly. New contacts and substantial communications require human oversight.

---

## Payment Actions

### Auto-Approve
- ✅ Recurring subscriptions < $50/month (pre-approved vendors only)
- ✅ Logging transactions (read-only)
- ✅ Categorizing expenses
- ✅ Generating payment reports

### Require Approval
- 🔒 **ALL payments to new payees (no exceptions)**
- 🔒 **ALL one-time payments > $100**
- 🔒 **ALL recurring payments > $50/month**
- 🔒 Changes to payment methods
- 🔒 Changes to billing information
- 🔒 Refund requests
- 🔒 Dispute filings
- 🔒 Subscription cancellations > $20/month

**Rationale:** Financial actions are irreversible and high-risk. Human approval is mandatory for all but the smallest recurring payments.

---

## Social Media Actions

### Auto-Approve
- ✅ Drafting posts (not publishing)
- ✅ Reading/monitoring social media
- ✅ Generating content ideas
- ✅ Analyzing post performance

### Require Approval
- 🔒 **ALL public posts (LinkedIn, Twitter, Facebook, Instagram)**
- 🔒 **ALL replies to comments/messages**
- 🔒 **ALL direct messages (DMs)**
- 🔒 Sharing/retweeting others' content
- 🔒 Changing profile information
- 🔒 Following/unfollowing accounts
- 🔒 Joining/leaving groups

**Rationale:** Social media is public-facing and affects brand reputation. All posts require human review before publication.

---

## File Operations

### Auto-Approve
- ✅ Creating files inside the Obsidian vault
- ✅ Reading any files
- ✅ Moving files within vault folders (Vault/Inbox → Vault/Needs_Action → Vault/Done)
- ✅ Creating subdirectories in vault
- ✅ Updating Vault/Dashboard.md, logs, and notes
- ✅ Creating backup copies

### Require Approval
- 🔒 **Deleting any files**
- 🔒 Moving files outside the vault
- 🔒 Modifying system files
- 🔒 Changing file permissions
- 🔒 Accessing files outside the vault
- 🔒 Bulk file operations (>10 files at once)
- 🔒 Modifying Vault/Company_Handbook.md or Vault/Business_Goals.md

**Rationale:** File operations can cause data loss. Deletions and external moves require explicit approval.

---

## API & Integration Actions

### Auto-Approve
- ✅ Reading data from APIs (GET requests)
- ✅ Searching/querying databases
- ✅ Generating reports from data
- ✅ Caching API responses

### Require Approval
- 🔒 **Creating/updating data via APIs (POST/PUT/PATCH)**
- 🔒 **Deleting data (DELETE requests)**
- 🔒 Changing API credentials
- 🔒 Adding new API integrations
- 🔒 Webhook configuration changes
- 🔒 OAuth authorizations

**Rationale:** Write operations via APIs can affect external systems. Read-only access is safe, modifications require approval.

---

## Calendar & Scheduling Actions

### Auto-Approve
- ✅ Reading calendar events
- ✅ Drafting meeting invitations (not sending)
- ✅ Suggesting meeting times
- ✅ Checking availability

### Require Approval
- 🔒 **Sending meeting invitations**
- 🔒 **Accepting/declining meetings on your behalf**
- 🔒 Canceling meetings
- 🔒 Rescheduling meetings
- 🔒 Adding other attendees to meetings
- 🔒 Modifying meeting details

**Rationale:** Calendar changes affect other people. All modifications require human approval.

---

## Task & Project Management Actions

### Auto-Approve
- ✅ Creating tasks in Obsidian vault
- ✅ Moving tasks between folders
- ✅ Updating task status
- ✅ Adding task notes and details
- ✅ Generating task reports
- ✅ Prioritizing tasks

### Require Approval
- 🔒 Deleting tasks
- 🔒 Assigning tasks to external collaborators
- 🔒 Changing project deadlines in Vault/Business_Goals.md
- 🔒 Marking critical milestones as complete
- 🔒 Creating external project dependencies

**Rationale:** Internal task management is safe to automate. External commitments or deletions require approval.

---

## Conditional Approval Rules

Some actions may auto-approve under specific conditions:

### Email to Known Contacts
**Condition:** Recipient in `Vault/Company_Handbook.md` contact list AND email < 200 words AND no attachments
**Result:** Auto-approve
**Otherwise:** Require approval

### Recurring Subscription Payment
**Condition:** Vendor in pre-approved list AND amount unchanged from last payment AND amount < $50
**Result:** Auto-approve
**Otherwise:** Require approval

### File Move Within Vault
**Condition:** Both source and destination are within vault folders AND not modifying core files (CLAUDE.md, Vault/Company_Handbook.md, Vault/Business_Goals.md)
**Result:** Auto-approve
**Otherwise:** Require approval

---

## Special Cases

### Urgent Actions
Even if an action normally requires approval, if marked as "urgent" priority:
- Approval expiration time reduced from 48 hours to 4 hours
- Dashboard flagged with high-priority alert
- But still requires approval (no bypass)

### Test/Sandbox Mode
When `DRY_RUN=true` or in test mode:
- All actions log their intent but don't execute
- No approval required (it's a simulation)
- Useful for testing skills and workflows

### After-Hours Actions
Actions created outside business hours (9 PM - 7 AM local time):
- Marked as "after-hours" in approval request
- Expiration extended by 12 hours
- Lower priority unless marked urgent

---

## Threshold Adjustment Process

To modify these thresholds:

1. Update this file with proposed changes
2. Create approval request for the change itself
3. Document rationale in Vault/Business_Goals.md
4. Test new threshold with dry-run
5. Monitor for 1 week after implementation
6. Review in next monthly audit

**Never adjust thresholds to bypass approvals for convenience.** These exist for safety.

---

## Quick Reference Table

| Action Type | Auto-Approve Criteria | Requires Approval |
|-------------|----------------------|-------------------|
| **Email** | Known contact, <200 words, no attachments | New contacts, attachments, bulk sends |
| **Payment** | Recurring < $50 (approved vendors) | New payees, >$100, changes |
| **Social** | Drafts only | All publishing, replies, DMs |
| **Files** | Create/read/move within vault | Delete, move outside, system files |
| **API** | Read-only (GET) | Write operations (POST/PUT/DELETE) |
| **Calendar** | Read/draft | Send invites, accept/decline |
| **Tasks** | Internal management | Delete, external assignments |

---

## Monitoring & Compliance

### Monthly Review
- Count auto-approved vs. approval-required actions
- Identify most common approval requests
- Adjust thresholds if too many false positives

### Audit Trail
- All auto-approved actions logged to Vault/Dashboard.md
- Approval-required actions logged to Vault/Pending_Approval files
- Executed approvals logged to Vault/Done folder

### Compliance Check
- Verify no unauthorized actions occurred
- Review all rejections for patterns
- Confirm thresholds align with Vault/Business_Goals.md

---

*This document is referenced by the handle-approval skill to determine when human approval is needed.*

*Last Updated: 2026-01-11*
*Version: 1.1 (Updated for Vault structure)*