# Xero MCP Server Setup Guide

**Purpose:** Complete setup instructions for Xero integration

**Estimated Time:** 30-60 minutes

**Last Updated:** 2026-01-11

---

## Prerequisites

Before starting, ensure you have:

- ✅ Xero account (free trial or paid subscription)
- ✅ Node.js v24+ installed
- ✅ Claude Code installed and configured
- ✅ Basic understanding of OAuth2
- ✅ Terminal/command line access

---

## Step 1: Create Xero Developer Account

1. **Sign up for Xero Developer Account**
   - Visit: https://developer.xero.com/
   - Click "Sign Up" or "Login" (use your Xero account credentials)
   - Accept developer terms

2. **Create a New App**
   - Navigate to: "My Apps" → "New App"
   - Fill in app details:
     - **App Name:** "Claude Code Autonomous FTE"
     - **Integration Type:** Select "Web App"
     - **Company or App URL:** `http://localhost:3000` (for local development)
     - **OAuth 2.0 redirect URI:** `http://localhost:3000/callback`

3. **Save App Credentials**
   - After creating app, note down:
     - **Client ID:** (e.g., `ABC123...`)
     - **Client Secret:** (click "Generate a secret")
   - **IMPORTANT:** Store these securely - you'll need them for MCP server config

---

## Step 2: Install Xero MCP Server

The official Xero MCP server is maintained by Xero and provides Claude Code integration.

### Installation

```bash
# Install globally via npm
npm install -g @xeroapi/xero-mcp-server

# Verify installation
xero-mcp-server --version
```

### Alternative: Clone from GitHub

```bash
# Clone the repository
git clone https://github.com/XeroAPI/xero-mcp-server.git
cd xero-mcp-server

# Install dependencies
npm install

# Build the server
npm run build
```

---

## Step 3: Configure Xero MCP Server

### Create Environment File

Create a `.env` file in your project root (or Xero MCP server directory):

```bash
# .env - DO NOT COMMIT THIS FILE

# Xero OAuth2 Credentials
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REDIRECT_URI=http://localhost:3000/callback

# Xero Scopes (permissions)
XERO_SCOPES=accounting.transactions,accounting.contacts,accounting.settings

# MCP Server Configuration
MCP_SERVER_PORT=3000
```

### Required Scopes

For full `manage-accounting` functionality, request these Xero scopes:

- `accounting.transactions` - Read/write bank transactions
- `accounting.transactions.read` - Read-only transactions
- `accounting.contacts` - Read/write contacts (clients)
- `accounting.contacts.read` - Read-only contacts
- `accounting.settings` - Read account settings
- `accounting.settings.read` - Read-only settings
- `accounting.attachments` - Upload receipts/invoices

**Recommended Minimal Scopes:**
```
accounting.transactions,accounting.contacts,accounting.settings
```

---

## Step 4: Configure Claude Code MCP Integration

### Locate Claude Code Config File

**Config file location:**
- **macOS/Linux:** `~/.config/claude-code/mcp.json`
- **Windows:** `%APPDATA%\claude-code\mcp.json`

### Add Xero MCP Server

Edit `mcp.json` and add the Xero MCP server configuration:

```json
{
  "mcpServers": {
    "xero": {
      "command": "node",
      "args": ["/path/to/xero-mcp-server/dist/index.js"],
      "env": {
        "XERO_CLIENT_ID": "your_client_id_here",
        "XERO_CLIENT_SECRET": "your_client_secret_here",
        "XERO_REDIRECT_URI": "http://localhost:3000/callback",
        "XERO_SCOPES": "accounting.transactions,accounting.contacts,accounting.settings"
      }
    }
  }
}
```

**If installed globally:**
```json
{
  "mcpServers": {
    "xero": {
      "command": "xero-mcp-server",
      "args": [],
      "env": {
        "XERO_CLIENT_ID": "your_client_id_here",
        "XERO_CLIENT_SECRET": "your_client_secret_here",
        "XERO_REDIRECT_URI": "http://localhost:3000/callback",
        "XERO_SCOPES": "accounting.transactions,accounting.contacts,accounting.settings"
      }
    }
  }
}
```

