# Expense Categorization Rules

**Purpose:** Auto-categorization logic for transaction classification

**Target Accuracy:** 80%+ auto-categorization rate

**Last Updated:** 2026-01-11

---

## Rule Processing Order

Rules are processed in this priority order (first match wins):

1. **Exact Vendor Match** (confidence: 95-100%)
2. **Vendor Pattern Match** (confidence: 85-95%)
3. **Description Keyword Match** (confidence: 75-90%)
4. **Amount Pattern Match** (confidence: 70-85%)
5. **Historical Similarity** (confidence: 65-80%)
6. **Manual Review Required** (confidence: <65%)

---

## 1. Exact Vendor Match Rules

**Confidence:** 95-100% | **Action:** Auto-categorize directly in Xero

### Software & Technology (IT & Software - 433)

```python
EXACT_TECH_VENDORS = {
    # Cloud Infrastructure
    'AMAZON WEB SERVICES': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'AWS': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'MICROSOFT AZURE': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'GOOGLE CLOUD': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'DIGITALOCEAN': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'HEROKU': {'category': 'IT & Software', 'code': 433, 'confidence': 100},

    # Developer Tools
    'GITHUB': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'GITLAB': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'JETBRAINS': {'category': 'IT & Software', 'code': 433, 'confidence': 100},

    # Design & Creative
    'ADOBE': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'FIGMA': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'CANVA': {'category': 'IT & Software', 'code': 433, 'confidence': 100},

    # Productivity
    'MICROSOFT 365': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'GOOGLE WORKSPACE': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'SLACK': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'ZOOM': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'NOTION': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'AIRTABLE': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'ASANA': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'MONDAY.COM': {'category': 'IT & Software', 'code': 433, 'confidence': 95},

    # Communication
    'TWILIO': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'SENDGRID': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'MAILCHIMP': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
}
```

### Marketing & Advertising (400)

```python
EXACT_MARKETING_VENDORS = {
    'GOOGLE ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'FACEBOOK ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'META ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'LINKEDIN ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'TWITTER ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'X ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'HUBSPOT': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 95},
    'MAILCHIMP': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 95},
}
```

### Bank & Payment Fees (404)

```python
EXACT_BANK_FEE_VENDORS = {
    'STRIPE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'PAYPAL': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'SQUARE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'BRAINTREE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'WISE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'TRANSFERWISE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
}
```

### Professional Services (412)

```python
EXACT_PROFESSIONAL_VENDORS = {
    'UPWORK': {'category': 'Consulting & Accounting', 'code': 412, 'confidence': 95},
    'FIVERR': {'category': 'Consulting & Accounting', 'code': 412, 'confidence': 95},
    'QUICKBOOKS': {'category': 'Consulting & Accounting', 'code': 412, 'confidence': 100},
    'XERO': {'category': 'Consulting & Accounting', 'code': 412, 'confidence': 100},
}
```

### Office Supplies (461)

```python
EXACT_OFFICE_VENDORS = {
    'STAPLES': {'category': 'Office Expenses', 'code': 461, 'confidence': 100},
    'OFFICE DEPOT': {'category': 'Office Expenses', 'code': 461, 'confidence': 100},
    'OFFICEMAX': {'category': 'Office Expenses', 'code': 461, 'confidence': 100},
}
```

### Subscriptions (485) - For Audit Tracking

```python
EXACT_SUBSCRIPTION_VENDORS = {
    # Media (Personal or Business)
    'NETFLIX': {'category': 'Subscriptions', 'code': 485, 'confidence': 95, 'note': 'Review if business use'},
    'SPOTIFY': {'category': 'Subscriptions', 'code': 485, 'confidence': 95, 'note': 'Review if business use'},
    'YOUTUBE PREMIUM': {'category': 'Subscriptions', 'code': 485, 'confidence': 95, 'note': 'Review if business use'},
    'APPLE MUSIC': {'category': 'Subscriptions', 'code': 485, 'confidence': 95, 'note': 'Review if business use'},

    # Cloud Storage (if not primary business tool)
    'DROPBOX': {'category': 'Subscriptions', 'code': 485, 'confidence': 90},
    'GOOGLE ONE': {'category': 'Subscriptions', 'code': 485, 'confidence': 90},
    'ICLOUD': {'category': 'Subscriptions', 'code': 485, 'confidence': 90},
}
```

