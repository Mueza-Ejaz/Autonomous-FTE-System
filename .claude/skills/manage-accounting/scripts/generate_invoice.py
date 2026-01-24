#!/usr/bin/env python3
"""
Invoice Generation Script

Creates invoice approval requests for Xero integration.
ALWAYS requires human approval before creating invoices in Xero.

Usage:
    python generate_invoice.py --client "Client A" --amount 1500 --description "Services"
    python generate_invoice.py --client "Client B" --template retainer --amount 3500
    python generate_invoice.py --line-items-file invoice_items.json

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


class InvoiceGenerator:
    """Handles invoice approval request generation"""

    def __init__(self, vault_path: str = "Vault"):
        """
        Initialize invoice generator.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.accounting_path = self.vault_path / "Accounting"
        self.invoices_path = self.accounting_path / "Invoices"

        # Create directories
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)
        self.invoices_path.mkdir(parents=True, exist_ok=True)

        # Invoice number tracking
        self.invoice_number_file = self.accounting_path / "invoice_counter.txt"

    def get_next_invoice_number(self) -> str:
        """
        Get next invoice number in sequence.

        Returns:
            Invoice number in format INV-YYYY-###
        """
        year = datetime.now().year
        prefix = f"INV-{year}-"

        # Read current counter
        if self.invoice_number_file.exists():
            content = self.invoice_number_file.read_text().strip()
            try:
                last_number = int(content)
                next_number = last_number + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1

        # Update counter file
        self.invoice_number_file.write_text(str(next_number))

        # Format invoice number
        invoice_number = f"{prefix}{next_number:03d}"
        return invoice_number

    def calculate_due_date(self, payment_terms: str = "Net 15") -> str:
        """
        Calculate due date based on payment terms.

        Args:
            payment_terms: Payment terms (e.g., "Net 15", "Net 30")

        Returns:
            Due date in ISO format
        """
        # Extract days from payment terms
        if "Net" in payment_terms:
            try:
                days = int(payment_terms.split()[1])
            except:
                days = 15  # Default
        else:
            days = 15

        due_date = datetime.now() + timedelta(days=days)
        return due_date.strftime("%Y-%m-%d")

    def create_hourly_invoice(self, client: str, amount: float, description: str, hours: Optional[float] = None, rate: Optional[float] = None) -> Dict:
        """
        Create hourly rate invoice data.

        Args:
            client: Client name
            amount: Total amount
            description: Service description
            hours: Hours worked (optional)
            rate: Hourly rate (optional)

        Returns:
            Invoice data dictionary
        """
        if hours and rate:
            calculated_amount = hours * rate
        elif hours:
            rate = amount / hours
            calculated_amount = amount
        elif rate:
            hours = amount / rate
            calculated_amount = amount
        else:
            # No hours/rate provided, treat as fixed amount
            hours = None
            rate = None
            calculated_amount = amount

        invoice_data = {
            "template": "hourly",
            "client": client,
            "invoice_number": self.get_next_invoice_number(),
            "invoice_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": self.calculate_due_date("Net 15"),
            "payment_terms": "Net 15 days",
            "line_items": [
                {
                    "description": description,
                    "hours": hours if hours else 1,
                    "rate": rate if rate else amount,
                    "amount": calculated_amount
                }
            ],
            "subtotal": calculated_amount,
            "tax_rate": 0,  # Update based on jurisdiction
            "tax_amount": 0,
            "total": calculated_amount
        }

        return invoice_data

    def create_project_invoice(self, client: str, amount: float, description: str, project_name: str) -> Dict:
        """
        Create project-based (fixed price) invoice data.

        Args:
            client: Client name
            amount: Fixed project amount
            description: Project description
            project_name: Project name

        Returns:
            Invoice data dictionary
        """
        invoice_data = {
            "template": "project",
            "client": client,
            "project_name": project_name,
            "invoice_number": self.get_next_invoice_number(),
            "invoice_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": self.calculate_due_date("Net 30"),
            "payment_terms": "Net 30 days",
            "line_items": [
                {
                    "description": f"{project_name} - {description}",
                    "quantity": 1,
                    "amount": amount
                }
            ],
            "subtotal": amount,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": amount
        }

        return invoice_data

    def create_approval_request(self, invoice_data: Dict) -> Path:
        """
        Create approval request file for invoice.

        Args:
            invoice_data: Invoice data dictionary

        Returns:
            Path to created approval request file
        """
        # Generate filename
        client_slug = "".join(c if c.isalnum() else "_" for c in invoice_data["client"][:20])
        amount_str = f"{invoice_data['total']:.0f}"
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"APPROVAL_INVOICE_{client_slug}_{amount_str}_{date_str}.md"
        filepath = self.pending_approval_path / filename

        # Build line items table
        line_items_table = "| Description | Qty/Hours | Rate | Amount |\n"
        line_items_table += "|-------------|-----------|------|--------|\n"

        for item in invoice_data["line_items"]:
            desc = item["description"]
            qty = item.get("hours", item.get("quantity", 1))
            rate = item.get("rate", item.get("amount", 0))
            amount = item["amount"]
            line_items_table += f"| {desc} | {qty} | ${rate:,.2f} | ${amount:,.2f} |\n"

        # Create markdown content
        content = f"""---
type: approval_request
action: create_invoice
template: {invoice_data["template"]}
client: {invoice_data["client"]}
invoice_number: {invoice_data["invoice_number"]}
amount: {invoice_data["total"]}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(hours=24)).isoformat()}
status: pending
---

# Invoice Approval Request

## Invoice Details

**Client:** {invoice_data["client"]}
**Invoice Number:** {invoice_data["invoice_number"]}
**Template:** {invoice_data["template"].capitalize()}
**Invoice Date:** {invoice_data["invoice_date"]}
**Due Date:** {invoice_data["due_date"]}
**Payment Terms:** {invoice_data["payment_terms"]}

---

## Line Items

{line_items_table}

**Subtotal:** ${invoice_data["subtotal"]:,.2f}
**Tax ({invoice_data["tax_rate"]}%):** ${invoice_data["tax_amount"]:,.2f}
**Total:** ${invoice_data["total"]:,.2f}

---

## Client Information

- **Name:** {invoice_data["client"]}
- **Email:** [To be looked up in Xero]
- **Contact ID (Xero):** [To be looked up in Xero]

---

## Preview

This invoice will be created in Xero as a **DRAFT** and will require manual sending.

**What will happen when approved:**
1. Look up client contact in Xero by name
2. Create invoice with line items above
3. Set status to DRAFT (not sent automatically)
4. Capture invoice number and URL from Xero
5. Log to Dashboard and accounting records
6. Move this approval file to /Done

**Note:** Invoice will be created as DRAFT. You must manually send it from Xero after reviewing.

---

## To Approve

Move this file to `Vault/Approved/` folder.

## To Reject

Move this file to `Vault/Rejected/` folder and add rejection reason below.

---

## Rejection Reason (if applicable)

<!-- Add rejection reason here -->

---

*Generated by generate_invoice.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Write file
        filepath.write_text(content, encoding="utf-8")
        print(f"[CREATED] Invoice approval request: {filepath.name}")
        print(f"[INFO] Review and move to /Approved to create invoice in Xero")

        return filepath

    def generate_invoice(self, client: str, amount: float, description: str, template: str = "hourly", **kwargs) -> Path:
        """
        Main invoice generation function.

        Args:
            client: Client name
            amount: Invoice amount
            description: Service/project description
            template: Invoice template (hourly, project, retainer)
            **kwargs: Additional template-specific parameters

        Returns:
            Path to created approval request file
        """
        print(f"[INFO] Generating {template} invoice for {client}...")
        print(f"[INFO] Amount: ${amount:,.2f}")

        # Create invoice data based on template
        if template == "hourly":
            invoice_data = self.create_hourly_invoice(
                client=client,
                amount=amount,
                description=description,
                hours=kwargs.get("hours"),
                rate=kwargs.get("rate")
            )
        elif template == "project":
            invoice_data = self.create_project_invoice(
                client=client,
                amount=amount,
                description=description,
                project_name=kwargs.get("project_name", "Project")
            )
        else:
            print(f"[ERROR] Unknown template: {template}")
            sys.exit(1)

        # Create approval request
        approval_file = self.create_approval_request(invoice_data)

        return approval_file


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate invoice approval requests for Xero",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hourly invoice
  python generate_invoice.py --client "Client A" --amount 1500 --description "Consulting services"

  # With hours and rate
  python generate_invoice.py --client "Client B" --amount 3000 --description "Development" --hours 20 --rate 150

  # Project-based invoice
  python generate_invoice.py --client "Client C" --amount 5000 --template project --project-name "Website Redesign"

  # Retainer invoice
  python generate_invoice.py --client "Client D" --amount 3500 --template retainer --description "Monthly retainer - January 2026"
        """
    )

    parser.add_argument(
        "--client",
        required=True,
        help="Client name (must match Xero contact)"
    )

    parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Total invoice amount"
    )

    parser.add_argument(
        "--description",
        required=True,
        help="Service or project description"
    )

    parser.add_argument(
        "--template",
        choices=["hourly", "project", "retainer"],
        default="hourly",
        help="Invoice template (default: hourly)"
    )

    parser.add_argument(
        "--hours",
        type=float,
        help="Hours worked (for hourly invoices)"
    )

    parser.add_argument(
        "--rate",
        type=float,
        help="Hourly rate (for hourly invoices)"
    )

    parser.add_argument(
        "--project-name",
        help="Project name (for project-based invoices)"
    )

    parser.add_argument(
        "--vault-path",
        default="Vault",
        help="Path to Obsidian vault"
    )

    args = parser.parse_args()

    # Create generator
    generator = InvoiceGenerator(vault_path=args.vault_path)

    # Generate invoice
    try:
        approval_file = generator.generate_invoice(
            client=args.client,
            amount=args.amount,
            description=args.description,
            template=args.template,
            hours=args.hours,
            rate=args.rate,
            project_name=args.project_name
        )

        print(f"\n[SUCCESS] Approval request created!")
        print(f"[FILE] {approval_file}")
        print(f"\n[NEXT STEPS]")
        print(f"1. Review the approval request in: {approval_file}")
        print(f"2. If approved, move to: {args.vault_path}/Approved/")
        print(f"3. Run: /handle-approval to process approved invoices")

        sys.exit(0)

    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
