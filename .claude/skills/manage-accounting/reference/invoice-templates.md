# Invoice Templates Reference

**Purpose:** Standard invoice templates and generation guidelines

**Last Updated:** 2026-01-11

---

## Template Selection Logic

Choose template based on service type and client relationship:

| Template | Use When | Typical Amount | Payment Terms |
|----------|----------|----------------|---------------|
| **Hourly** | Time-based work, consulting | $500-$5,000 | Net 15 |
| **Project-Based** | Fixed-price deliverables | $1,000-$10,000 | Net 30 (milestones) |
| **Retainer** | Ongoing monthly services | $2,000-$15,000 | Net 7 (recurring) |
| **Recurring** | Subscriptions, maintenance | $100-$2,000 | Net 7 (monthly) |
| **Milestone** | Large projects with phases | $5,000-$50,000 | Per milestone |

---

## Template 1: Hourly Rate Invoice

**Best For:** Consulting, freelance work, variable-hour projects

### Xero API Structure

```json
{
  "Type": "ACCREC",
  "Contact": {
    "ContactID": "{{contact_id}}"
  },
  "Date": "{{invoice_date}}",
  "DueDate": "{{due_date}}",
  "LineAmountTypes": "Exclusive",
  "LineItems": [
    {
      "Description": "{{service_description}}",
      "Quantity": {{hours}},
      "UnitAmount": {{hourly_rate}},
      "AccountCode": "200",
      "TaxType": "OUTPUT2"
    }
  ],
  "Reference": "INV-{{year}}-{{number}}",
  "Status": "DRAFT"
}
```

### Example - Consulting Services

```markdown
**Line Items:**
- Business Strategy Consulting (40 hours @ $150/hr) = $6,000
- Technical Architecture Review (8 hours @ $150/hr) = $1,200

**Subtotal:** $7,200
**Tax (if applicable):** $720
**Total:** $7,920

**Payment Terms:** Net 15 days
**Due Date:** 2026-01-26
```

### Approval Request Format

When creating approval for hourly invoice:

```markdown
---
type: approval_request
action: create_invoice
template: hourly
created: 2026-01-11T10:30:00Z
expires: 2026-01-12T10:30:00Z
status: pending
---

## Invoice Details

**Client:** {{client_name}}
**Template:** Hourly Rate
**Invoice Date:** {{invoice_date}}
**Due Date:** {{due_date}} (Net 15)

## Line Items

| Description | Hours | Rate | Amount |
|-------------|-------|------|--------|
| {{service_1}} | {{hours_1}} | ${{rate}} | ${{amount_1}} |
| {{service_2}} | {{hours_2}} | ${{rate}} | ${{amount_2}} |

**Subtotal:** ${{subtotal}}
**Tax ({{tax_rate}}%):** ${{tax_amount}}
**Total:** ${{total}}

## Client Information

- Name: {{client_name}}
- Email: {{client_email}}
- Company: {{client_company}}
- Contact ID (Xero): {{contact_id}}

## To Approve

Move this file to `/Vault/Approved/` to create invoice in Xero.

## To Reject

Move this file to `/Vault/Rejected/` and add rejection reason.
```

---

## Template 2: Project-Based (Fixed Price)

**Best For:** Website builds, defined deliverables, fixed-scope projects

### Xero API Structure

```json
{
  "Type": "ACCREC",
  "Contact": {
    "ContactID": "{{contact_id}}"
  },
  "Date": "{{invoice_date}}",
  "DueDate": "{{due_date}}",
  "LineAmountTypes": "Exclusive",
  "LineItems": [
    {
      "Description": "{{project_name}} - {{deliverable_description}}",
      "Quantity": 1,
      "UnitAmount": {{project_amount}},
      "AccountCode": "200",
      "TaxType": "OUTPUT2"
    }
  ],
  "Reference": "INV-{{year}}-{{number}}",
  "Status": "DRAFT"
}
```

### Example - Website Development