---

## 2. Vendor Pattern Match Rules

**Confidence:** 85-95% | **Action:** Auto-categorize if confidence >= 90%, else create approval

### Pattern Matching Logic

```python
import re

def match_vendor_pattern(vendor_name, description):
    """Match transaction against vendor patterns"""

    # Normalize: uppercase, remove extra spaces
    vendor = vendor_name.upper().strip()
    desc = description.upper().strip()

    # Cloud Infrastructure Patterns
    if re.search(r'AWS|AMAZON WEB SERVICES', vendor):
        return {'category': 'IT & Software', 'code': 433, 'confidence': 100}

    # Google Services (differentiate Ads vs Workspace)
    if 'GOOGLE' in vendor:
        if 'ADS' in desc or 'ADWORDS' in desc:
            return {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100}
        elif 'WORKSPACE' in desc or 'GSUITE' in desc:
            return {'category': 'IT & Software', 'code': 433, 'confidence': 100}
        elif 'CLOUD' in desc:
            return {'category': 'IT & Software', 'code': 433, 'confidence': 100}
        else:
            return {'category': 'IT & Software', 'code': 433, 'confidence': 85}

    # Amazon (differentiate AWS vs Business vs Retail)
    if 'AMAZON' in vendor:
        if 'AWS' in desc or 'WEB SERVICES' in desc:
            return {'category': 'IT & Software', 'code': 433, 'confidence': 100}
        elif 'BUSINESS' in desc:
            return {'category': 'Office Expenses', 'code': 461, 'confidence': 90}
        else:
            # Could be personal - require review
            return {'category': 'Office Expenses', 'code': 461, 'confidence': 70}

    # Payment Processors
    if re.search(r'STRIPE|PAYPAL|SQUARE|PAYMENT PROCESSOR', vendor):
        return {'category': 'Bank Fees', 'code': 404, 'confidence': 100}

    # Airlines (Travel)
    if re.search(r'AIRLINES|AIRWAYS|JETBLUE|SOUTHWEST|DELTA|UNITED|AMERICAN AIRLINES', vendor):
        return {'category': 'Travel - National', 'code': 493, 'confidence': 95}

    # Hotels (Travel)
    if re.search(r'HOTEL|MARRIOTT|HILTON|HYATT|HOLIDAY INN|AIRBNB', vendor):
        return {'category': 'Travel - National', 'code': 493, 'confidence': 95}

    # Car Rental (Travel)
    if re.search(r'HERTZ|AVIS|ENTERPRISE|CAR RENTAL', vendor):
        return {'category': 'Travel - National', 'code': 493, 'confidence': 95}

    # Rideshare
    if re.search(r'UBER|LYFT|RIDESHARE', vendor):
        return {'category': 'Travel - National', 'code': 493, 'confidence': 85}

    # Restaurants (Entertainment - check if client meeting)
    if re.search(r'RESTAURANT|CAFE|COFFEE|STARBUCKS|DUNKIN', vendor):
        # Needs context - was it a client meeting?
        return {'category': 'Entertainment', 'code': 420, 'confidence': 70}

    # Gas Stations (Motor Vehicle)
    if re.search(r'SHELL|EXXON|CHEVRON|BP|MOBIL|GAS STATION', vendor):
        return {'category': 'Motor Vehicle Expenses', 'code': 457, 'confidence': 90}

    # Utilities
    if re.search(r'ELECTRIC|POWER|GAS COMPANY|WATER|UTILITY', vendor):
        return {'category': 'Light, Power, Heating', 'code': 453, 'confidence': 95}

    # Internet/Phone
    if re.search(r'COMCAST|VERIZON|AT&T|T-MOBILE|SPRINT|INTERNET|BROADBAND', vendor):
        return {'category': 'Telephone & Internet', 'code': 489, 'confidence': 95}

    # Generic patterns not found
    return None
```

