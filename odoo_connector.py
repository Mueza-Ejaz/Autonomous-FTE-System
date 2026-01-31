"""
Odoo Integration Module for Gold Tier
Handles integration with Odoo Community Edition for accounting, invoicing, and business management.
"""

import json
import requests
from datetime import datetime
import os
from typing import Dict, List, Optional


class OdooConnector:
    """
    Connector class for interacting with Odoo via JSON-RPC API
    """

    def __init__(self, config_path: str = None):
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.config = config['odoo_config']
        else:
            # Default configuration
            self.config = {
                "url": "http://localhost:8069",
                "database": "ai_employee_gold",
                "username": "admin",
                "password": "",
                "api_key": "",
                "modules": ["account", "sale", "crm", "project", "hr"],
                "connection_timeout": 30,
                "retry_attempts": 3
            }

        self.url = self.config['url']
        self.db = self.config['database']
        self.username = self.config['username']
        self.password = self.config['password']
        self.uid = None

    def connect(self) -> bool:
        """Authenticate and connect to Odoo instance"""
        try:
            # Get user ID via common endpoint
            common_url = f"{self.url}/xmlrpc/2/common"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "res.users",
                    "method": "authenticate",
                    "args": [self.db, self.username, self.password, {}]
                },
                "id": int(datetime.now().timestamp())
            }

            response = requests.post(common_url, json=payload, timeout=self.config['connection_timeout'])
            result = response.json()

            if 'result' in result and result['result']:
                self.uid = result['result']
                print(f"Successfully connected to Odoo as {self.username}")
                return True
            else:
                print("Authentication failed")
                return False

        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def create_invoice(self, partner_id: int, lines: List[Dict], date: str = None) -> Optional[int]:
        """Create an invoice in Odoo"""
        if not self.uid:
            if not self.connect():
                return None

        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        try:
            # Prepare invoice data
            invoice_data = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'invoice_date': date,
                'invoice_line_ids': []
            }

            for line in lines:
                invoice_line = {
                    'product_id': line.get('product_id', False),
                    'name': line.get('name', ''),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                    'tax_ids': line.get('tax_ids', [])
                }
                invoice_data['invoice_line_ids'].append([0, 0, invoice_line])

            # Call Odoo API to create invoice
            models_url = f"{self.url}/xmlrpc/2/object"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.db,
                        self.uid,
                        self.password,
                        'account.move',
                        'create',
                        [invoice_data]
                    ]
                },
                "id": int(datetime.now().timestamp())
            }

            response = requests.post(models_url, json=payload, timeout=self.config['connection_timeout'])
            result = response.json()

            if 'result' in result:
                invoice_id = result['result']
                print(f"Invoice created successfully with ID: {invoice_id}")
                return invoice_id
            else:
                print(f"Failed to create invoice: {result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"Error creating invoice: {str(e)}")
            return None

    def get_partner_by_email(self, email: str) -> Optional[int]:
        """Get partner ID by email"""
        if not self.uid:
            if not self.connect():
                return None

        try:
            models_url = f"{self.url}/xmlrpc/2/object"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.db,
                        self.uid,
                        self.password,
                        'res.partner',
                        'search',
                        [[['email', '=', email]]],
                        {'limit': 1}
                    ]
                },
                "id": int(datetime.now().timestamp())
            }

            response = requests.post(models_url, json=payload, timeout=self.config['connection_timeout'])
            result = response.json()

            if 'result' in result and result['result']:
                return result['result'][0]  # Return first match
            else:
                print(f"No partner found with email: {email}")
                return None

        except Exception as e:
            print(f"Error searching partner: {str(e)}")
            return None

    def create_partner(self, name: str, email: str = None, phone: str = None) -> Optional[int]:
        """Create a new partner/customer in Odoo"""
        if not self.uid:
            if not self.connect():
                return None

        try:
            partner_data = {
                'name': name,
                'email': email,
                'phone': phone
            }

            models_url = f"{self.url}/xmlrpc/2/object"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.db,
                        self.uid,
                        self.password,
                        'res.partner',
                        'create',
                        [partner_data]
                    ]
                },
                "id": int(datetime.now().timestamp())
            }

            response = requests.post(models_url, json=payload, timeout=self.config['connection_timeout'])
            result = response.json()

            if 'result' in result:
                partner_id = result['result']
                print(f"Partner created successfully with ID: {partner_id}")
                return partner_id
            else:
                print(f"Failed to create partner: {result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"Error creating partner: {str(e)}")
            return None

    def get_unpaid_invoices(self) -> List[Dict]:
        """Get all unpaid invoices"""
        if not self.uid:
            if not self.connect():
                return []

        try:
            models_url = f"{self.url}/xmlrpc/2/object"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.db,
                        self.uid,
                        self.password,
                        'account.move',
                        'search_read',
                        [
                            [
                                ['state', '=', 'posted'],
                                ['payment_state', '!=', 'paid'],
                                ['move_type', '=', 'out_invoice']
                            ]
                        ],
                        ['name', 'partner_id', 'amount_total', 'invoice_date', 'payment_state']
                    ]
                },
                "id": int(datetime.now().timestamp())
            }

            response = requests.post(models_url, json=payload, timeout=self.config['connection_timeout'])
            result = response.json()

            if 'result' in result:
                return result['result']
            else:
                print(f"Failed to get unpaid invoices: {result.get('error', 'Unknown error')}")
                return []

        except Exception as e:
            print(f"Error getting unpaid invoices: {str(e)}")
            return []


def test_connection():
    """Test function to verify Odoo connection"""
    print("Testing Odoo connection...")

    # Use the config file we created
    connector = OdooConnector("AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/odoo_config.json")

    if connector.connect():
        print("✓ Odoo connection successful!")
        return True
    else:
        print("✗ Odoo connection failed - make sure Odoo is running at http://localhost:8069")
        return False


if __name__ == "__main__":
    test_connection()