```markdown
**Project:** E-commerce Website Development
**Deliverables:**
- Custom WordPress theme
- WooCommerce integration
- Payment gateway setup
- 5 pages content migration
- 2 rounds of revisions

**Fixed Price:** $8,500
**Tax (if applicable):** $850
**Total:** $9,350

**Payment Terms:** 50% upfront ($4,675), 50% on completion
**Due Date:** Upon completion (2026-02-15)
```

---

## Template 3: Milestone-Based

**Best For:** Large projects, phased deliverables, risk mitigation

### Milestone Structure

```markdown
**Project:** {{project_name}}
**Total Value:** ${{total_project_value}}

**Milestones:**
1. Project Kickoff & Discovery (20%) - ${{milestone_1_amount}} - Due: {{date_1}}
2. Design & Wireframes (25%) - ${{milestone_2_amount}} - Due: {{date_2}}
3. Development Phase 1 (30%) - ${{milestone_3_amount}} - Due: {{date_3}}
4. Development Phase 2 (15%) - ${{milestone_4_amount}} - Due: {{date_4}}
5. Final Delivery & Handoff (10%) - ${{milestone_5_amount}} - Due: {{date_5}}

**Current Invoice:** Milestone {{milestone_number}} - {{milestone_name}}
**Amount:** ${{milestone_amount}}
**Payment Terms:** Net 7 days
```

### Xero Line Item for Milestone

```json
{
  "Description": "{{project_name}} - Milestone {{number}}: {{milestone_name}}",
  "Quantity": 1,
  "UnitAmount": {{milestone_amount}},
  "AccountCode": "200",
  "TaxType": "OUTPUT2"
}
```

---

## Template 4: Recurring/Retainer

**Best For:** Monthly retainers, subscription services, ongoing support

### Xero Repeating Invoice Setup

```json
{
  "Type": "ACCREC",
  "Contact": {
    "ContactID": "{{contact_id}}"
  },
  "Schedule": {
    "Period": 1,
    "Unit": "MONTHLY",
    "DueDate": 7,
    "DueDateType": "OFFOLLOWINGMONTH",
    "StartDate": "{{start_date}}",
    "NextScheduledDate": "{{next_date}}"
  },
  "LineItems": [
    {
      "Description": "{{retainer_service}} - {{month}} {{year}}",
      "Quantity": 1,
      "UnitAmount": {{monthly_retainer}},
      "AccountCode": "200",
      "TaxType": "OUTPUT2"
    }
  ],
  "Reference": "RETAINER-{{client_code}}-{{year}}-{{month}}"
}
```

### Example - Monthly Retainer

```markdown
**Service:** Digital Marketing Retainer
**Included:**
- Social media management (LinkedIn, Twitter, Facebook)
- 4 blog posts per month
- Monthly analytics report
- Email marketing (1 campaign/month)

**Monthly Fee:** $3,500
**Billing Cycle:** 1st of each month
**Payment Terms:** Net 7 days
**Contract Period:** 12 months (renewal option)
```

---

## Template 5: Expense Reimbursement

**Best For:** Client-approved expenses, travel reimbursement

### Xero Line Items

```json
{
  "LineItems": [
    {
      "Description": "Professional Services - {{description}}",
      "Quantity": {{hours}},
      "UnitAmount": {{rate}},
      "AccountCode": "200",
      "TaxType": "OUTPUT2"
    },
    {
      "Description": "Reimbursable Expenses: {{expense_description}}",
      "Quantity": 1,
      "UnitAmount": {{expense_total}},
      "AccountCode": "200",
      "TaxType": "NONE"
    }
  ]
}
```

### Example

```markdown
**Services:**
- Consulting (20 hours @ $150/hr) = $3,000

**Reimbursable Expenses:**
- Travel: Flight to client site = $450
- Accommodation: Hotel (2 nights) = $350
- Meals during trip = $100

**Services Subtotal:** $3,000
**Expenses Subtotal:** $900
**Tax on Services:** $300
**Total Due:** $4,200
```