---

## 3. Description Keyword Match Rules

**Confidence:** 75-90% | **Action:** Create approval if <90%

### Keyword to Category Mapping

```python
DESCRIPTION_KEYWORDS = {
    'IT & Software': {
        'keywords': ['software', 'license', 'subscription', 'saas', 'cloud', 'hosting', 'domain', 'ssl'],
        'confidence': 85,
    },
    'Advertising & Marketing': {
        'keywords': ['ads', 'advertising', 'marketing', 'campaign', 'promotion', 'seo', 'ppc'],
        'confidence': 85,
    },
    'Office Expenses': {
        'keywords': ['office supplies', 'stationery', 'printer', 'paper', 'pens', 'folders'],
        'confidence': 85,
    },
    'Consulting & Accounting': {
        'keywords': ['consulting', 'consultant', 'advisory', 'professional services', 'accountant', 'lawyer', 'legal'],
        'confidence': 80,
    },
    'Travel - National': {
        'keywords': ['flight', 'hotel', 'accommodation', 'rental car', 'conference', 'business trip'],
        'confidence': 85,
    },
    'Entertainment': {
        'keywords': ['dinner', 'lunch', 'client meeting', 'networking', 'event'],
        'confidence': 75,  # Lower confidence - context matters
    },
}

def match_description_keywords(description):
    """Match description against keyword patterns"""
    desc = description.lower()

    for category, rule in DESCRIPTION_KEYWORDS.items():
        for keyword in rule['keywords']:
            if keyword in desc:
                return {
                    'category': category,
                    'confidence': rule['confidence'],
                    'matched_keyword': keyword
                }

    return None
```

---

## 4. Amount Pattern Match Rules

**Confidence:** 70-85% | **Action:** Use as supporting evidence, not primary rule

### Recurring Amount Detection

```python
def detect_recurring_amount(vendor, amount, transaction_history):
    """Detect if amount matches historical pattern for vendor"""

    # Get past transactions from same vendor
    past_transactions = [t for t in transaction_history if t['vendor'] == vendor]

    if len(past_transactions) < 2:
        return None

    # Check if amount matches recent transactions
    recent_amounts = [t['amount'] for t in past_transactions[-5:]]

    # If exact match in 80%+ of recent transactions
    match_count = sum(1 for a in recent_amounts if abs(a - amount) < 0.01)
    match_rate = match_count / len(recent_amounts)

    if match_rate >= 0.8:
        # Use category from most recent matching transaction
        matching_tx = next(t for t in reversed(past_transactions) if abs(t['amount'] - amount) < 0.01)
        return {
            'category': matching_tx['category'],
            'confidence': 75 + (match_rate * 10),  # 75-85%
            'reason': f'Recurring amount pattern ({match_rate*100:.0f}% match)'
        }

    return None
```

### Typical Amount Ranges by Category

```python
TYPICAL_RANGES = {
    'Subscriptions': {
        'min': 5.00,
        'max': 100.00,
        'monthly_pattern': True,
    },
    'IT & Software': {
        'min': 10.00,
        'max': 500.00,
        'monthly_pattern': True,
    },
    'Bank Fees': {
        'min': 0.50,
        'max': 50.00,
        'monthly_pattern': False,
    },
    'Office Expenses': {
        'min': 5.00,
        'max': 200.00,
        'monthly_pattern': False,
    },
}
```

---

## 5. Historical Similarity Matching

**Confidence:** 65-80% | **Action:** Use as last resort before manual review

### Fuzzy Vendor Matching

