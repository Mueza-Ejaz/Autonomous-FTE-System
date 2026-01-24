# Approval Request Template

This is the standard format for all approval request files created by the AI Employee.

**Usage:** Copy this template when creating new approval requests in `Vault/Pending_Approval` folder.

---

## File Naming Convention

**Format:** `APPROVAL_[TYPE]_[DESCRIPTION]_[DATE].md`

**Examples:**
- `APPROVAL_EMAIL_ClientA_Invoice_2026-01-11.md`
- `APPROVAL_PAYMENT_SubscriptionRenewal_2026-01-11.md`
- `APPROVAL_SOCIAL_LinkedInPost_ProjectUpdate_2026-01-11.md`
- `APPROVAL_FILE_DeleteOldBackups_2026-01-11.md`

**Rules:**
- Use underscores `_` not spaces
- Use descriptive names (include recipient/target)
- Include date in YYYY-MM-DD format
- Keep filename < 100 characters

---

## Template Structure

```markdown
---
type: approval_request
action: [email | payment | social | file | api | calendar | other]
created: [YYYY-MM-DDTHH:MM:SSZ]
expires: [YYYY-MM-DDTHH:MM:SSZ]
priority: [low | normal | high | urgent]
status: pending
source_skill: [name of skill that created this request]
---

## Action Summary
[One clear sentence describing what action will be taken]

## Details
- **Action Type:** [Specific type: send_email, make_payment, publish_post, etc.]
- **Target:** [Email address / Payment recipient / Platform / File path]
- **Reason:** [Why this action is needed - context from task/message]
- **Source:** [What triggered this: email from X, scheduled task, user request]

## Parameters

### [Action-Specific Parameters]
[List all parameters needed to execute the action]

**Example for Email:**
- To: recipient@example.com
- CC:
- BCC:
- Subject: [Subject line]
- Body: [See draft below or inline]
- Attachments: [List files]
- Reply-To: [If different from sender]

**Example for Payment:**
- Payee: [Company/Person Name]
- Amount: $XXX.XX
- Currency: USD
- Account: [Last 4 digits: XXXX]
- Reference: [Invoice #, Description]
- Payment Method: [Credit Card / Bank Transfer / PayPal]

**Example for Social Post:**
- Platform: [LinkedIn / Twitter / Facebook / Instagram]
- Content: [See draft below]
- Media: [Image/Video files if any]
- Scheduled Time: [If scheduling vs immediate]
- Tags/Mentions: [People/companies to tag]
- Hashtags: [List of hashtags]

**Example for File Operation:**
- Operation: [delete / move / modify]
- Source Path: /path/to/file
- Destination Path: [If moving]
- Affected Files: [List if multiple]

## Draft Content / Preview

[For emails, social posts, or file modifications: show the actual content]

### Email Draft Example:
```
Subject: January 2026 Invoice - $1,500

Hi [Client Name],

Thank you for your business this month. Please find attached the invoice
for services provided in January 2026.

Invoice Details:
- Invoice #: 2026-001
- Amount Due: $1,500.00
- Due Date: January 31, 2026
- Services: [List of services]

Payment can be made via [payment methods]. Please let me know if you
have any questions.

Best regards,
[Your Name]
```

### Social Post Draft Example:
```
Just completed another successful project! 🎉

Delivered a custom automation solution for [Client - confidential] that
saves them 10+ hours per week on routine tasks.

Key features:
• AI-powered email processing
• Smart task prioritization
• Automated reporting

Interested in streamlining your workflows? Let's connect!

#Automation #AI #Productivity #BusinessEfficiency
```

## Risks & Considerations

**Potential Risks:**
- Risk 1: [Description of what could go wrong]
- Risk 2: [Another potential issue]

**Mitigations:**
- Mitigation 1: [How risk is minimized]
- Mitigation 2: [Safety measures in place]

**Impact if Rejected:**
- [What happens if this approval is denied]

## Business Alignment

**Relates to Business Goal:**
- [Reference specific goal from Vault/Business_Goals.md]
- [How this action supports that goal]

**Budget Impact:**
- Cost: $XXX (if applicable)
- Budget Category: [From Vault/Business_Goals.md]
- Within Budget: Yes/No

## Security Validation

✅ **Pre-Approval Checks Passed:**
- [ ] Action type allowed by Vault/Company_Handbook.md
- [ ] Parameters validated against security-rules.md
- [ ] Recipient/target verified (if applicable)
- [ ] Amount within thresholds (if payment)
- [ ] No sensitive data exposure
- [ ] MCP server available and configured

## Instructions for Human

### To Approve This Action:
1. Review all details carefully
2. Verify parameters are correct (amounts, recipients, content)
3. Check content/preview for accuracy and appropriateness
4. **Move this file to `Vault/Approved` folder**
5. The AI will detect the approval and execute the action
6. Execution log will be added to this file

### To Reject This Action:
1. **Move this file to `Vault/Rejected` folder**
2. **Add your rejection reason at the bottom** (see format below)
3. The AI will log the rejection and archive the file
4. No action will be taken

### To Modify Before Approving:
1. Edit the parameters or content in this file directly
2. Save changes
3. Move to `Vault/Approved` folder
4. The AI will use your modified version

---

## Execution Log
[This section is automatically filled after approval/rejection]

**Status:** [Pending / Approved / Rejected / Executed / Failed]

**Approved By:** [Human / System]
**Approved At:** [Timestamp]

**Executed By:** claude_code
**Executed At:** [Timestamp]

**Result:** [Success / Failed]

**Details:**
- Confirmation ID: [If applicable - email sent ID, transaction ID, post URL]
- Error Message: [If failed]
- Retry Attempts: [If applicable]

**Logs:**
- Dashboard Updated: [Yes/No]
- Audit Trail: Vault/Done/[filename]

---

## Rejection Information
[Only filled if rejected - human adds this]

**Rejected By:** [Your name]
**Rejected At:** [Timestamp]
**Reason:** [Explain why you rejected this]

**Feedback for AI:**
[Optional: What should the AI do differently next time?]

---
```

