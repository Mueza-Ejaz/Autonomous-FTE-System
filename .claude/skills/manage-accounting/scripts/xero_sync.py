#!/usr/bin/env python3
"""
Xero Transaction Sync Script

Fetches transactions from Xero via MCP server and updates Vault accounting records.

Usage:
    python xero_sync.py                                    # Sync today's transactions
    python xero_sync.py --date-range 2026-01-01:2026-01-11 # Sync specific range
    python xero_sync.py --dry-run                          # Preview without writing
    python xero_sync.py --json                             # JSON output
    python xero_sync.py --test-connection                  # Test Xero MCP connection

Author: Autonomous FTE
Version: 1.0
Last Updated: 2026-01-11
Branch: feat/gold-accounting-xero
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# NOTE: This script requires Xero MCP server to be running
# The actual MCP communication will be handled by Claude Code
# This script provides the data processing and file writing logic

class XeroSyncError(Exception):
    """Custom exception for Xero sync errors"""
    pass

class XeroSync:
    """Handles syncing Xero transactions to Vault"""

    def __init__(self, vault_path: str = "Vault", dry_run: bool = False):
        """
        Initialize Xero sync handler.

        Args:
            vault_path: Path to Obsidian vault root
            dry_run: If True, preview changes without writing files
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.accounting_path = self.vault_path / "Accounting"
        self.transactions_path = self.accounting_path / "Transactions"
        self.current_month_file = self.accounting_path / "Current_Month.md"

        # Create directories if they don't exist
        if not dry_run:
            self.accounting_path.mkdir(parents=True, exist_ok=True)
            self.transactions_path.mkdir(parents=True, exist_ok=True)

        # Sync statistics
        self.stats = {
            "total_transactions": 0,
            "new_transactions": 0,
            "updated_transactions": 0,
            "skipped_transactions": 0,
            "errors": 0,
            "revenue_transactions": 0,
            "expense_transactions": 0,
        }

    def fetch_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch transactions from Xero via MCP server.

        NOTE: This is a placeholder. The actual MCP call will be made by Claude Code.
        When Claude Code invokes this script, it will replace this function with
        actual MCP server communication.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of transaction dictionaries

        Raises:
            XeroSyncError: If MCP connection fails
        """
        print(f"[INFO] Fetching Xero transactions from {start_date} to {end_date}...")

        # Placeholder: In real implementation, Claude Code will call Xero MCP server
        # Example MCP call (pseudocode):
        # response = mcp_client.call("xero_mcp", "get_bank_transactions", {
        #     "start_date": start_date,
        #     "end_date": end_date
        # })

        # For testing purposes, return empty list
        # In production, this will be replaced with actual MCP response
        print("[WARNING] MCP integration pending. No transactions fetched.")
        print("[INFO] To enable, invoke this script through Claude Code with Xero MCP server running.")

        return []

    def process_transaction(self, transaction: Dict) -> Dict:
        """
        Process and enrich transaction data.

        Args:
            transaction: Raw transaction from Xero

        Returns:
            Enriched transaction dictionary
        """
        # Extract standard fields
        tx_id = transaction.get("BankTransactionID", "")
        date = transaction.get("Date", "")
        amount = float(transaction.get("Total", 0))
        description = transaction.get("Reference", transaction.get("Description", "Unknown"))
        contact = transaction.get("Contact", {}).get("Name", "Unknown")
        type_code = transaction.get("Type", "")  # RECEIVE, SPEND, etc.

        # Determine if revenue or expense
        tx_type = "revenue" if type_code == "RECEIVE" else "expense"

        # Extract category if already categorized in Xero
        category = None
        category_code = None
        line_items = transaction.get("LineItems", [])
        if line_items:
            first_item = line_items[0]
            category_code = first_item.get("AccountCode", "")
            category = first_item.get("Description", "")

        # Create enriched transaction
        enriched = {
            "id": tx_id,
            "date": date,
            "amount": amount,
            "description": description,
            "vendor": contact,
            "type": tx_type,
            "category": category,
            "category_code": category_code,
            "status": transaction.get("Status", ""),
            "reference": transaction.get("Reference", ""),
            "is_reconciled": transaction.get("IsReconciled", False),
            "raw_data": transaction,  # Keep full data for reference
        }

        return enriched

    def write_transaction_file(self, transaction: Dict) -> Path:
        """
        Write individual transaction file to Vault.

        Args:
            transaction: Processed transaction dictionary

        Returns:
            Path to created file
        """
        # Generate filename
        date_str = transaction["date"][:10] if transaction["date"] else "UNKNOWN"
        desc_slug = "".join(c if c.isalnum() else "_" for c in transaction["description"][:30])
        filename = f"TRANS_{date_str}_{desc_slug}.md"
        filepath = self.transactions_path / filename

        # Check if file already exists
        if filepath.exists():
            self.stats["skipped_transactions"] += 1
            return filepath

        # Format amount
        amount_str = f"${transaction['amount']:.2f}"
        if transaction["type"] == "expense":
            amount_str = f"-{amount_str}"

        # Create markdown content
        content = f"""---