```python
from difflib import SequenceMatcher

def find_similar_vendor(new_vendor, transaction_history, threshold=0.8):
    """Find historically categorized vendors similar to new vendor"""

    best_match = None
    best_score = 0

    for tx in transaction_history:
        if 'category' not in tx:
            continue

        similarity = SequenceMatcher(None, new_vendor.upper(), tx['vendor'].upper()).ratio()

        if similarity > best_score and similarity >= threshold:
            best_score = similarity
            best_match = tx

    if best_match:
        return {
            'category': best_match['category'],
            'confidence': 65 + (best_score * 15),  # 65-80%
            'reason': f'Similar to "{best_match["vendor"]}" ({best_score*100:.0f}% match)'
        }

    return None
```

---

## 6. Special Case Rules

### Split Transactions

**Rule:** If description contains multiple purposes, flag for manual split

**Examples:**
- "Office supplies and software licenses" → Manual review
- "Conference registration + hotel" → Manual review

**Confidence:** 0% (requires human judgment)

### Reimbursements

**Rule:** If description contains "reimburse" or "reimbursement", flag specially

**Category:** Create asset (Accounts Receivable) or expense depending on direction

**Confidence:** 50% (requires verification)

### Refunds & Reversals

**Rule:** If amount is negative (credit), check for original transaction

**Action:**
1. Find original transaction
2. Reverse categorization
3. Add note linking transactions

**Confidence:** 90% if original found, 50% otherwise

### Foreign Currency

**Rule:** If currency != base currency, note exchange rate and date

**Action:**
1. Categorize normally
2. Add metadata: original_amount, original_currency, exchange_rate
3. Track for tax reporting

**Confidence:** Same as underlying rule

---

## Confidence Threshold Actions

| Confidence Range | Action | Requires Approval |
|------------------|--------|-------------------|
| 90-100% | Auto-categorize in Xero directly | No |
| 75-89% | Create approval request | Yes |
| 65-74% | Flag for manual review | Yes |
| <65% | Require human categorization | Yes |

---

## Rule Customization

### Adding New Vendor Rules

To add a new vendor pattern:

1. Add to appropriate dictionary (EXACT_*_VENDORS)
2. Set confidence based on ambiguity:
   - 100%: Absolutely certain (e.g., "GOOGLE ADS" → Advertising)
   - 95%: Very confident, minimal ambiguity
   - 90%: Confident, some edge cases
   - 85%: Mostly confident, needs occasional review
   - <85%: Requires approval

3. Test with historical data
4. Update this file

### Learning from Corrections

When a human corrects an auto-categorization:

1. Log the correction in categorization_corrections.json
2. If same vendor/description occurs 3+ times with human override:
   - Update rule confidence
   - Or add new rule
3. Monthly review of corrections to improve rules

---

## Testing & Validation

### Test Cases (Target: 80%+ Pass Rate)

Run categorization against historical transactions and validate:

```bash
python .claude/skills/manage-accounting/scripts/categorize_expense.py --test --report
```

**Success Metrics:**
- ✅ 80%+ transactions auto-categorized (confidence >= 90%)
- ✅ 95%+ accuracy on high-confidence categorizations
- ✅ <5% miscategorizations requiring correction
- ✅ <10% flagged for manual review

---

## Error Handling

**Uncategorizable Transactions:**
- Create file in `Vault/Accounting/Needs_Review/`
- Include:
  - Transaction details
  - Why it couldn't be categorized
  - 2-3 suggested categories with reasoning
  - Similar past transactions for reference

**Conflicting Rules:**
- If multiple rules match with similar confidence, flag for review
- Log conflict for rule refinement

**Missing Information:**
- If vendor or description missing, require manual input
- Cannot auto-categorize without vendor name

---

## Performance Monitoring

Track these metrics monthly:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Auto-categorization rate | >80% | [TBD] | 🟡 Pending |
| High-confidence accuracy | >95% | [TBD] | 🟡 Pending |
| Approval request rate | <15% | [TBD] | 🟡 Pending |
| Manual review rate | <10% | [TBD] | 🟡 Pending |
| Miscategorization rate | <5% | [TBD] | 🟡 Pending |

---

*Last Updated: 2026-01-11 | Branch: feat/gold-accounting-xero*
*Target Accuracy: 80%+ | Current Accuracy: [Test after implementation]*
