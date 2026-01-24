# Security Rules for Approval System

This document defines security policies, validation rules, and safeguards for the approval workflow.

**Last Updated:** 2026-01-11
**Security Level:** Critical
**Review Frequency:** Monthly

---

## Core Security Principles

### 1. **Never Auto-Execute Sensitive Actions**
The AI Employee must NEVER bypass the approval system for:
- Financial transactions
- External communications
- Public-facing content
- Data deletion
- System modifications

### 2. **Principle of Least Privilege**
The AI Employee should only request permissions it needs for specific tasks. If an action can be done with read-only access, don't request write access.

### 3. **Defense in Depth**
Multiple layers of validation:
- Pre-approval checks (before creating approval request)
- Approval file validation (before execution)
- MCP server validation (at execution time)
- Post-execution audit (verify result)

### 4. **Audit Everything**
Every action (approved or rejected) must be logged with:
- Timestamp
- Action type and parameters
- Who/what approved it
- Execution result
- Any errors or warnings

---

## Never Auto-Approve (Zero Tolerance)

These actions **ALWAYS** require human approval with **NO exceptions**:

### Financial Actions
- 🔒 **All payments to new recipients** (even $0.01)
- 🔒 **All one-time payments > $100**
- 🔒 **All recurring payments > $50/month**
- 🔒 **Any changes to payment methods**
- 🔒 **Any changes to billing information**
- 🔒 **All refund requests**
- 🔒 **All dispute filings**
- 🔒 **Subscription cancellations > $20/month**

### Communication Actions
- 🔒 **All emails to new/unknown contacts**
- 🔒 **All bulk email sends** (>1 recipient in TO/CC)
- 🔒 **All emails with attachments**
- 🔒 **All emails mentioning pricing, contracts, or legal matters**
- 🔒 **All public social media posts**
- 🔒 **All social media replies/comments**
- 🔒 **All direct messages on any platform**

### Data & System Actions
- 🔒 **All file deletions**
- 🔒 **Moving files outside the vault**
- 🔒 **Modifying system files or configurations**
- 🔒 **Changing API credentials or secrets**
- 🔒 **Adding new integrations or webhooks**
- 🔒 **Database write operations (INSERT/UPDATE/DELETE)**

### Calendar & Commitments
- 🔒 **Sending meeting invitations**
- 🔒 **Accepting/declining meetings on your behalf**
- 🔒 **Canceling or rescheduling meetings**
- 🔒 **Adding attendees to meetings**

---

## Required Validation Checks

### Before Creating Approval Request

All these checks must pass before creating an approval file:

1. **Action Type Validation**
   ```
   ✅ Action is defined in approval-thresholds.md
   ✅ Action is not in "never auto-approve" list
   ✅ Action aligns with Vault/Company_Handbook.md policies
   ```

2. **Parameter Validation**
   ```
   ✅ All required parameters are present
   ✅ Parameter types are correct (email is valid email, amount is number)
   ✅ No null, undefined, or placeholder values
   ✅ Parameters pass format validation
   ```

3. **Business Rules Validation**
   ```
   ✅ Action supports goals in Vault/Business_Goals.md
   ✅ Within budget constraints (if financial)
   ✅ Within rate limits (if API call)
   ✅ Appropriate timing (business hours for client communications)
   ```

4. **Security Validation**
   ```
   ✅ No sensitive data in plaintext (passwords, API keys)
   ✅ Recipient/target is valid and verified
   ✅ Action doesn't violate security policies
   ✅ MCP server is available and authenticated
   ```

**If ANY check fails:** Do NOT create approval request. Log error and alert user.

---

### Before Executing Approved Action

All these checks must pass before execution:

1. **Approval File Validation**
   ```
   ✅ File is in Vault/Approved folder (not Vault/Pending_Approval)
   ✅ File has proper YAML frontmatter
   ✅ Required sections are present and complete
   ✅ Approval has not expired
   ```

2. **Re-Validation of Parameters**
   ```
   ✅ All parameters still present and valid
   ✅ No parameters have been corrupted
   ✅ Recipient/target still valid (not blocked/banned)
   ✅ Amount matches expected range (for payments)
   ```

3. **System State Validation**
   ```
   ✅ MCP server is online and authenticated
   ✅ API credentials are valid (not expired)
   ✅ Rate limits not exceeded
   ✅ No system maintenance in progress
   ```

