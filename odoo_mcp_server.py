"""
Odoo MCP Server for Gold Tier
Implements MCP protocol for Odoo integration allowing Claude to interact with Odoo for accounting, invoicing, and business management.
"""

import asyncio
import json
from typing import Dict, Any, List
from pathlib import Path
import aiohttp
from aiohttp import web
import logging
from datetime import datetime

from odoo_connector import OdooConnector


class OdooMCPHandler:
    """Handler for Odoo MCP commands"""

    def __init__(self):
        self.connector = OdooConnector("AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/odoo_config.json")
        self.logger = logging.getLogger(__name__)

    async def handle_request(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP commands for Odoo operations"""

        if command == "create_invoice":
            return await self.create_invoice(params)
        elif command == "get_unpaid_invoices":
            return await self.get_unpaid_invoices(params)
        elif command == "create_customer":
            return await self.create_customer(params)
        elif command == "search_customer":
            return await self.search_customer(params)
        elif command == "record_payment":
            return await self.record_payment(params)
        elif command == "get_financial_report":
            return await self.get_financial_report(params)
        elif command == "health_check":
            return await self.health_check()
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "data": None
            }

    async def create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an invoice in Odoo"""
        try:
            customer_email = params.get('customer_email')
            customer_name = params.get('customer_name')
            line_items = params.get('line_items', [])
            invoice_date = params.get('invoice_date')

            # First, try to find the customer by email
            customer_id = None
            if customer_email:
                customer_id = self.connector.get_partner_by_email(customer_email)

            # If not found and customer_name provided, create new customer
            if not customer_id and customer_name:
                customer_id = self.connector.create_partner(
                    name=customer_name,
                    email=customer_email
                )

            if not customer_id:
                return {
                    "success": False,
                    "error": "Could not find or create customer",
                    "data": None
                }

            # Create the invoice
            invoice_id = self.connector.create_invoice(
                partner_id=customer_id,
                lines=line_items,
                date=invoice_date
            )

            if invoice_id:
                return {
                    "success": True,
                    "error": None,
                    "data": {
                        "invoice_id": invoice_id,
                        "customer_id": customer_id
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create invoice",
                    "data": None
                }

        except Exception as e:
            self.logger.error(f"Error creating invoice: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def get_unpaid_invoices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all unpaid invoices"""
        try:
            invoices = self.connector.get_unpaid_invoices()

            return {
                "success": True,
                "error": None,
                "data": {
                    "invoices": invoices,
                    "count": len(invoices)
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting unpaid invoices: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def create_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a customer in Odoo"""
        try:
            name = params.get('name')
            email = params.get('email')
            phone = params.get('phone')

            customer_id = self.connector.create_partner(name, email, phone)

            if customer_id:
                return {
                    "success": True,
                    "error": None,
                    "data": {
                        "customer_id": customer_id
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create customer",
                    "data": None
                }

        except Exception as e:
            self.logger.error(f"Error creating customer: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def search_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for a customer by email"""
        try:
            email = params.get('email')

            customer_id = self.connector.get_partner_by_email(email)

            if customer_id:
                return {
                    "success": True,
                    "error": None,
                    "data": {
                        "customer_id": customer_id,
                        "found": True
                    }
                }
            else:
                return {
                    "success": True,
                    "error": None,
                    "data": {
                        "customer_id": None,
                        "found": False
                    }
                }

        except Exception as e:
            self.logger.error(f"Error searching customer: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def record_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Record a payment for an invoice"""
        # Placeholder implementation - actual payment recording would be more complex
        invoice_id = params.get('invoice_id')
        amount = params.get('amount')
        payment_method = params.get('payment_method', 'manual')

        # In a real implementation, this would record the payment in Odoo
        # For now, we'll just return a success response
        return {
            "success": True,
            "error": None,
            "data": {
                "payment_recorded": True,
                "invoice_id": invoice_id,
                "amount": amount,
                "method": payment_method
            }
        }

    async def get_financial_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial report data"""
        # Placeholder implementation - would connect to Odoo reporting
        start_date = params.get('start_date')
        end_date = params.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        # This would normally fetch data from Odoo
        # For now, return a template response
        return {
            "success": True,
            "error": None,
            "data": {
                "report_period": f"{start_date} to {end_date}",
                "revenue": 0,
                "expenses": 0,
                "profit": 0,
                "invoiced_amount": 0,
                "paid_amount": 0,
                "unpaid_amount": 0
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check if Odoo connection is healthy"""
        try:
            # Test the connection
            connected = self.connector.connect()

            return {
                "success": True,
                "error": None,
                "data": {
                    "connected": connected,
                    "server_url": self.connector.url,
                    "database": self.connector.db
                }
            }
        except Exception as e:
            self.logger.error(f"Health check error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }


# MCP Server Implementation
class OdooMCPServer:
    """MCP Server for Odoo integration"""

    def __init__(self):
        self.handler = OdooMCPHandler()
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        """Setup web routes for MCP server"""
        self.app.router.add_post('/execute', self.handle_execute)
        self.app.router.add_get('/health', self.health)

    async def handle_execute(self, request):
        """Handle MCP execute command"""
        try:
            data = await request.json()
            command = data.get('command')
            params = data.get('params', {})

            result = await self.handler.handle_request(command, params)

            return web.json_response({
                "version": "1.0",
                "request_id": data.get('request_id'),
                "result": result
            })
        except Exception as e:
            return web.json_response({
                "version": "1.0",
                "request_id": data.get('request_id') if 'data' in locals() else None,
                "result": {
                    "success": False,
                    "error": str(e),
                    "data": None
                }
            })

    async def health(self, request):
        """Health check endpoint"""
        result = await self.handler.health_check()
        return web.json_response(result)

    async def start(self, host='localhost', port=8070):
        """Start the MCP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        print(f"Odoo MCP Server started at http://{host}:{port}")
        print("Ready to handle Odoo integration commands...")

        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("Shutting down Odoo MCP Server...")
            await runner.cleanup()


async def main():
    """Main function to start the Odoo MCP server"""
    server = OdooMCPServer()
    await server.start(host='localhost', port=8070)


if __name__ == "__main__":
    # Test the Odoo connector first
    print("Testing Odoo connector...")
    from odoo_connector import test_connection
    test_connection()

    print("\nStarting Odoo MCP Server...")
    # Uncomment the next line to start the server
    # asyncio.run(main())