**Replace `/path/to/xero-mcp-server` with actual path:**
- Find path: `which xero-mcp-server` (Linux/Mac) or `where xero-mcp-server` (Windows)

---

## Step 5: Authenticate with Xero

### Start Authentication Flow

1. **Restart Claude Code** to load new MCP server configuration

2. **Test Connection**
   ```bash
   python .claude/skills/manage-accounting/scripts/xero_sync.py --test-connection
   ```

3. **OAuth2 Flow**
   - On first run, Xero MCP server will prompt for authentication
   - A browser window will open automatically
   - Login to your Xero account
   - Authorize the app to access your Xero data
   - Select which Xero organization to connect (if you have multiple)
   - You'll be redirected to `http://localhost:3000/callback`

4. **Token Storage**
   - Xero MCP server stores OAuth2 tokens securely
   - **Access Token:** Valid for 30 minutes
   - **Refresh Token:** Valid for 60 days
   - Tokens automatically refresh when expired

---

## Step 6: Verify Installation

### Test Xero MCP Connection

Run test commands to verify setup:

```bash
# Test 1: Connection test
python .claude/skills/manage-accounting/scripts/xero_sync.py --test-connection

# Test 2: Fetch organizations
# (Xero MCP server should return list of connected Xero orgs)

# Test 3: Sync transactions (dry run)
python .claude/skills/manage-accounting/scripts/xero_sync.py --dry-run
```

### Expected Output

✅ **Success:**
```
[INFO] Testing Xero MCP connection...
[SUCCESS] Xero MCP connection successful!
[INFO] Connected to: Your Company Name
[INFO] Organization ID: abc-123-def-456
```

❌ **Failure:**
```
[ERROR] Xero MCP connection failed: Invalid credentials
```

**Troubleshooting:** See Section 8 below.

---

## Step 7: Configure Bank Feeds (Optional but Recommended)

For automatic transaction sync, connect your bank to Xero:

### Option A: Xero Bank Feeds (Recommended)

1. **In Xero Web Interface:**
   - Go to: Accounting → Bank accounts
   - Click "Add Bank Account"
   - Search for your bank
   - Follow authorization flow

2. **Benefits:**
   - Automatic daily sync
   - Real-time transaction data
   - Reconciliation tools

### Option B: Manual Upload

1. **Export from your bank** (CSV format)
2. **Import to Xero:**
   - Accounting → Bank accounts → Import
   - Upload CSV file
   - Map columns

**Recommendation:** Use bank feeds for automation. Manual upload as fallback.

---

## Step 8: Troubleshooting

### Issue 1: "Invalid Client ID" Error

**Cause:** Incorrect credentials in MCP config

**Solution:**
1. Double-check `XERO_CLIENT_ID` and `XERO_CLIENT_SECRET` in `mcp.json`
2. Verify credentials match Xero Developer Portal
3. Regenerate secret if needed (old secret will be invalid)

---

### Issue 2: "Redirect URI Mismatch" Error

**Cause:** Redirect URI doesn't match Xero app settings

**Solution:**
1. Go to Xero Developer Portal → Your App → OAuth 2.0 redirect URIs
2. Ensure it includes: `http://localhost:3000/callback`
3. Update `XERO_REDIRECT_URI` in MCP config to match exactly

---

### Issue 3: "Insufficient Scopes" Error

**Cause:** Missing required permissions

**Solution:**
1. Check `XERO_SCOPES` in MCP config
2. Ensure includes: `accounting.transactions,accounting.contacts,accounting.settings`
3. Re-authenticate after updating scopes

---

### Issue 4: MCP Server Not Starting

**Cause:** Port conflict or Node.js version

**Solution:**
1. Check Node.js version: `node --version` (need v24+)
2. Change port in `.env`: `MCP_SERVER_PORT=3001`
3. Update redirect URI in Xero app to match new port
4. Check server logs: `xero-mcp-server --verbose`

---

### Issue 5: Token Expired / Re-authentication Required

**Cause:** Refresh token expired (>60 days since last auth)

