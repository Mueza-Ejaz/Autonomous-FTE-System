# Xero Categories Reference

**Purpose:** Standard chart of accounts for transaction categorization

**Last Updated:** 2026-01-11

---

## Revenue Categories

| Category | Xero Code | Description | Examples |
|----------|-----------|-------------|----------|
| **Sales** | 200 | Primary business revenue | Consulting fees, product sales, service revenue |
| **Other Revenue** | 260 | Secondary income | Interest income, referral fees, affiliate commissions |
| **Grants & Subsidies** | 270 | Government or institutional funding | Research grants, business subsidies |

---

## Expense Categories

### Operating Expenses

| Category | Xero Code | Description | Common Vendors | Tax Deductible |
|----------|-----------|-------------|----------------|----------------|
| **Advertising & Marketing** | 400 | Promotional activities | Google Ads, Facebook Ads, LinkedIn Ads | Yes |
| **Bank Fees** | 404 | Transaction fees, account fees | Bank charges, PayPal fees, Stripe fees | Yes |
| **Cleaning** | 408 | Office cleaning services | Cleaning contractors | Yes |
| **Consulting & Accounting** | 412 | Professional services | Accountants, lawyers, business consultants | Yes |
| **Depreciation** | 416 | Asset value reduction | N/A (calculated) | Yes |
| **Entertainment** | 420 | Client entertainment | Restaurants (50% deductible in most regions) | Partial (50%) |
| **General Expenses** | 429 | Miscellaneous | Uncategorized small expenses | Yes |
| **IT & Software** | 433 | Technology expenses | Software subscriptions, cloud services | Yes |
| **Insurance** | 441 | Business insurance | Liability, professional indemnity | Yes |
| **Interest Expense** | 445 | Loan interest | Business loan interest, credit card interest | Yes |
| **Legal Expenses** | 449 | Legal services | Lawyers, legal filings, contract review | Yes |
| **Light, Power, Heating** | 453 | Utilities | Electricity, gas, water | Yes |
| **Motor Vehicle Expenses** | 457 | Vehicle costs | Fuel, maintenance, parking | Yes |
| **Office Expenses** | 461 | Office supplies | Stationery, printing, postage | Yes |
| **Postage & Courier** | 465 | Shipping costs | Postal services, couriers | Yes |
| **Printing & Stationery** | 469 | Print materials | Business cards, letterhead | Yes |
| **Rent** | 473 | Office rent | Co-working space, office lease | Yes |
| **Repairs & Maintenance** | 477 | Equipment repairs | Computer repairs, office maintenance | Yes |
| **Subscriptions** | 485 | Recurring services | Netflix, Spotify, Adobe, GitHub, AWS | Depends (business vs personal) |
| **Telephone & Internet** | 489 | Communication costs | Phone bills, internet, mobile | Yes |
| **Travel - National** | 493 | Domestic travel | Domestic flights, hotels, rental cars | Yes |
| **Travel - International** | 494 | International travel | International flights, foreign hotels | Yes |
| **Wages & Salaries** | 477 | Employee compensation | Salaries, contractor payments | Yes |

---

## Asset Categories

| Category | Xero Code | Description | Examples |
|----------|-----------|-------------|----------|
| **Computer Equipment** | 610 | Computing hardware | Laptops, desktops, monitors, peripherals |
| **Office Equipment** | 620 | Office furniture & equipment | Desks, chairs, printers |
| **Intangible Assets** | 630 | Non-physical assets | Software licenses (>1 year), domain names |

---

## Categorization Rules

### When to Use "IT & Software" vs "Subscriptions"

**IT & Software (433):**
- Mission-critical business software
- Development tools (IDEs, GitHub, GitLab)
- Cloud infrastructure (AWS, Azure, Google Cloud)
- Productivity tools (Microsoft 365, Google Workspace)
- Security software

**Subscriptions (485):**
- Non-essential SaaS
- Media/streaming (if personal use)
- Marketing tools (if small/recurring)
- Use this for subscription audit tracking

**Rule of thumb:** If it's essential for business operations, use IT & Software. If it's recurring and potentially cuttable, use Subscriptions.

---

### When to Use "Consulting & Accounting" vs "Wages & Salaries"

**Consulting & Accounting (412):**
- Independent contractors (1099/freelance)
- One-time professional services
- Accountants, lawyers, business consultants
- Advisory services

**Wages & Salaries (477):**
- W-2 employees
- Regular payroll
- Benefits and payroll taxes

**Rule of thumb:** If they get a W-2, it's Wages. If they get a 1099, it's Consulting.

---

### When to Use "Travel - National" vs "Motor Vehicle Expenses"

**Travel - National/International (493/494):**
- Flights, trains, long-distance buses
- Hotels, accommodation
- Rental cars (during travel)
- Meals during business travel

**Motor Vehicle Expenses (457):**
- Daily commute fuel
- Vehicle maintenance/repairs
- Parking (local)
- Vehicle insurance

**Rule of thumb:** Travel is for trips away from home base. Motor Vehicle is for local driving.

---

### When to Use "Entertainment" vs "Meals & Travel"

**Entertainment (420):**
- Client dinners/lunches
- Networking events with food
- Event tickets with clients
- **Tax Note:** Often 50% deductible

**Travel - National/International:**
- Meals while traveling for business
- **Tax Note:** Usually 100% deductible if traveling