---

## Required Fields Validation

Before creating invoice, ensure these fields are present:

### Critical (Must Have)
- ✅ Client/Contact ID (Xero)
- ✅ Invoice Date
- ✅ Due Date
- ✅ Line Item Description
- ✅ Amount (Quantity × Unit Price)
- ✅ Account Code (usually 200 for Sales)
- ✅ Tax Type

### Recommended (Should Have)
- ✅ Reference Number (INV-YYYY-###)
- ✅ Payment Terms (Net 7/15/30)
- ✅ Client PO Number (if required by client)
- ✅ Project Reference
- ✅ Contact Email

### Optional (Nice to Have)
- URL to project/deliverables
- Notes/Payment Instructions
- Branding Theme ID (Xero)

---

## Invoice Numbering System

**Format:** `INV-[YEAR]-[SEQUENCE]`

**Examples:**
- INV-2026-001
- INV-2026-002
- INV-2026-137

**Sequence Reset:** Annually (January 1st → 001)

**Special Prefixes:**
- `RETAINER-[CLIENT]-[YEAR]-[MONTH]` - Recurring retainers
- `MILESTONE-[PROJECT]-[NUMBER]` - Milestone invoices
- `CREDIT-[YEAR]-[SEQUENCE]` - Credit notes

---

## Payment Terms Reference

| Term | Due Date | Use Case |
|------|----------|----------|
| Due on Receipt | Immediate | Small amounts (<$500), upfront payments |
| Net 7 | 7 days from invoice date | Retainers, recurring services |
| Net 15 | 15 days from invoice date | Standard consulting, hourly work |
| Net 30 | 30 days from invoice date | Enterprise clients, larger projects |
| Net 45/60 | 45-60 days | Government, large corporations |
| 50/50 Split | 50% upfront, 50% completion | Project-based work |
| Milestone | Per milestone schedule | Large multi-phase projects |

**Default Recommendation:** Net 15 for most consulting/services

---

## Tax Handling

### Tax Types in Xero

| Tax Code | Description | Rate | When to Use |
|----------|-------------|------|-------------|
| OUTPUT2 | GST/VAT on Income | 10-20% | Standard sales (varies by country) |
| NONE | No Tax | 0% | Expense reimbursements, zero-rated sales |
| EXEMPTOUTPUT | Tax Exempt | 0% | Exempt services (education, medical, etc.) |
| ZERORATEDOUTPUT | Zero-Rated | 0% | Exports, international services |

**Check with accountant for your jurisdiction's specific rules.**

### Common Scenarios

1. **Standard Service (Taxable):** Use OUTPUT2
2. **International Client (Outside tax jurisdiction):** Use ZERORATEDOUTPUT
3. **Reimbursable Expenses:** Use NONE (expenses already taxed)
4. **Tax-Exempt Organization:** Use EXEMPTOUTPUT (requires documentation)

---

## Approval Workflow

### Step 1: Generate Invoice Request

When user requests "create invoice for Client A, $1,500":

1. Look up client in Xero (get Contact ID)
2. Determine template (ask if unclear: hourly, project, retainer?)
3. Populate template with details
4. Calculate tax
5. Generate preview

### Step 2: Create Approval File

Save in `Vault/Pending_Approval/APPROVAL_INVOICE_[Client]_[Amount]_[Date].md`

Include:
- Full invoice details
- Line items breakdown
- Tax calculation
- Client information
- Preview of what will be created in Xero

### Step 3: Wait for Human Approval

Human reviews and either:
- Approves: Moves to `Vault/Approved/`
- Rejects: Moves to `Vault/Rejected/` with reason
- Modifies: Edits amounts/details, then moves to `Vault/Approved/`

### Step 4: Execute Approved Invoice

`handle-approval` skill:
1. Validates approval file
2. Calls Xero MCP to create invoice (status: DRAFT)
3. Captures invoice number and URL
4. Optionally sends invoice via email (separate approval)
5. Logs to Dashboard and accounting records

---

## Invoice Sending Options

**Option 1: Draft in Xero (Manual Send)**
- Create as DRAFT
- Human reviews in Xero web interface
- Human clicks "Approve & Send" in Xero
- ✅ Safest option

**Option 2: Auto-Approve in Xero**
- Create as AUTHORISED (approved)
- Still requires human to send via Xero
- Invoice is final but not sent

**Option 3: Full Automation (Requires Second Approval)**
- Create as AUTHORISED
- Send via Xero API or Email MCP
- **Requires TWO approvals:**
  1. Approve invoice creation
  2. Approve invoice sending

**Recommendation:** Use Option 1 (Draft) for Gold Tier

---

## Common Mistakes to Avoid

❌ **Wrong Tax Type:** Using OUTPUT2 for international clients (should be ZERORATEDOUTPUT)
❌ **Missing Contact ID:** Invoice fails if client doesn't exist in Xero
❌ **Duplicate Invoice Numbers:** Xero rejects duplicates
❌ **Incorrect Payment Terms:** Net 30 when client agreement says Net 15
❌ **Missing Line Item Descriptions:** Vague descriptions cause payment delays
❌ **Not Checking for Existing Invoices:** Re-invoicing same work

✅ **Validate client exists before creating**
✅ **Match payment terms to client agreement**
✅ **Use clear, specific line item descriptions**
✅ **Check for duplicate/similar recent invoices**
✅ **Include reference to project or work completed**
✅ **Verify tax treatment for client's jurisdiction**

---

## Integration with Business_Goals.md

Before creating invoice, check `Vault/Business_Goals.md` for:

1. **Standard Rates:**
   - Hourly consulting rate
   - Project minimums
   - Retainer pricing

2. **Client-Specific Terms:**
   - Special rates for specific clients
   - Preferred payment terms
   - Discount agreements

3. **Invoice Policies:**
   - When to charge deposits
   - Late payment fees
   - Early payment discounts

**Example Business_Goals.md excerpt:**
```markdown
## Pricing & Rates

- **Standard Hourly:** $150/hr
- **Enterprise Hourly:** $200/hr
- **Retainer Discount:** 10% off hourly rate
- **Project Minimum:** $1,000

## Client-Specific Rates

- **Client A:** $125/hr (long-term partner)
- **Client B:** Net 45 terms (enterprise agreement)
```

---

## Testing Invoice Generation

Before going live, test with Xero Demo Company:

```bash
# Test invoice creation (dry run)
python .claude/skills/manage-accounting/scripts/generate_invoice.py \
  --client "Test Client" \
  --amount 1000 \
  --dry-run

# Create in Xero Demo Company
python .claude/skills/manage-accounting/scripts/generate_invoice.py \
  --client "Test Client" \
  --amount 1000 \
  --demo-mode
```

**Test Cases:**
- ✅ Hourly invoice with multiple line items
- ✅ Fixed-price project invoice
- ✅ Invoice with expense reimbursements
- ✅ International client (zero-rated tax)
- ✅ Recurring retainer setup

---

## Troubleshooting

**"Contact not found" error:**
- Verify client exists in Xero
- Check spelling of client name
- Create contact in Xero first, then retry

**"Duplicate invoice number" error:**
- Check last invoice number in Xero
- Increment sequence number
- Verify numbering system sync

**Tax calculation incorrect:**
- Verify tax type for client's jurisdiction
- Check if client is tax-exempt
- Confirm tax rate in Xero settings

**Invoice not appearing in Xero:**
- Check API connection
- Verify authentication token not expired
- Review Xero API logs
- Ensure status is DRAFT or AUTHORISED (not invalid status)

---

*Last Updated: 2026-01-11 | Branch: feat/gold-accounting-xero*
*Templates: 5 | Default: Hourly (Net 15) | Always Require Approval*