**Solution:**
1. Re-run authentication flow
2. Delete stored tokens: `~/.xero-mcp-server/tokens.json` (or Windows equivalent)
3. Restart Claude Code
4. Re-authenticate when prompted

---

## Step 9: Security Best Practices

### Credential Security

✅ **DO:**
- Store credentials in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables in MCP config
- Rotate credentials quarterly
- Use separate Xero app for dev vs production

❌ **DON'T:**
- Commit `.env` to git
- Share credentials in Slack/email
- Use production Xero org for testing
- Store credentials in plain text

### Access Control

- **Principle of Least Privilege:** Only request scopes you need
- **Regular Audits:** Review Xero app access monthly
- **Revoke Unused Apps:** Disconnect old/unused integrations

### Token Management

- Tokens stored by Xero MCP server (encrypted)
- Access tokens: 30 min expiry (auto-refresh)
- Refresh tokens: 60 day expiry (re-auth required)
- Check token status: `xero-mcp-server --check-auth`

---

## Step 10: Testing with Xero Demo Company

For testing without affecting real data:

### Create Xero Demo Company

1. **In Xero:**
   - Click organization dropdown (top right)
   - Click "Add Organization"
   - Select "Try a demo company"
   - Choose industry (e.g., "Consulting")

2. **Switch to Demo Company:**
   - Organization dropdown → Select demo company
   - Re-authenticate Xero MCP server if needed

3. **Test Scripts:**
   ```bash
   # Sync demo data
   python .claude/skills/manage-accounting/scripts/xero_sync.py

   # Categorize demo expenses
   python .claude/skills/manage-accounting/scripts/categorize_expense.py --dry-run

   # Create test invoice
   python .claude/skills/manage-accounting/scripts/generate_invoice.py \
     --client "Test Client" \
     --amount 100 \
     --description "Test invoice"
   ```

**Benefits:**
- Safe testing environment
- Pre-populated with sample data
- No impact on real financials

---

## Step 11: Ongoing Maintenance

### Monthly Tasks

- [ ] Review Xero API usage (check rate limits)
- [ ] Verify all transactions syncing correctly
- [ ] Check token expiry date
- [ ] Review and update expense categorization rules
- [ ] Audit connected apps in Xero

### Quarterly Tasks

- [ ] Rotate Xero client secret
- [ ] Update expense-rules.md based on new vendors
- [ ] Review and update xero-categories.md
- [ ] Test invoice generation workflow
- [ ] Verify reconciliation accuracy (target: 95%+)

### Annual Tasks

- [ ] Review Xero subscription level (upgrade if needed)
- [ ] Archive old transaction files (>1 year)
- [ ] Update tax categories for new tax year
- [ ] Comprehensive security audit

---

## Quick Reference

### Xero Developer Portal
https://developer.xero.com/

### Xero MCP Server GitHub
https://github.com/XeroAPI/xero-mcp-server

### Xero API Documentation
https://developer.xero.com/documentation/api/accounting/overview

### Common Commands

```bash
# Test connection
python .claude/skills/manage-accounting/scripts/xero_sync.py --test-connection

# Sync transactions
python .claude/skills/manage-accounting/scripts/xero_sync.py

# Categorize expenses
python .claude/skills/manage-accounting/scripts/categorize_expense.py

# Create invoice
python .claude/skills/manage-accounting/scripts/generate_invoice.py --client "Name" --amount 1000 --description "Services"

# Check MCP server status
xero-mcp-server --status

# View MCP server logs
xero-mcp-server --logs
```

---

## Support

**Xero Support:**
- Developer Forum: https://community.xero.com/developer/
- Support Email: api@xero.com

**Claude Code Support:**
- GitHub Issues: https://github.com/anthropics/claude-code/issues

**This Skill:**
- See: `.claude/skills/manage-accounting/SKILL.md`
- Reference: `.claude/skills/manage-accounting/reference/`

---

*Last Updated: 2026-01-11 | Branch: feat/gold-accounting-xero*
*Setup Time: 30-60 minutes | Difficulty: Intermediate*