**Rule of thumb:** Entertainment is local client relationship building. Travel meals are part of business trips.

---

## Tax Treatment Guide

### Fully Deductible (100%)

- Advertising & Marketing
- IT & Software (business use)
- Office Expenses
- Rent
- Telephone & Internet (business portion)
- Professional Services (Consulting, Legal, Accounting)
- Bank Fees
- Travel (business purpose)

### Partially Deductible (50%)

- Entertainment (client dinners, networking events)
- Meals (not during travel)

### Non-Deductible (0%)

- Personal subscriptions (Netflix, Spotify, etc.)
- Fines and penalties
- Personal meals
- Commuting costs (home to office)
- Charitable donations (may be separately deductible)

### Special Rules

**Home Office:**
- Deductible if dedicated workspace
- Percentage based on square footage or hours used
- Categories: Rent, Utilities, Internet

**Vehicle:**
- Mileage method vs actual expense method
- Keep mileage log for deductible trips

**Software:**
- <$2,500: Expense immediately
- >$2,500: Capitalize and depreciate over 3 years

---

## Confidence Scoring for Auto-Categorization

When auto-categorizing, use this confidence framework:

### High Confidence (90-100%) - Auto-categorize directly

- Exact vendor match in expense-rules.md
- Recurring transaction with consistent category history
- Clear category indicators in description

**Examples:**
- "GOOGLE ADS" → Advertising & Marketing (100%)
- "AWS Services" → IT & Software (95%)
- "Adobe Creative Cloud" → IT & Software (95%)

### Medium Confidence (70-89%) - Create approval request

- Vendor match but description ambiguous
- New vendor in known category
- Amount unusual for typical category

**Examples:**
- "Amazon.com" → Could be Office Expenses or Personal (75%)
- New software subscription (first occurrence) → IT & Software (80%)

### Low Confidence (<70%) - Flag for manual review

- Unknown vendor
- Description too generic
- Amount very large or very small
- Category unclear

**Examples:**
- "Payment to John Doe" → Unknown (40%)
- "Misc charge" → Unknown (30%)

---

## Category Hierarchy

```
Revenue
├── Sales
├── Other Revenue
└── Grants & Subsidies

Expenses
├── Operating Expenses
│   ├── Marketing & Sales (400-410)
│   ├── Office & Admin (429-489)
│   ├── Technology (433)
│   ├── Professional Services (412, 449)
│   └── People (477)
├── Cost of Goods Sold (COGS)
│   └── [Not applicable for service business]
└── Depreciation & Amortization

Assets
├── Current Assets
│   └── Accounts Receivable
└── Fixed Assets
    ├── Computer Equipment
    ├── Office Equipment
    └── Intangible Assets
```

---

## Subscription Audit Tracking

For cost optimization, track all recurring subscriptions here:

| Vendor | Category | Monthly Cost | Annual Cost | Business Use | Review Frequency |
|--------|----------|--------------|-------------|--------------|------------------|
| Adobe Creative Cloud | IT & Software | $54.99 | $659.88 | High | Quarterly |
| GitHub Pro | IT & Software | $7.00 | $84.00 | High | Annually |
| AWS | IT & Software | Varies | ~$600 | High | Monthly |
| Notion | Subscriptions | $15.00 | $180.00 | Medium | Monthly |
| Netflix | Subscriptions | $15.99 | $191.88 | Low (Personal) | Monthly |

**Flag for review if:**
- No usage detected in 30+ days
- Duplicate functionality with another tool
- Cost increased >20% without notification
- Business use drops from High to Medium/Low

---

## Custom Categories

If your business needs custom categories, add them here:

| Custom Category | Xero Code | Description | When to Use |
|----------------|-----------|-------------|-------------|
| *None yet* | - | - | - |

**To add custom category:**
1. Create in Xero web interface
2. Add to this table
3. Update expense-rules.md with matching patterns

---

## Quick Reference - Common Vendors

| Vendor Pattern | Category | Code |
|----------------|----------|------|
| Google (Ads, Workspace) | Marketing or IT & Software | 400 or 433 |
| Amazon (Business) | Office Expenses | 461 |
| Amazon (AWS) | IT & Software | 433 |
| Adobe | IT & Software | 433 |
| Microsoft 365 | IT & Software | 433 |
| Stripe | Bank Fees | 404 |
| PayPal | Bank Fees | 404 |
| Zoom | IT & Software | 433 |
| Slack | IT & Software | 433 |
| Dropbox | IT & Software | 433 |
| Netflix/Spotify | Subscriptions | 485 |
| Uber/Lyft (business) | Travel - National | 493 |
| Starbucks (client meeting) | Entertainment | 420 |
| Hotel chains | Travel - National/International | 493/494 |
| Airlines | Travel - National/International | 493/494 |

---

## Error Prevention

**Common mistakes to avoid:**

❌ Categorizing personal expenses as business
❌ Using "General Expenses" too often (should be <5% of transactions)
❌ Mixing capital purchases with operating expenses
❌ Incorrect tax treatment (e.g., claiming 100% on entertainment)
❌ Not splitting home office/personal use

✅ Use specific categories whenever possible
✅ Document business purpose for borderline expenses
✅ Keep receipts for expenses >$75
✅ Separate personal and business transactions
✅ Review and update categories monthly

---

*Last Updated: 2026-01-11 | Branch: feat/gold-accounting-xero*
