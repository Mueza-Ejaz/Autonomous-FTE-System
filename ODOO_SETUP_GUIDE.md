# Odoo Setup Guide for Gold Tier

## Overview
This guide provides step-by-step instructions for setting up Odoo Community Edition to integrate with the Gold Tier AI Employee system. The integration enables automated accounting, invoicing, and business management capabilities.

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), Windows 10+, or macOS 10.14+
- **Processor**: Dual-core 2 GHz or better
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 20 GB available space
- **Network**: Stable internet connection

### Software Dependencies
- Docker and Docker Compose (recommended approach)
- Python 3.8+ (for connector development)
- PostgreSQL client tools

## Installation Methods

### Method 1: Docker Installation (Recommended)

#### Step 1: Install Docker
```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# For Windows/Mac
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
```

#### Step 2: Create Odoo Docker Configuration
Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:17.0
    container_name: odoo-gold-tier
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=your_secure_password
    networks:
      - odoo-network

  db:
    image: postgres:13
    container_name: odoo-db-gold-tier
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=your_secure_password
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    networks:
      - odoo-network

volumes:
  odoo-web-data:
  odoo-db-data:

networks:
  odoo-network:
    driver: bridge
```

#### Step 3: Create Configuration Directory
```bash
mkdir -p config addons
```

#### Step 4: Create Odoo Configuration File
Create `config/odoo.conf`:

```ini
[options]
; Basic configuration
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
admin_passwd = master_password_change_this_immediately
db_host = db
db_port = 5432
db_user = odoo
db_password = your_secure_password
data_dir = /var/lib/odoo

; Server configuration
xmlrpc_port = 8069
longpolling_port = 8072
workers = 0  ; Use 0 for development, 4+ for production

; Logging
logfile = /var/log/odoo/odoo-server.log
log_level = info

; Security
limit_time_cpu = 600
limit_time_real = 1200
max_cron_threads = 1
```

#### Step 5: Start Odoo Services
```bash
docker-compose up -d
```

#### Step 6: Verify Installation
Open your browser and navigate to `http://localhost:8069`
You should see the Odoo setup screen.

### Method 2: Native Installation (Advanced Users)

#### Step 1: Install Python and Dependencies
```bash
# Install Python 3.8+
sudo apt-get update
sudo apt-get install python3 python3-pip python3-dev python3-venv

# Install system dependencies
sudo apt-get install build-essential libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev libjpeg-dev libpng-dev libfreetype6-dev
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv odoo-env
source odoo-env/bin/activate  # On Windows: odoo-env\Scripts\activate
```

#### Step 3: Install Odoo
```bash
pip3 install psycopg2-binary
pip3 install odoo
```

#### Step 4: Download Odoo Source (Alternative)
```bash
git clone https://github.com/odoo/odoo.git -b 17.0 --depth=1
cd odoo
pip install -e .
```

#### Step 5: Initialize Database
```bash
# Create PostgreSQL database user
sudo -u postgres createuser -s odoo
sudo -u postgres createdb odoo -O odoo
```

#### Step 6: Configure Odoo
Create an `odoo.conf` file similar to the Docker version above.

#### Step 7: Start Odoo Server
```bash
odoo -c odoo.conf
```

## Initial Configuration

### Step 1: Database Setup
1. Navigate to `http://localhost:8069`
2. Create a new database:
   - Database Name: `ai_employee_gold`
   - Master Password: Set a strong password
   - Email: Your admin email
   - Password: Admin password

### Step 2: Install Required Apps
After database creation, install these essential apps:
- Accounting
- Sales
- Purchase
- Inventory
- Project
- HR

### Step 3: Configure Accounting Modules
1. Go to **Accounting** → **Configuration** → **Settings**
2. Enable required features:
   - Invoicing
   - Purchase Bills & Costs
   - Analytic Accounting
   - Budget Management

### Step 4: Set Up Chart of Accounts
1. Go to **Accounting** → **Configuration** → **Charts of Accounts**
2. Choose an appropriate chart for your region
3. Customize accounts as needed for your business

## AI Employee Integration Setup

### Step 1: Configure Odoo Connector
The AI Employee system uses the `odoo_connector.py` module to interact with Odoo.

