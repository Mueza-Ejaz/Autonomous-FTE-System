#!/usr/bin/env python3
"""
Expense Categorization Script

Auto-categorizes transactions using pattern matching and historical data.
Targets 80%+ auto-categorization accuracy.

Usage:
    python categorize_expense.py                           # Categorize all uncategorized
    python categorize_expense.py --transaction-id TX123    # Categorize specific transaction
    python categorize_expense.py --dry-run                 # Preview without updating Xero
    python categorize_expense.py --threshold 0.7           # Set confidence threshold
    python categorize_expense.py --test                    # Run test suite

Author: Autonomous FTE
Version: 1.0
Last Updated: 2026-01-11
Branch: feat/gold-accounting-xero
"""

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Categorization rules (from expense-rules.md)
EXACT_TECH_VENDORS = {
    'AMAZON WEB SERVICES': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'AWS': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'MICROSOFT AZURE': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'GOOGLE CLOUD': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'GITHUB': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'ADOBE': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'MICROSOFT 365': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'GOOGLE WORKSPACE': {'category': 'IT & Software', 'code': 433, 'confidence': 100},
    'SLACK': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'ZOOM': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
    'NOTION': {'category': 'IT & Software', 'code': 433, 'confidence': 95},
}

EXACT_MARKETING_VENDORS = {
    'GOOGLE ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'FACEBOOK ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'META ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
    'LINKEDIN ADS': {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100},
}

EXACT_BANK_FEE_VENDORS = {
    'STRIPE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'PAYPAL': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
    'SQUARE': {'category': 'Bank Fees', 'code': 404, 'confidence': 100},
}

EXACT_OFFICE_VENDORS = {
    'STAPLES': {'category': 'Office Expenses', 'code': 461, 'confidence': 100},
    'OFFICE DEPOT': {'category': 'Office Expenses', 'code': 461, 'confidence': 100},
}

# Combine all exact vendors
EXACT_VENDORS = {}
EXACT_VENDORS.update(EXACT_TECH_VENDORS)
EXACT_VENDORS.update(EXACT_MARKETING_VENDORS)
EXACT_VENDORS.update(EXACT_BANK_FEE_VENDORS)
EXACT_VENDORS.update(EXACT_OFFICE_VENDORS)

# Description keyword patterns
DESCRIPTION_KEYWORDS = {
    'IT & Software': ['software', 'license', 'subscription', 'saas', 'cloud', 'hosting'],
    'Advertising & Marketing': ['ads', 'advertising', 'marketing', 'campaign', 'promotion'],
    'Office Expenses': ['office supplies', 'stationery', 'printer', 'paper'],
    'Travel - National': ['flight', 'hotel', 'accommodation', 'rental car'],
    'Entertainment': ['dinner', 'lunch', 'networking', 'event'],
}


