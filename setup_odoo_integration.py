"""
Setup script for Odoo Integration in Gold Tier
This script sets up the Odoo integration components and verifies the installation.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "requests",
        "aiohttp",
        "asyncio"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return False
    return True


def create_odoo_setup_files():
    """Create additional setup files for Odoo integration"""

    # Create a sample invoice template
    invoice_template = {
        "invoice_template": {
            "default_terms": "Payment due within 30 days",
            "default_taxes": [],
            "currency": "USD",
            "sequence_prefix": "INV/"
        }
    }

    template_path = "AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/invoice_template.json"
    with open(template_path, 'w') as f:
        json.dump(invoice_template, f, indent=2)

    print(f"Created invoice template at {template_path}")

    # Create a sample data file for testing
    sample_data = {
        "sample_customers": [
            {
                "name": "Gold Tier Customer",
                "email": "customer@goldtier.com",
                "phone": "+1-555-0123"
            }
        ],
        "sample_products": [
            {
                "name": "AI Employee Service",
                "description": "Monthly AI employee service",
                "price": 999.00,
                "uom": "Month"
            }
        ]
    }

    data_path = "AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/sample_data.json"
    with open(data_path, 'w') as f:
        json.dump(sample_data, f, indent=2)

    print(f"Created sample data at {data_path}")


def verify_odoo_setup():
    """Verify that Odoo integration is properly set up"""
    print("\nVerifying Odoo integration setup...")

    # Check if required files exist
    required_files = [
        "odoo_connector.py",
        "odoo_mcp_server.py",
        "AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/odoo_config.json"
    ]

    all_present = True
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            all_present = False
        else:
            print(f"✓ Found: {file_path}")

    # Test importing the connector
    try:
        from odoo_connector import OdooConnector, test_connection
        print("✓ Successfully imported OdooConnector")
    except ImportError as e:
        print(f"❌ Failed to import OdooConnector: {e}")
        all_present = False

    # Test importing the MCP server
    try:
        from odoo_mcp_server import OdooMCPHandler, OdooMCPServer
        print("✓ Successfully imported OdooMCP components")
    except ImportError as e:
        print(f"❌ Failed to import OdooMCP components: {e}")
        all_present = False

    if all_present:
        print("\n✓ Odoo integration setup verification PASSED")
        return True
    else:
        print("\n❌ Odoo integration setup verification FAILED")
        return False


def update_environment_config():
    """Update .env file with Odoo configuration"""
    env_file = ".env"

    # Check if .env file exists and contains Odoo config
    odoo_config_exists = False

    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if 'ODOO_' in content:
                odoo_config_exists = True

    if not odoo_config_exists:
        # Add Odoo configuration to .env file
        odoo_config = """
# ODOO CONFIGURATION (Gold Tier)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_gold
ODOO_USERNAME=admin
ODOO_PASSWORD=your_odoo_password
ODOO_API_KEY=your_odoo_api_key
"""
        with open(env_file, 'a') as f:
            f.write(odoo_config)

        print("Added Odoo configuration to .env file")


def main():
    """Main setup function"""
    print("Setting up Odoo Integration for Gold Tier...")
    print("=" * 50)

    # Check and install dependencies
    print("\n1. Checking Python dependencies...")
    deps_ok = check_python_dependencies()
    if deps_ok:
        print("✓ All required packages are installed")
    else:
        print("✓ Missing packages have been installed")

    # Create additional setup files
    print("\n2. Creating setup files...")
    create_odoo_setup_files()

    # Update environment configuration
    print("\n3. Updating environment configuration...")
    update_environment_config()

    # Verify setup
    print("\n4. Verifying setup...")
    setup_ok = verify_odoo_setup()

    print("\n" + "=" * 50)
    if setup_ok:
        print("✅ Odoo Integration setup completed successfully!")
        print("\nNext steps:")
        print("- Install Odoo Community Edition locally (Docker recommended)")
        print("- Start Odoo server at http://localhost:8069")
        print("- Update credentials in AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/odoo_config.json")
        print("- Run 'python odoo_mcp_server.py' to start the MCP server")
        print("- Test connection with 'python odoo_connector.py'")
    else:
        print("❌ Odoo Integration setup failed!")
        print("Please check the errors above and try again.")
        return False

    return True


if __name__ == "__main__":
    main()