# Bank Reconciliation Guide

**Purpose:** Step-by-step procedures for reconciling bank transactions with Xero

**Frequency:** Weekly (recommended) or before CEO briefing generation

**Last Updated:** 2026-01-11

---

## Overview

Bank reconciliation ensures your Xero records match your actual bank/credit card statements by:

1. **Matching transactions:** Link bank deposits to invoices, expenses to bills
2. **Identifying discrepancies:** Find missing, duplicate, or incorrect transactions
3. **Maintaining accuracy:** Ensure financial reports reflect reality
4. **Detecting fraud:** Catch unauthorized transactions early

**Success Metric:** 95%+ of transactions reconciled within 7 days

---

## Reconciliation Workflow

### Phase 1: Pre-Reconciliation Setup

**Before starting reconciliation:**

1. **Sync Xero Transactions**
   ```bash
   python .claude/skills/manage-accounting/scripts/xero_sync.py
   ```
   - Pulls latest bank transactions from Xero bank feeds
   - Updates `Vault/Accounting/Current_Month.md`
   - Creates transaction files in `Vault/Accounting/Transactions/`

2. **Verify Data Completeness**
   - Check last sync timestamp
   - Ensure no sync errors
   - Confirm date range covers period being reconciled

3. **Gather Supporting Documents**
   - Bank/credit card statements (PDF or online)
   - Receipts for expenses
   - Invoice records
   - Payment confirmations

---

### Phase 2: Transaction Matching

#### Money In (Revenue/Deposits)

**Objective:** Match bank deposits to invoices in Xero

1. **Identify Unreconciled Deposits**
   - Filter transactions: Type = "Deposit" or "Credit"
   - Status = "Unreconciled" in Xero
   - Date range: Current reconciliation period

2. **Match to Invoices**
   - **Exact Amount Match (easiest):**
     - Deposit amount = Invoice total → Direct match
     - Confidence: 100%
     - Action: Mark as reconciled in Xero

   - **Partial Payment:**
     - Deposit amount < Invoice total → Partial payment
     - Create payment record for partial amount
     - Update invoice status to "Partially Paid"
     - Note remaining balance

   - **Multiple Invoices in One Deposit:**
     - Deposit amount = Sum of multiple invoices
     - Match each invoice
     - Create payment record splitting deposit across invoices

   - **Unexplained Deposits:**
     - No matching invoice found
     - Flag for manual review
     - Possible causes:
       - Refund from vendor
       - Interest income
       - Miscellaneous revenue
       - Bank error

3. **Verification Checklist**
   - ✅ Amount matches exactly (or explained variance)
   - ✅ Date within reasonable range (payment delay normal)
   - ✅ Client/payer matches invoice
   - ✅ Reference number matches (if provided)

---

#### Money Out (Expenses/Payments)

**Objective:** Match bank withdrawals/charges to bills, expenses, or payments

1. **Identify Unreconciled Withdrawals**
   - Filter transactions: Type = "Withdrawal" or "Debit"
   - Status = "Unreconciled"

