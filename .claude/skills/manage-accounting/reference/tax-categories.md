# Tax Categories Reference

**Purpose:** Tax treatment guide for expense categorization and invoice generation

**Important:** This is general guidance. **Always consult a qualified accountant** for tax advice specific to your jurisdiction.

**Last Updated:** 2026-01-11

---

## Tax Treatment by Expense Type

### Fully Deductible (100%)

Expenses that are fully deductible if used exclusively for business:

| Category | Xero Code | Examples | Documentation Required |
|----------|-----------|----------|------------------------|
| Advertising & Marketing | 400 | Google Ads, Facebook Ads, print ads | Invoices, campaign records |
| IT & Software | 433 | AWS, GitHub, Adobe (business use) | Subscription confirmations |
| Bank Fees | 404 | Transaction fees, payment processing | Bank statements |
| Office Expenses | 461 | Supplies, postage, printing | Receipts |
| Professional Services | 412 | Accountants, lawyers, consultants | Invoices, contracts |
| Rent | 473 | Office rent, co-working space | Lease agreement |
| Telephone & Internet | 489 | Business phone, internet | Bills (business portion only) |
| Travel - Business | 493/494 | Flights, hotels for business trips | Itinerary, business purpose |
| Insurance | 441 | Professional liability, business insurance | Policy documents |
| Legal Fees | 449 | Contract review, business legal | Invoices |

**Key Rule:** Must be "ordinary and necessary" for your business

---

### Partially Deductible (50%)

Expenses with limited deductibility:

| Category | Deduction | Why Limited | Best Practice |
|----------|-----------|-------------|---------------|
| Entertainment | 50% | Tax law limitation | Document business purpose, attendees |
| Meals (Non-Travel) | 50% | Tax law limitation | Keep detailed records |
| Client Gifts | 50% or $25 limit | Varies by jurisdiction | Track per recipient |

**Documentation Essential:**
- Who attended (names, business relationship)
- Business purpose discussed
- Date, location
- Total cost

**Example:**
- Client dinner: $200 → $100 deductible
- Categorize full $200 in Xero
- Tax software applies 50% limit at year-end

---

### Business Use Percentage

Expenses split between business and personal use:

#### Home Office

**Deduction Method 1: Simplified (if allowed in your jurisdiction)**
- Fixed rate per square foot
- Example: 200 sq ft × $5 = $1,000/year
- Easy to calculate, less documentation

**Deduction Method 2: Actual Expenses**
- Calculate business use percentage: Office sq ft / Total home sq ft
- Apply to: Rent/mortgage interest, utilities, insurance, repairs
- Example: 15% business use → 15% of expenses deductible

**Categories Affected:**
- Rent (473): Business portion
- Utilities (453): Business portion
- Internet (489): Business portion
- Insurance (441): Business portion

**Documentation:**
- Floor plan showing dedicated office space
- Total square footage calculations
- Exclusive business use (not guest bedroom/office combo)

#### Vehicle

**Deduction Method 1: Standard Mileage Rate**
- Rate per business mile (varies by year, ~$0.65/mile in 2026)
- Track: Date, miles, destination, business purpose
- Simpler, no receipt tracking needed

**Deduction Method 2: Actual Expenses**
- Track all vehicle costs: Gas, maintenance, insurance, depreciation
- Calculate business use %: Business miles / Total miles
- Apply business % to all expenses

**Cannot Mix:** Choose one method and stick with it for the vehicle's life

**Example:**
- Total miles: 20,000
- Business miles: 12,000
- Business use: 60%
- Gas cost: $3,000 → $1,800 deductible

**Documentation:**
- Mileage log (digital app recommended)
- Business purpose for each trip
- Start/end odometer readings

---

### Non-Deductible (0%)

Expenses that are NEVER tax-deductible:

| Type | Why Not Deductible | What to Do |
|------|---------------------|------------|
| Personal Expenses | Not business-related | Don't categorize as business |
| Fines & Penalties | Tax law prohibition | Separate category or exclude |
| Political Contributions | Tax law prohibition | Personal expense |
| Commuting (Home → Office) | Personal expense | Only business travel deductible |
| Personal Meals | Not business-related | Only client meals/travel meals |
| Personal Subscriptions | Netflix, Spotify (personal use) | Exclude or mark personal |
| Clothing | Unless uniform/costume | Not deductible |

**Red Flag Categories:**
- If categorized as business but personal, you risk audit penalties
- When in doubt, exclude or consult accountant

---

## Sales Tax / VAT / GST on Income