#### Update Configuration
Edit the configuration file at `AI_Employee_Vault/Gold_Tier/Odoo_Integration/Config/odoo_config.json`:

```json
{
  "odoo_config": {
    "url": "http://localhost:8069",
    "database": "ai_employee_gold",
    "username": "admin",  // Or create a dedicated API user
    "password": "your_odoo_admin_password",
    "api_key": "",  // For API key authentication if configured
    "modules": [
      "account",
      "sale",
      "crm",
      "project",
      "hr"
    ],
    "connection_timeout": 30,
    "retry_attempts": 3,
    "sync_frequency": "daily",
    "log_level": "INFO"
  }
}
```

### Step 2: Create API User (Recommended)
For security, create a dedicated user for API access:

1. Go to **Settings** → **Users & Companies** → **Users**
2. Create a new user:
   - Name: "AI Employee API"
   - Login: "ai.employee"
   - Password: Strong, unique password
3. Assign appropriate groups:
   - Accounting & Finance: Billing Manager
   - Sales: Sales Manager
   - Purchase: Purchase Manager

### Step 3: Configure OAuth (Optional)
For enhanced security, configure OAuth2:

1. Go to **Apps** → Search for "OAuth"
2. Install "OAuth2 Authentication"
3. Configure OAuth providers as needed

## Testing the Integration

### Step 1: Test Connection
Run the connection test:

```bash
python odoo_connector.py
```

### Step 2: Test Invoice Creation
The system should be able to:
- Create new customers
- Generate invoices
- Track payments
- Update financial reports

### Step 3: Verify MCP Server
Start the Odoo MCP server:

```bash
python odoo_mcp_server.py
```

The server should start on `http://localhost:8070` and be accessible to Claude Code.

## Security Best Practices

### 1. Database Security
- Use strong passwords
- Regular backups
- Limit database access
- Use SSL connections

### 2. API Security
- Use dedicated API user
- Implement rate limiting
- Monitor API usage
- Regular credential rotation

### 3. Network Security
- Use VPN for remote access
- Implement firewall rules
- Use HTTPS for production
- Regular security updates

## Troubleshooting

### Common Issues

#### Issue: Cannot Connect to Database
**Symptoms**: Connection refused or timeout errors
**Solutions**:
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check connection parameters in configuration
- Ensure database user has proper permissions

#### Issue: Odoo Won't Start
**Symptoms**: Server fails to start or crashes immediately
**Solutions**:
- Check `odoo.conf` file syntax
- Verify Python dependencies are installed
- Check file permissions

#### Issue: API Authentication Fails
**Symptoms**: 401 Unauthorized errors
**Solutions**:
- Verify credentials in configuration
- Check user permissions in Odoo
- Ensure database connection is correct

### Diagnostic Commands

```bash
# Check Docker containers
docker-compose ps

# View Odoo logs
docker-compose logs odoo

# Check database connectivity
docker exec -it odoo-db-gold-tier psql -U odoo -c "\dt"

# Test API connection
curl -X POST http://localhost:8069/xmlrpc/2/common \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0", "method":"call", "params":{"db":"ai_employee_gold"}}'
```

## Maintenance

### Regular Tasks
- **Daily**: Check system logs
- **Weekly**: Verify backup integrity
- **Monthly**: Review and update security settings
- **Quarterly**: Update Odoo to latest patch version

### Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec odoo-db-gold-tier pg_dump -U odoo ai_employee_gold > backup_${DATE}.sql
gzip backup_${DATE}.sql
```

## Upgrading Odoo

### Docker Method
```bash
# Stop current containers
docker-compose down

# Update docker-compose.yml to new version
# Change image: odoo:17.0 to image: odoo:18.0 (for example)

# Pull new image
docker-compose pull

# Start new containers
docker-compose up -d
```

### Native Installation
```bash
# Update pip package
pip install --upgrade odoo

# Or update from source
cd odoo
git pull
pip install -e .
```

## Conclusion

Once Odoo is properly configured, the Gold Tier AI Employee system will be able to:
- Automatically create and manage invoices
- Track expenses and revenue
- Generate financial reports
- Integrate with business workflows
- Provide real-time financial insights

The integration enables a fully automated accounting system that works alongside the AI Employee's other capabilities.