type: transaction
id: {transaction['id']}
date: {transaction['date']}
amount: {transaction['amount']}
vendor: {transaction['vendor']}
category: {transaction.get('category', 'Uncategorized')}
category_code: {transaction.get('category_code', '')}
status: {transaction['status']}
is_reconciled: {transaction['is_reconciled']}
synced_at: {datetime.now().isoformat()}
---

# Transaction: {transaction['description']}

**Date:** {transaction['date']}
**Amount:** {amount_str}
**Vendor:** {transaction['vendor']}
**Type:** {transaction['type'].capitalize()}

## Details

- **Reference:** {transaction['reference']}
- **Status:** {transaction['status']}
- **Reconciled:** {'Yes' if transaction['is_reconciled'] else 'No'}

## Category

- **Category:** {transaction.get('category', 'Uncategorized')}
- **Code:** {transaction.get('category_code', 'N/A')}

## Notes

<!-- Add manual notes here -->

---

*Synced from Xero: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        if self.dry_run:
            print(f"[DRY RUN] Would create: {filepath}")
            self.stats["new_transactions"] += 1
        else:
            filepath.write_text(content, encoding="utf-8")
            self.stats["new_transactions"] += 1
            print(f"[CREATED] {filepath.name}")

        return filepath

    def update_current_month_summary(self, transactions: List[Dict]):
        """
        Update Current_Month.md with summary of all transactions.

        Args:
            transactions: List of processed transactions
        """
        if not transactions:
            print("[INFO] No transactions to summarize.")
            return

        # Calculate summary statistics
        total_revenue = sum(t["amount"] for t in transactions if t["type"] == "revenue")
        total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
        net_cash_flow = total_revenue - total_expenses

        # Group by category
        by_category = {}
        for tx in transactions:
            category = tx.get("category", "Uncategorized")
            if category not in by_category:
                by_category[category] = {
                    "count": 0,
                    "total": 0,
                    "transactions": []
                }
            by_category[category]["count"] += 1
            by_category[category]["total"] += tx["amount"]
            by_category[category]["transactions"].append(tx)

        # Current month
        current_month = datetime.now().strftime("%B %Y")

        # Build markdown content
        content = f"""# Accounting Summary - {current_month}

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

| Metric | Amount |
|--------|--------|
| **Total Revenue** | ${total_revenue:,.2f} |
| **Total Expenses** | ${total_expenses:,.2f} |
| **Net Cash Flow** | ${net_cash_flow:,.2f} |
| **Total Transactions** | {len(transactions)} |

---

## Revenue Breakdown

| Date | Description | Amount | Status |
|------|-------------|--------|--------|
"""

        # Add revenue transactions
        revenue_txs = [t for t in transactions if t["type"] == "revenue"]
        if revenue_txs:
            for tx in sorted(revenue_txs, key=lambda x: x["date"], reverse=True):
                status_icon = "✅" if tx["is_reconciled"] else "⏳"
                content += f"| {tx['date'][:10]} | {tx['description']} | ${tx['amount']:,.2f} | {status_icon} |\n"
        else:
            content += "| - | No revenue transactions | - | - |\n"

        content += "\n---\n\n## Expense Breakdown by Category\n\n"

        # Add expense transactions grouped by category
        expense_txs = [t for t in transactions if t["type"] == "expense"]
        if expense_txs:
            for category in sorted(by_category.keys()):
                cat_data = by_category[category]
                content += f"### {category} (${cat_data['total']:,.2f})\n\n"
                content += "| Date | Description | Amount | Status |\n"
                content += "|------|-------------|--------|--------|\n"

                cat_txs = [t for t in cat_data["transactions"] if t["type"] == "expense"]
                for tx in sorted(cat_txs, key=lambda x: x["date"], reverse=True):
                    status_icon = "✅" if tx["is_reconciled"] else "⏳"
                    content += f"| {tx['date'][:10]} | {tx['description']} | ${tx['amount']:,.2f} | {status_icon} |\n"

                content += "\n"
        else:
            content += "No expense transactions.\n\n"

        content += "---\n\n"
        content += f"*Generated by xero_sync.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        if self.dry_run:
            print(f"[DRY RUN] Would update: {self.current_month_file}")
        else:
            self.current_month_file.write_text(content, encoding="utf-8")
            print(f"[UPDATED] {self.current_month_file.name}")

    def sync(self, start_date: str, end_date: str) -> Dict:
        """
        Main sync function.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Sync statistics dictionary
        """
        print(f"[INFO] Starting Xero sync...")
        print(f"[INFO] Date range: {start_date} to {end_date}")
        print(f"[INFO] Vault path: {self.vault_path}")
        print(f"[INFO] Dry run: {self.dry_run}")

        try:
            # Fetch transactions from Xero
            raw_transactions = self.fetch_transactions(start_date, end_date)
            self.stats["total_transactions"] = len(raw_transactions)

            if not raw_transactions:
                print("[INFO] No transactions to sync.")
                return self.stats

            # Process each transaction
            processed_transactions = []
            for raw_tx in raw_transactions:
                try:
                    processed = self.process_transaction(raw_tx)
                    processed_transactions.append(processed)

                    # Update type counters
                    if processed["type"] == "revenue":
                        self.stats["revenue_transactions"] += 1
                    else:
                        self.stats["expense_transactions"] += 1

                    # Write individual transaction file
                    self.write_transaction_file(processed)

                except Exception as e:
                    print(f"[ERROR] Failed to process transaction: {e}")
                    self.stats["errors"] += 1

            # Update monthly summary
            self.update_current_month_summary(processed_transactions)

            print(f"\n[SUCCESS] Sync complete!")
            return self.stats

        except Exception as e:
            print(f"[ERROR] Sync failed: {e}")
            raise XeroSyncError(f"Sync failed: {e}")

    def test_connection(self) -> bool:
        """
        Test connection to Xero MCP server.

        Returns:
            True if connection successful, False otherwise
        """
        print("[INFO] Testing Xero MCP connection...")

        # Placeholder: In real implementation, test MCP connection
        # Example:
        # try:
        #     response = mcp_client.call("xero_mcp", "test_connection", {})
        #     if response.get("status") == "ok":
        #         print("[SUCCESS] Xero MCP connection successful!")
        #         return True
        # except Exception as e:
        #     print(f"[ERROR] Xero MCP connection failed: {e}")
        #     return False

        print("[WARNING] MCP connection test not implemented yet.")
        print("[INFO] Xero MCP server must be configured in Claude Code settings.")
        return False