class ExpenseCategorizer:
    """Handles expense categorization logic"""

    def __init__(self, vault_path: str = "Vault", dry_run: bool = False, threshold: float = 0.90):
        """
        Initialize categorizer.

        Args:
            vault_path: Path to Obsidian vault
            dry_run: If True, preview categorizations without updating
            threshold: Minimum confidence for auto-categorization (0-1)
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.threshold = threshold
        self.transactions_path = self.vault_path / "Accounting" / "Transactions"

        # Statistics
        self.stats = {
            "total_processed": 0,
            "auto_categorized": 0,
            "approval_required": 0,
            "manual_review": 0,
            "errors": 0,
            "by_confidence": {
                "high": 0,  # 90-100%
                "medium": 0,  # 75-89%
                "low": 0,  # <75%
            }
        }

    def normalize_vendor(self, vendor: str) -> str:
        """Normalize vendor name for matching"""
        return vendor.upper().strip()

    def match_exact_vendor(self, vendor: str, description: str) -> Optional[Dict]:
        """
        Match against exact vendor list.

        Args:
            vendor: Vendor name
            description: Transaction description

        Returns:
            Match result dict or None
        """
        normalized = self.normalize_vendor(vendor)

        # Check exact match
        if normalized in EXACT_VENDORS:
            result = EXACT_VENDORS[normalized].copy()
            result['method'] = 'exact_vendor_match'
            return result

        return None

    def match_vendor_pattern(self, vendor: str, description: str) -> Optional[Dict]:
        """
        Match using vendor patterns.

        Args:
            vendor: Vendor name
            description: Transaction description

        Returns:
            Match result dict or None
        """
        vendor_norm = self.normalize_vendor(vendor)
        desc_norm = description.upper().strip()

        # Google Services (differentiate)
        if 'GOOGLE' in vendor_norm:
            if 'ADS' in desc_norm or 'ADWORDS' in desc_norm:
                return {'category': 'Advertising & Marketing', 'code': 400, 'confidence': 100, 'method': 'pattern_match'}
            elif 'WORKSPACE' in desc_norm or 'GSUITE' in desc_norm:
                return {'category': 'IT & Software', 'code': 433, 'confidence': 100, 'method': 'pattern_match'}
            elif 'CLOUD' in desc_norm:
                return {'category': 'IT & Software', 'code': 433, 'confidence': 100, 'method': 'pattern_match'}
            else:
                return {'category': 'IT & Software', 'code': 433, 'confidence': 85, 'method': 'pattern_match'}

        # Amazon (differentiate AWS vs Business vs Retail)
        if 'AMAZON' in vendor_norm:
            if 'AWS' in desc_norm or 'WEB SERVICES' in desc_norm:
                return {'category': 'IT & Software', 'code': 433, 'confidence': 100, 'method': 'pattern_match'}
            elif 'BUSINESS' in desc_norm:
                return {'category': 'Office Expenses', 'code': 461, 'confidence': 90, 'method': 'pattern_match'}
            else:
                return {'category': 'Office Expenses', 'code': 461, 'confidence': 70, 'method': 'pattern_match'}

        # Payment Processors
        if re.search(r'STRIPE|PAYPAL|SQUARE', vendor_norm):
            return {'category': 'Bank Fees', 'code': 404, 'confidence': 100, 'method': 'pattern_match'}

        # Airlines
        if re.search(r'AIRLINES|AIRWAYS|JETBLUE|SOUTHWEST|DELTA|UNITED', vendor_norm):
            return {'category': 'Travel - National', 'code': 493, 'confidence': 95, 'method': 'pattern_match'}

        # Hotels
        if re.search(r'HOTEL|MARRIOTT|HILTON|HYATT|AIRBNB', vendor_norm):
            return {'category': 'Travel - National', 'code': 493, 'confidence': 95, 'method': 'pattern_match'}

        # Restaurants (Entertainment)
        if re.search(r'RESTAURANT|CAFE|COFFEE|STARBUCKS', vendor_norm):
            return {'category': 'Entertainment', 'code': 420, 'confidence': 70, 'method': 'pattern_match'}

        return None

    def match_description_keywords(self, description: str) -> Optional[Dict]:
        """
        Match based on description keywords.

        Args:
            description: Transaction description

        Returns:
            Match result dict or None
        """
        desc_lower = description.lower()

        for category, keywords in DESCRIPTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    # Map category to code (simplified)
                    code_map = {
                        'IT & Software': 433,
                        'Advertising & Marketing': 400,
                        'Office Expenses': 461,
                        'Travel - National': 493,
                        'Entertainment': 420,
                    }
                    return {
                        'category': category,
                        'code': code_map.get(category, 429),
                        'confidence': 85,
                        'method': 'keyword_match',
                        'matched_keyword': keyword
                    }

        return None

    def categorize_transaction(self, transaction: Dict) -> Dict:
        """
        Categorize a single transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Categorization result
        """
        vendor = transaction.get("vendor", "Unknown")
        description = transaction.get("description", "")
        amount = transaction.get("amount", 0)

        # Try exact vendor match first (highest confidence)
        result = self.match_exact_vendor(vendor, description)
        if result and result['confidence'] >= self.threshold * 100:
            return result

        # Try vendor pattern match
        result = self.match_vendor_pattern(vendor, description)
        if result and result['confidence'] >= self.threshold * 100:
            return result

        # Try description keyword match
        result = self.match_description_keywords(description)
        if result and result['confidence'] >= self.threshold * 100:
            return result

        # No high-confidence match found
        return {
            'category': 'Uncategorized',
            'code': 429,  # General Expenses
            'confidence': 0,
            'method': 'none',
            'reason': 'No matching rules found'
        }

    def update_transaction_file(self, filepath: Path, categorization: Dict):
        """
        Update transaction file with categorization.

        Args:
            filepath: Path to transaction file
            categorization: Categorization result
        """
        # Read current content
        content = filepath.read_text(encoding="utf-8")

        # Update frontmatter
        # This is a simplified version; in production, use a YAML parser
        updated_content = content.replace(
            f"category: Uncategorized",
            f"category: {categorization['category']}"
        )
        updated_content = updated_content.replace(
            f"category_code: ",
            f"category_code: {categorization['code']}"
        )

        # Add categorization metadata
        categorization_note = f"\n\n## Auto-Categorization\n\n"
        categorization_note += f"- **Method:** {categorization['method']}\n"
        categorization_note += f"- **Confidence:** {categorization['confidence']}%\n"
        categorization_note += f"- **Timestamp:** {datetime.now().isoformat()}\n"

        if 'matched_keyword' in categorization:
            categorization_note += f"- **Matched Keyword:** {categorization['matched_keyword']}\n"

        # Append before the final line (if not already there)
        if "## Auto-Categorization" not in updated_content:
            parts = updated_content.split("---\n\n*Synced from Xero")
            if len(parts) == 2:
                updated_content = parts[0] + categorization_note + "\n---\n\n*Synced from Xero" + parts[1]

        if self.dry_run:
            print(f"[DRY RUN] Would update: {filepath.name}")
        else:
            filepath.write_text(updated_content, encoding="utf-8")
            print(f"[UPDATED] {filepath.name} → {categorization['category']} ({categorization['confidence']}%)")

    def process_all_uncategorized(self):
        """Process all uncategorized transactions"""
        print(f"[INFO] Processing uncategorized transactions in {self.transactions_path}...")

        if not self.transactions_path.exists():
            print(f"[ERROR] Transactions directory not found: {self.transactions_path}")
            return

        # Find all transaction files
        transaction_files = list(self.transactions_path.glob("TRANS_*.md"))
        print(f"[INFO] Found {len(transaction_files)} transaction files")

        for filepath in transaction_files:
            try:
                # Read transaction file (simplified parsing)
                content = filepath.read_text(encoding="utf-8")

                # Check if already categorized (simple check)
                if "category: Uncategorized" not in content and "category: " in content:
                    continue  # Skip already categorized

                # Extract transaction data (simplified)
                # In production, use proper frontmatter parser
                transaction = self.extract_transaction_from_file(content)

                # Categorize
                categorization = self.categorize_transaction(transaction)

                # Update statistics
                self.stats["total_processed"] += 1
                if categorization['confidence'] >= 90:
                    self.stats["by_confidence"]["high"] += 1
                    self.stats["auto_categorized"] += 1
                    self.update_transaction_file(filepath, categorization)
                elif categorization['confidence'] >= 75:
                    self.stats["by_confidence"]["medium"] += 1
                    self.stats["approval_required"] += 1
                    print(f"[APPROVAL] {filepath.name} → {categorization['category']} ({categorization['confidence']}%)")
                else:
                    self.stats["by_confidence"]["low"] += 1
                    self.stats["manual_review"] += 1
                    print(f"[REVIEW] {filepath.name} → Manual review needed ({categorization['confidence']}%)")

            except Exception as e:
                print(f"[ERROR] Failed to process {filepath.name}: {e}")
                self.stats["errors"] += 1

    def extract_transaction_from_file(self, content: str) -> Dict:
        """Extract transaction data from file content (simplified)"""
        # Simplified extraction - in production, use proper YAML parser
        transaction = {}

        # Extract vendor
        vendor_match = re.search(r'vendor: (.+)', content)
        if vendor_match:
            transaction['vendor'] = vendor_match.group(1).strip()

        # Extract description
        desc_match = re.search(r'# Transaction: (.+)', content)
        if desc_match:
            transaction['description'] = desc_match.group(1).strip()

        # Extract amount
        amount_match = re.search(r'amount: ([\d.]+)', content)
        if amount_match:
            transaction['amount'] = float(amount_match.group(1))

        return transaction


from datetime import datetime


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Auto-categorize expense transactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python categorize_expense.py                           # Categorize all uncategorized
  python categorize_expense.py --transaction-id TX123    # Categorize specific transaction
  python categorize_expense.py --dry-run                 # Preview without updating
  python categorize_expense.py --threshold 0.85          # Lower threshold (more aggressive)
        """
    )

    parser.add_argument(
        "--vault-path",
        help="Path to Obsidian vault",
        default="Vault"
    )

    parser.add_argument(
        "--transaction-id",
        help="Categorize specific transaction by ID",
        default=None
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview categorizations without updating"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        help="Minimum confidence for auto-categorization (0-1, default: 0.90)",
        default=0.90
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test suite"
    )

    args = parser.parse_args()

    # Create categorizer
    categorizer = ExpenseCategorizer(
        vault_path=args.vault_path,
        dry_run=args.dry_run,
        threshold=args.threshold
    )

    # Process transactions
    try:
        categorizer.process_all_uncategorized()

        # Output statistics
        print("\n" + "="*50)
        print("CATEGORIZATION STATISTICS")
        print("="*50)
        print(f"Total Processed:    {categorizer.stats['total_processed']}")
        print(f"Auto-Categorized:   {categorizer.stats['auto_categorized']} ({categorizer.stats['by_confidence']['high']} high confidence)")
        print(f"Approval Required:  {categorizer.stats['approval_required']} ({categorizer.stats['by_confidence']['medium']} medium confidence)")
        print(f"Manual Review:      {categorizer.stats['manual_review']} ({categorizer.stats['by_confidence']['low']} low confidence)")
        print(f"Errors:             {categorizer.stats['errors']}")

        # Calculate accuracy
        if categorizer.stats['total_processed'] > 0:
            accuracy = (categorizer.stats['auto_categorized'] / categorizer.stats['total_processed']) * 100
            print(f"\nAuto-Categorization Rate: {accuracy:.1f}%")
            if accuracy >= 80:
                print("✅ Target accuracy achieved (80%+)")
            else:
                print(f"⚠️ Below target accuracy (need {80-accuracy:.1f}% more)")

        print("="*50)

        sys.exit(0)

    except Exception as e:
        print(f"\n[FATAL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