4. **Double-Check for Duplicates**
   ```
   ✅ This exact action hasn't been executed already
   ✅ No duplicate approval files in Vault/Approved
   ✅ Check Vault/Done for recent identical actions
   ```

**If ANY check fails:** Do NOT execute. Move file back to `Vault/Pending_Approval` with error note.

---

## Expiration Policies

### Standard Expiration Times

| Action Type | Expiration | Rationale |
|-------------|-----------|-----------|
| **Payments** | 24 hours | Financial urgency, but time to verify |
| **Emails** | 48 hours | Allow time for review, not urgent |
| **Social Posts** | 72 hours | Content can wait, thorough review needed |
| **File Operations** | 48 hours | Data loss risk, allow time to verify |
| **Calendar** | 24 hours | Meeting coordination is time-sensitive |
| **API Writes** | 36 hours | Balance between safety and timeliness |

### Urgent Overrides

If priority is marked "urgent":
- Expiration time = 25% of standard
- Payment: 24h → 6h
- Email: 48h → 12h
- Social: 72h → 18h

**Warning:** Use "urgent" sparingly. Rushed approvals increase error risk.

### After Expiration

When approval expires:
1. File automatically moved to `Vault/Rejected`
2. Note added: "EXPIRED - No decision made within [X] hours"
3. Dashboard updated with expired approval
4. No action taken (safety default)
5. Can be re-requested if still needed

---

## Specific Security Rules by Action Type

### Email Security Rules

**Recipient Validation:**
```python
def validate_email_recipient(email):
    # Must be valid email format
    if not is_valid_email_format(email):
        return False

    # Check against known contacts
    if email in known_contacts:
        return True  # Can proceed

    # Unknown contact - require approval
    return "requires_approval"
```

**Content Scanning:**
- ⚠️ Flag emails containing: "password", "credit card", "SSN", "API key"
- ⚠️ Flag emails with pricing > $1000
- ⚠️ Flag emails to competitors or sensitive domains
- ✅ Allow informational emails with no sensitive data

**Attachment Security:**
- Scan for file types: .exe, .zip, .rar require extra approval note
- Check file size < 10MB for email
- Verify attachment actually exists at path
- Ensure attachment is inside vault (no system files)

---

### Payment Security Rules

**Amount Validation:**
```python
def validate_payment_amount(amount):
    # Must be positive number
    if amount <= 0:
        return False

    # Suspiciously round numbers > $1000
    if amount > 1000 and amount % 100 == 0:
        return "warn: suspiciously_round_number"

    # Amount > monthly budget limit
    if amount > monthly_budget_limit():
        return "requires_additional_approval"

    return True
```

**Payee Validation:**
- First payment to new payee always requires approval
- Verify payee name matches expected format (no weird characters)
- Check if payee is on blocklist
- For large amounts (>$1000), require two-factor human confirmation

**Duplicate Detection:**
- Check if same payee + amount paid in last 7 days
- If duplicate found, flag as "possible_duplicate_payment"
- Require human to confirm it's intentional

---

### Social Media Security Rules

**Content Validation:**
```python
def validate_social_content(content):
    # Check for sensitive information
    sensitive_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (maybe)
        r'password', r'secret', r'confidential'
    ]

    for pattern in sensitive_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return "contains_sensitive_data"

    return True
```

**Brand Safety:**
- ❌ Block posts with profanity, political content, controversial topics
- ⚠️ Warn if post is negative or complaining
- ✅ Ensure posts align with brand voice in `Vault/Company_Handbook.md`
- ✅ Verify hashtags are appropriate and professional

**Timing:**
- Don't post after 10 PM or before 7 AM (unless urgent)
- Spread posts throughout week (max 1 per day on LinkedIn)
- Check for duplicate posts in last 30 days

---

### File Operation Security Rules

**Delete Operations:**
```python
def validate_file_delete(filepath):
    # Never delete critical files
    critical_files = [
        'CLAUDE.md',
        'Company_Handbook.md',
        'Business_Goals.md',
        'Dashboard.md'
    ]

    if any(filepath.endswith(f) for f in critical_files):
        return "cannot_delete_critical_file"

    # Never delete outside vault
    if not is_inside_vault(filepath):
        return "cannot_delete_outside_vault"

    # Require approval for all deletes
    return "requires_approval"
```