### Tax Types in Xero

| Tax Code | Name | Rate | Use When |
|----------|------|------|----------|
| OUTPUT2 | Standard GST/VAT on Sales | 10-20% | Standard taxable sales |
| EXEMPTOUTPUT | Tax Exempt | 0% | Exempt services (education, medical) |
| ZERORATEDOUTPUT | Zero-Rated | 0% | Exports, international clients |
| NONE | No Tax | 0% | Non-taxable items |

**Rate varies by jurisdiction:**
- USA: Sales tax (varies by state, 0-10%)
- Canada: GST (5%) + PST (varies by province)
- UK: VAT (20%)
- Australia: GST (10%)
- EU: VAT (varies by country, 15-27%)

### When to Charge Tax

**Charge Tax (OUTPUT2):**
- ✅ Client in same country/state
- ✅ Taxable services (consulting, software, design)
- ✅ Client is not tax-exempt

**Zero-Rated (ZERORATEDOUTPUT):**
- ✅ International client (outside your tax jurisdiction)
- ✅ Exports
- ✅ Services to overseas clients

**Exempt (EXEMPTOUTPUT):**
- ✅ Educational services (varies by jurisdiction)
- ✅ Medical services
- ✅ Non-profit clients (with documentation)

**No Tax (NONE):**
- ✅ Reimbursable expenses (already taxed)
- ✅ Out-of-scope items

**Example - US Consultant:**
- Client in same state → Charge state sales tax
- Client in different state → Check nexus rules (complex)
- Client in UK → No US tax (zero-rated)

**Example - UK Freelancer:**
- UK client → Charge 20% VAT
- EU client (B2B with VAT number) → Zero-rated (reverse charge)
- US client → Zero-rated (export of services)

---

## Tax Documentation Requirements

### Receipts & Records

**Receipt Threshold:**
- < $75: Receipt recommended but not always required
- ≥ $75: Receipt required by tax law
- Always keep receipts for: Travel, meals, entertainment, gifts

**Digital Receipts Acceptable:**
- Screenshot/photo is fine
- Attach to transaction in Xero
- Backup to cloud storage

**Retention Period:**
- USA: 3-7 years (IRS recommends 7)
- Canada: 6 years
- UK: 6 years
- Australia: 5 years

**What to Keep:**
- Invoices (sent and received)
- Receipts
- Bank statements
- Contracts
- Mileage logs
- Home office calculations

---

### Special Documentation

**Entertainment & Meals:**
Required on receipt or log:
- Amount
- Date
- Location
- Business purpose
- Attendees (names, business relationship)

**Travel:**
- Itinerary
- Business purpose
- Dates
- Accommodation receipts
- Transportation receipts
- Meal receipts (if claiming)

**Home Office:**
- Floor plan
- Square footage calculation
- Proof of exclusive business use
- Utility bills
- Rent/mortgage statements

**Vehicle:**
- Mileage log (every trip)
- Maintenance records
- Insurance proof
- Purchase/lease documentation

---

## Tax Categories by Scenario

### Scenario 1: Software as a Service (SaaS)

**Question:** Is Adobe Creative Cloud deductible?

**Answer:**
- **Business use:** 100% deductible (IT & Software, 433)
- **Mixed use:** Deduct business % only
- **Personal use:** 0% deductible

**Documentation:** Screenshot of business projects, client work using Adobe

---

### Scenario 2: Home Internet

**Question:** Can I deduct my home internet?

**Answer:**
- **Dedicated business line:** 100% deductible
- **Home office (exclusive use):** Business % deductible
- **No home office:** 0% deductible

**Example:**
- $100/month internet
- Home office = 20% of home
- Deductible: $20/month ($240/year)

---

### Scenario 3: Conference Attendance

**Question:** Can I deduct conference ticket + travel?

**Answer:**
- **Conference ticket:** 100% deductible (Professional Services, 412)
- **Travel (flight, hotel):** 100% deductible (Travel, 493)
- **Meals during travel:** 100% deductible (Travel, 493)
- **Networking dinner:** 50% deductible (Entertainment, 420)
- **Personal sightseeing:** 0% deductible

**Documentation:**
- Conference agenda showing business relevance
- Receipt for registration
- Travel itinerary
- Hotel bill
- Meal receipts with notes

---

### Scenario 4: Business Lunch

**Question:** Can I deduct a lunch with a client?

**Answer:**
- **With client (discussing business):** 50% deductible (Entertainment, 420)
- **Alone:** 0% deductible
- **While traveling:** 100% deductible (Travel, 493)