2. **Match to Category**

   **Scenario A: Bill Payment**
   - Match to bill in Xero
   - Verify amount, vendor, due date
   - Mark bill as "Paid"

   **Scenario B: Direct Expense (No Bill)**
   - Categorize expense (see expense-rules.md)
   - Create expense record in Xero
   - Attach receipt if available
   - Mark as reconciled

   **Scenario C: Transfer Between Accounts**
   - Identify as transfer (not expense)
   - Match with corresponding deposit in other account
   - Category: "Bank Transfer" (doesn't affect P&L)

   **Scenario D: Bank Fee/Charge**
   - Category: "Bank Fees" (404)
   - Usually small amounts ($0.50-$50)
   - Auto-categorize if matches pattern

3. **Special Cases**

   **Subscription Payments:**
   - Recurring monthly charges
   - Auto-categorize using vendor history
   - Track in subscription audit

   **Credit Card Payments:**
   - Match to credit card statement total
   - Individual charges already reconciled on card
   - Don't double-count expenses

   **ATM Withdrawals:**
   - Personal expense (not business)
   - Category: "Owner's Draw" or exclude from books
   - Flag if significant amount

---

### Phase 3: Discrepancy Resolution

**Common Discrepancies:**

#### 1. Amount Mismatch

**Problem:** Bank shows $1,050, invoice was $1,000

**Possible Causes:**
- Client included tip/bonus (+$50)
- Bank fees deducted ($1,000 - $50 fee = $950 net)
- Currency conversion variance
- Data entry error

**Resolution:**
1. Investigate: Check bank transaction details
2. If legitimate variance:
   - Create adjustment entry for difference
   - Categorize appropriately (Other Income, Bank Fees, etc.)
3. If error:
   - Correct original invoice/expense
   - Update Xero record

**Example:**
```markdown
**Transaction:** $1,050 deposit
**Invoice:** $1,000
**Variance:** +$50

Investigation: Client email confirms intentional tip
Resolution:
- Allocate $1,000 to Invoice #123
- Allocate $50 to "Other Revenue" (code 260)
- Mark both as reconciled
```

---

#### 2. Missing Transactions

**Problem:** Invoice marked "Paid" but no matching bank deposit

**Possible Causes:**
- Payment not yet cleared (in transit)
- Payment sent to wrong account
- Payment method different than expected (check vs wire)
- Data entry error (marked paid accidentally)

**Resolution:**
1. Check invoice status in Xero: When marked paid? By whom?
2. Contact client if payment overdue
3. Check all bank accounts (might be in different account)
4. If truly missing:
   - Un-mark invoice as paid
   - Update status to "Awaiting Payment"
   - Follow up with client

---

#### 3. Duplicate Transactions

**Problem:** Same expense appears twice in bank feed

**Possible Causes:**
- Manual entry + automatic sync
- Pending vs cleared showing twice
- Bank feed error

**Resolution:**
1. Identify true transaction (check bank statement)
2. Delete duplicate in Xero
3. Mark original as reconciled
4. Note in reconciliation report

---

#### 4. Timing Differences

**Problem:** Expense recorded in January, but clears bank in February

**Acceptable:** This is normal (accrual accounting)

**Resolution:**
- Expense remains in January (when incurred)
- Bank reconciliation shows as "cleared" in February
- No action needed if amounts match

**When to Investigate:**
- Delay > 30 days (payment might be lost)
- Large amounts
- Time-sensitive payments (taxes, payroll)

---

### Phase 4: Reconciliation Report

**Generate weekly reconciliation report:**

```markdown
# Bank Reconciliation Report
**Period:** {{start_date}} to {{end_date}}
**Generated:** {{timestamp}}
**Accounts:** {{account_names}}

## Summary

| Metric | Count | Amount |
|--------|-------|--------|
| Transactions Reviewed | {{total_count}} | ${{total_amount}} |
| Successfully Reconciled | {{reconciled_count}} | ${{reconciled_amount}} |
| Pending Review | {{pending_count}} | ${{pending_amount}} |
| Discrepancies Found | {{discrepancy_count}} | ${{discrepancy_amount}} |

**Reconciliation Rate:** {{reconciled_count/total_count*100}}%

## Revenue Reconciliation

| Invoice # | Amount | Bank Deposit | Date | Status |
|-----------|--------|--------------|------|--------|
| INV-2026-001 | $1,500 | $1,500 | 2026-01-05 | ✅ Matched |
| INV-2026-002 | $2,000 | $2,000 | 2026-01-08 | ✅ Matched |
| INV-2026-003 | $3,500 | Pending | - | ⏳ Awaiting payment |

**Total Invoiced:** ${{invoiced_total}}
**Total Received:** ${{received_total}}
**Outstanding:** ${{outstanding_total}}

## Expense Reconciliation

| Date | Vendor | Category | Amount | Status |
|------|--------|----------|--------|--------|
| 2026-01-03 | AWS | IT & Software | $150.00 | ✅ Matched |
| 2026-01-05 | Adobe | IT & Software | $54.99 | ✅ Matched |
| 2026-01-07 | Unknown | Pending Review | $200.00 | ⚠️ Review |

**Total Expenses:** ${{expense_total}}

## Discrepancies Requiring Attention

### High Priority

1. **Missing Deposit:** Invoice #INV-2026-004 ($5,000) marked paid on 2025-12-20, no matching deposit found
   - **Action:** Contact Client D to verify payment method
   - **Due:** 2026-01-15

2. **Amount Mismatch:** Expected $1,000 (Invoice #123), received $950
   - **Investigation:** $50 bank fee deducted
   - **Action:** Categorize $50 to Bank Fees
   - **Due:** 2026-01-12

### Low Priority

3. **Uncategorized Expense:** $25.00 transaction to "ABC Store"
   - **Action:** Manual categorization needed
   - **Due:** 2026-01-18

## Recommendations

- Follow up on missing $5,000 deposit (Client D)
- Categorize 3 pending transactions
- Review and approve bank fee allocation ($50)

## Next Reconciliation

**Scheduled:** {{next_date}}
**Scope:** Transactions from {{next_start}} to {{next_end}}
```

---

## Automation Rules

### Auto-Reconcile (High Confidence)

**Criteria for automatic reconciliation (no approval needed):**

1. **Exact Invoice Match:**
   - Amount matches exactly
   - Date within 30 days of invoice
   - Client/payer matches
   - **Action:** Auto-reconcile

2. **Known Recurring Expense:**
   - Vendor matches historical pattern
   - Amount within 5% of typical
   - Monthly subscription
   - **Action:** Auto-reconcile, categorize

3. **Bank Fees:**
   - Vendor = bank name
   - Category = Bank Fees
   - Amount < $50
   - **Action:** Auto-reconcile

### Require Human Review

**Scenarios that need manual approval:**

- ❌ Amount variance > 5%
- ❌ Unknown/new vendor
- ❌ Large amounts (>$1,000)
- ❌ Missing reference information
- ❌ Timing > 30 days from expected date
- ❌ Duplicate detection
- ❌ First-time client payment

---

## Integration with CEO Briefing

**Weekly reconciliation feeds into CEO briefing:**

1. **Cash Flow Status:**
   - Total deposits this week
   - Total expenses this week
   - Net cash flow

2. **Outstanding Items:**
   - Overdue invoices (>30 days)
   - Expected deposits not yet received
   - Large pending expenses

3. **Financial Health:**
   - Reconciliation rate (target: 95%+)
   - Discrepancy count (lower is better)
   - Average payment collection time

**Example CEO Briefing Excerpt:**
```markdown
## Financial Reconciliation

- **Reconciliation Rate:** 98% (145/148 transactions)
- **Outstanding Invoices:** $8,500 (3 invoices)
- **Cash Flow This Week:** +$4,200
- **Alert:** Client D payment ($5,000) overdue by 15 days
```

---

## Troubleshooting

### Bank Feed Not Syncing

**Problem:** Xero not pulling new transactions

**Solutions:**
1. Reconnect bank feed in Xero
2. Check bank API credentials
3. Verify bank account still active
4. Manual import bank statement (CSV)

### Can't Find Matching Invoice

**Problem:** Deposit received but no invoice in system

**Possible Causes:**
- Invoice not created in Xero
- Invoice under different client name
- Unexpected payment (not invoiced yet)

**Steps:**
1. Search Xero by amount
2. Search by client name (check variations)
3. Contact client for invoice reference
4. Create invoice retroactively if legitimate

### Reconciliation Balance Off

**Problem:** Xero balance ≠ Bank statement balance

**Common Causes:**
- Unreconciled transactions
- Duplicate entries
- Manual journal entries not accounted for
- Bank feed delay

**Resolution:**
1. Generate Xero reconciliation report
2. Compare to bank statement line by line
3. Identify missing/duplicate transactions
4. Correct and re-reconcile

---

## Best Practices

✅ **Reconcile weekly** (not monthly) - easier to catch errors early
✅ **Document everything** - add notes to unusual transactions
✅ **Keep receipts** - digital copies in Xero attachments
✅ **Review before CEO briefing** - ensure accurate financial data
✅ **Set calendar reminders** - make reconciliation routine
✅ **Use bank feeds** - automatic sync reduces manual entry errors
✅ **Separate personal & business** - avoid commingling transactions

❌ **Don't ignore small discrepancies** - they add up and hide errors
❌ **Don't batch too many periods** - harder to find specific transactions
❌ **Don't auto-reconcile everything** - maintain some manual review
❌ **Don't delete transactions** - correct with journal entries instead

---

## Metrics to Track

**Monthly Performance:**

| Metric | Target | Formula |
|--------|--------|---------|
| Reconciliation Rate | >95% | Reconciled / Total Transactions |
| Avg Time to Reconcile | <7 days | Days between transaction and reconciliation |
| Discrepancy Rate | <5% | Discrepancies / Total Transactions |
| Outstanding Invoices | <10% of monthly revenue | Unpaid Invoices / Monthly Revenue |

**Update these in:** `Vault/Accounting/Reconciliation_Metrics.md`

---

## Quick Reference - Matching Rules

| Bank Transaction | Matches To | Confidence | Action |
|------------------|------------|------------|--------|
| Deposit = Invoice amount | Invoice | 100% | Auto-reconcile |
| Withdrawal = Bill amount | Bill | 100% | Auto-reconcile |
| Monthly subscription (known) | Recurring expense | 95% | Auto-reconcile |
| Bank fee (<$50, known pattern) | Bank Fees category | 90% | Auto-reconcile |
| Deposit < Invoice amount | Partial payment | 85% | Create partial payment record |
| Unknown vendor | - | <70% | Manual review required |
| Large amount (>$1,000) new vendor | - | <70% | Manual review required |

---

*Last Updated: 2026-01-11 | Branch: feat/gold-accounting-xero*
*Frequency: Weekly | Target: 95%+ reconciliation rate | Auto-reconcile: High-confidence only*