def parse_date_range(date_range_str: str) -> tuple:
    """
    Parse date range string.

    Args:
        date_range_str: Date range in format "YYYY-MM-DD:YYYY-MM-DD"

    Returns:
        Tuple of (start_date, end_date)
    """
    try:
        start, end = date_range_str.split(":")
        # Validate dates
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end, "%Y-%m-%d")
        return start, end
    except ValueError as e:
        raise ValueError(f"Invalid date range format. Use YYYY-MM-DD:YYYY-MM-DD") from e


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Sync Xero transactions to Vault accounting records",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python xero_sync.py                                    # Sync today's transactions
  python xero_sync.py --date-range 2026-01-01:2026-01-11 # Sync specific range
  python xero_sync.py --dry-run                          # Preview without writing
  python xero_sync.py --json                             # JSON output
  python xero_sync.py --test-connection                  # Test Xero MCP connection
        """
    )

    parser.add_argument(
        "--date-range",
        help="Date range to sync (YYYY-MM-DD:YYYY-MM-DD)",
        default=None
    )

    parser.add_argument(
        "--vault-path",
        help="Path to Obsidian vault",
        default="Vault"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Xero MCP connection and exit"
    )

    args = parser.parse_args()

    # Create sync handler
    syncer = XeroSync(vault_path=args.vault_path, dry_run=args.dry_run)

    # Test connection if requested
    if args.test_connection:
        success = syncer.test_connection()
        sys.exit(0 if success else 1)

    # Determine date range
    if args.date_range:
        try:
            start_date, end_date = parse_date_range(args.date_range)
        except ValueError as e:
            print(f"[ERROR] {e}")
            sys.exit(1)
    else:
        # Default: Today only
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = today
        end_date = today

    # Run sync
    try:
        stats = syncer.sync(start_date, end_date)

        # Output results
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n" + "="*50)
            print("SYNC STATISTICS")
            print("="*50)
            print(f"Total Transactions: {stats['total_transactions']}")
            print(f"New Transactions:   {stats['new_transactions']}")
            print(f"Updated:            {stats['updated_transactions']}")
            print(f"Skipped:            {stats['skipped_transactions']}")
            print(f"Revenue:            {stats['revenue_transactions']}")
            print(f"Expenses:           {stats['expense_transactions']}")
            print(f"Errors:             {stats['errors']}")
            print("="*50)

        sys.exit(0)

    except XeroSyncError as e:
        print(f"\n[FATAL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