**Documentation:**
- Receipt showing total
- Note: Client name, business discussed
- Date, location

---

### Scenario 5: Office Equipment

**Question:** Can I deduct a $2,000 laptop?

**Answer:**
- **Business use:** Yes, deductible
- **Method 1:** Expense immediately (Section 179 if allowed)
- **Method 2:** Depreciate over 3-5 years

**Threshold (varies by jurisdiction):**
- <$2,500: Expense immediately
- ≥$2,500: Capitalize and depreciate

**Example:**
- $1,500 laptop → Expense in year of purchase (Computer Equipment, 610 or Office Expenses, 461)
- $3,000 laptop → Depreciate over 3 years ($1,000/year)

---

## Tax Planning Tips

### Maximize Deductions

✅ **Keep meticulous records:** The more documentation, the safer
✅ **Separate business & personal:** Different bank accounts, credit cards
✅ **Use business cards:** Easier to prove business use
✅ **Categorize promptly:** Don't wait until tax time
✅ **Track mileage religiously:** Often overlooked deduction
✅ **Don't forget small expenses:** They add up

### Avoid Red Flags

❌ **Don't deduct 100% vehicle:** Unless truly only for business
❌ **Don't round numbers:** Real expenses are $47.23, not $50
❌ **Don't over-claim home office:** Be honest about space %
❌ **Don't forget to categorize income:** All income taxable
❌ **Don't commingle funds:** Keep business and personal separate

### When to Consult Accountant

Mandatory consultation:
- First year in business
- Revenue >$100K
- Multiple income streams
- International clients
- Payroll/employees
- Major equipment purchases
- Audit notice

Recommended consultation:
- Quarterly tax planning
- Annual tax prep
- Major business changes

---

## Tax Reporting Integration

### Xero Tax Summary Report

At year-end, Xero can generate tax reports showing:

- Total revenue by tax type
- Total deductible expenses by category
- Tax collected (sales tax/VAT/GST)
- Tax paid on expenses

**Export to accountant:**
1. Run Tax Summary report in Xero
2. Export to Excel or PDF
3. Share with accountant
4. Accountant files tax return

---

## International Considerations

### If You Have International Clients

**Tax Treatment:**
- Usually zero-rated (no tax charged)
- Report as export of services
- Track separately for tax reporting

**Currency:**
- Invoice in client's currency or USD/EUR
- Xero tracks exchange rates
- Report in your home currency for taxes

**Documentation:**
- Client address (proves international)
- Service delivery location
- Payment records showing foreign source

---

## Common Mistakes

### Mistake 1: Mixing Personal & Business

**Wrong:**
- Using business card for personal Netflix
- Deducting personal meals as "client meetings"

**Right:**
- Separate cards
- Only deduct legitimate business expenses

### Mistake 2: Missing Documentation

**Wrong:**
- "I know I spent $5,000 on ads" (no receipts)
- Deducting without proof

**Right:**
- Keep every receipt
- Attach to Xero transactions
- Document business purpose

### Mistake 3: Incorrect Category

**Wrong:**
- Categorizing subscription fee as "Office Supplies"
- Mislabeling to inflate deductions

**Right:**
- Use correct category per xero-categories.md
- Ask accountant if uncertain

### Mistake 4: Forgetting Tax on Invoices

**Wrong:**
- Charging client $1,000, forgetting to add 10% GST
- You owe tax authority $100 out of pocket

**Right:**
- Always apply correct tax type
- Client pays $1,100 ($1,000 + $100 GST)
- You remit $100 to tax authority

---

## Quick Reference - Tax Deductibility

| Expense Type | Deductible % | Category | Conditions |
|--------------|--------------|----------|------------|
| Business software | 100% | IT & Software | Exclusively business use |
| Home office | Business % | Rent/Utilities | Dedicated space |
| Client dinner | 50% | Entertainment | Document attendees, purpose |
| Business travel meal | 100% | Travel | Away from home overnight |
| Office supplies | 100% | Office Expenses | Business use |
| Commuting | 0% | N/A | Personal expense |
| Netflix (personal) | 0% | N/A | Personal expense |
| Conference ticket | 100% | Professional Services | Business-related |
| Laptop (<$2,500) | 100% | Office/Equipment | Expense in year of purchase |
| Vehicle (60% business) | 60% | Motor Vehicle | Track mileage |

---

*Last Updated: 2026-01-11 | Branch: feat/gold-accounting-xero*
*Disclaimer: Not tax advice. Consult qualified accountant for your specific situation.*