**Move Operations:**
- Moving within vault: generally safe (auto-approve)
- Moving out of vault: always requires approval
- Bulk moves (>10 files): require approval even within vault

**Modify Operations:**
- Modifying critical files: always requires approval
- Modifying in `Vault/Done` folder: requires approval (archive should be immutable)
- Modifying user-created content: can auto-approve

---

## Rate Limiting & Throttling

### Email Rate Limits
- Max 10 emails per hour
- Max 50 emails per day
- If limit exceeded, queue additional emails for approval

### Social Media Rate Limits
- Max 1 LinkedIn post per day
- Max 3 Twitter posts per day
- Max 5 total social interactions per day

### API Call Rate Limits
- Respect MCP server rate limits
- Max 100 API calls per minute
- Max 1000 API calls per hour

### Payment Rate Limits
- Max 5 payments per day
- Max $5000 total per week
- Amounts above limits require additional verification

---

## Audit Requirements

### Required Audit Logs

Every action must be logged with:

```json
{
  "timestamp": "2026-01-11T16:00:00Z",
  "action_type": "email_send",
  "action_id": "unique_id",
  "actor": "claude_code",
  "approval_status": "approved",
  "approved_by": "human",
  "approved_at": "2026-01-11T14:00:00Z",
  "parameters": {
    "to": "recipient@example.com",
    "subject": "Invoice",
    "attachment_count": 1
  },
  "result": "success",
  "confirmation_id": "email_123456",
  "errors": null,
  "duration_ms": 1250
}
```

### Log Retention

- **Approval requests:** Keep all in `Vault/Done` folder (indefinite)
- **Execution logs:** Keep in `Vault/Dashboard.md` (indefinite)
- **Audit JSON:** Keep for minimum 90 days in `Vault/Logs` folder

### Monthly Security Audit

Review each month:
- [ ] All approval requests (identify patterns)
- [ ] All rejections (understand why)
- [ ] All failed executions (fix root causes)
- [ ] Rate limit violations (adjust if needed)
- [ ] Security rule violations (investigate)

---

## Emergency Procedures

### If Unauthorized Action Detected

1. **Immediate Actions:**
   - Stop all automation immediately
   - Review `Vault/Done` folder for unauthorized actions
   - Check `Vault/Dashboard.md` for suspicious activity
   - Verify MCP server connections

2. **Investigation:**
   - Identify what happened (logs, audit trail)
   - Determine if it was: bug, misconfiguration, or security breach
   - Document timeline and impact

3. **Remediation:**
   - Revoke compromised API credentials if applicable
   - Update security rules to prevent recurrence
   - Notify affected parties if necessary
   - Re-test approval workflow

4. **Post-Mortem:**
   - Write incident report
   - Update security rules and thresholds
   - Add new validation checks
   - Review all similar actions

### If MCP Server Compromised

1. Immediately revoke all API credentials
2. Disable MCP server connections
3. Review all actions taken via that server
4. Audit for data breaches
5. Rotate all secrets and keys
6. Re-test integration before re-enabling

---

## Compliance & Best Practices

### Privacy Protection

- Never log sensitive data (passwords, credit cards, SSNs)
- Redact sensitive fields in audit logs
- Use `[REDACTED]` placeholder for sensitive values
- Encrypt logs at rest if possible

### Data Minimization

- Only collect data needed for the action
- Don't store data longer than necessary
- Delete old logs after retention period
- Minimize PII in approval requests

### User Control

- User can reject any approval at any time
- User can modify approval parameters before approving
- User can revoke approvals after the fact (via audit review)
- User can disable specific action types in `Vault/Company_Handbook.md`

---

## Security Checklist

Before deploying to production, verify:

- [ ] All "never auto-approve" actions require approval
- [ ] All validation checks are implemented
- [ ] All MCP servers use authentication
- [ ] All API credentials are in secrets management
- [ ] Audit logging is enabled and working
- [ ] Rate limits are configured and enforced
- [ ] Expiration policies are set correctly
- [ ] Emergency stop procedure is documented
- [ ] Monthly audit schedule is configured
- [ ] Security rules are reviewed and approved

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-11 | Initial security rules for Silver Tier |

---

*These security rules are mandatory and must be followed by all skills in the AI Employee system.*

*Violations of these rules should be logged as security incidents and investigated.*

*Last Updated: 2026-01-11*
*Next Review: 2026-02-11*