---

## Template Variations by Action Type

### Email Approval Template (Minimal Example)

```markdown
---
type: approval_request
action: email
created: 2026-01-11T16:00:00Z
expires: 2026-01-13T16:00:00Z
priority: normal
status: pending
---

## Action Summary
Send project update email to Client A

## Details
- **To:** clienta@example.com
- **Subject:** Project Update - Week 2
- **Attachments:** None

## Draft
[Email content here]

## To Approve: Move to Vault/Approved
## To Reject: Move to Vault/Rejected and add reason below

---
## Execution Log
[Filled after decision]
```

### Payment Approval Template (Critical)

```markdown
---
type: approval_request
action: payment
created: 2026-01-11T16:00:00Z
expires: 2026-01-12T16:00:00Z  # 24 hours for payments
priority: high
status: pending
---

## Action Summary
Pay invoice to [Vendor] for [Service]

## ⚠️ PAYMENT DETAILS - VERIFY CAREFULLY
- **Payee:** [Full Legal Name]
- **Amount:** $XXX.XX USD
- **Account:** [Verify this is correct account]
- **Reference:** Invoice #XXXX
- **Due Date:** [Date]

## Verification Checklist
- [ ] Payee name is correct
- [ ] Amount matches invoice
- [ ] Account number is correct
- [ ] We have not already paid this invoice

## To Approve: Move to Vault/Approved (double-check everything!)
## To Reject: Move to Vault/Rejected

---
## Execution Log
[Filled after decision]
```

### Social Post Approval Template

```markdown
---
type: approval_request
action: social
created: 2026-01-11T16:00:00Z
expires: 2026-01-14T16:00:00Z  # 72 hours for social posts
priority: normal
status: pending
---

## Action Summary
Publish LinkedIn post about [topic]

## Platform
LinkedIn (public post)

## Draft Content
[Full post content here]

## Hashtags
#Tag1 #Tag2 #Tag3

## Preview
[How it will appear on the platform]

## To Approve: Move to Vault/Approved
## To Reject: Move to Vault/Rejected

---
## Execution Log
[Filled after decision]
```

---

## Required Sections (Mandatory)

All approval requests MUST include:

1. **YAML Frontmatter**
   - type, action, created, expires, priority, status

2. **Action Summary**
   - One-line clear description

3. **Details**
   - At minimum: action type, target, reason

4. **Parameters**
   - All information needed to execute the action

5. **Instructions for Human**
   - How to approve (move to `Vault/Approved`)
   - How to reject (move to `Vault/Rejected` + add reason)

6. **Execution Log Section**
   - Empty placeholder (filled after decision)

---

## Optional Sections (Recommended)

Include when applicable:

- **Draft Content/Preview** - For emails, posts, etc.
- **Risks & Considerations** - For complex/risky actions
- **Business Alignment** - How this supports goals
- **Security Validation** - Pre-checks passed
- **Budget Impact** - For financial actions

---

## Best Practices

### Do:
- ✅ Use clear, specific action summaries
- ✅ Include all parameters needed for execution
- ✅ Show full draft/preview when applicable
- ✅ Set realistic expiration times
- ✅ Reference `Vault/Business_Goals.md` when relevant
- ✅ Make it easy for human to approve/reject

### Don't:
- ❌ Use vague descriptions like "Handle email"
- ❌ Skip required sections
- ❌ Set expiration < 4 hours (except urgent)
- ❌ Forget to include draft content
- ❌ Make humans search for details

---

## Expiration Guidelines

| Action Type | Standard Expiration | Urgent Expiration |
|-------------|---------------------|-------------------|
| Payment | 24 hours | 4 hours |
| Email | 48 hours | 6 hours |
| Social Post | 72 hours | 12 hours |
| File Operation | 48 hours | 8 hours |
| Calendar | 24 hours | 4 hours |

**After Expiration:**
- File automatically moves to `Vault/Rejected`
- Note added: "EXPIRED - No decision made within timeframe"
- No action is taken

---

## Example Workflow

1. **Skill creates approval request**
   - Uses this template
   - Fills in all sections
   - Saves to `Vault/Pending_Approval`

2. **Human reviews request**
   - Opens file in `Vault/Pending_Approval`
   - Reviews all details
   - Makes decision

3. **Human approves**
   - Moves file to `Vault/Approved` folder
   - AI detects the move
   - AI executes action
   - AI logs result to Execution Log section
   - AI moves file to `Vault/Done`

4. **OR Human rejects**
   - Moves file to `Vault/Rejected` folder
   - Adds rejection reason at bottom
   - AI detects the move
   - AI logs rejection
   - AI moves file to `Vault/Done`
   - No action taken

---

*This template ensures consistent, complete approval requests that humans can quickly review and decide on.*

*Last Updated: 2026-01-11*
*Version: 1.1 (Updated for Vault structure)*