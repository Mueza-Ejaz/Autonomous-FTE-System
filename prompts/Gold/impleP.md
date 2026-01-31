GOLD TIER IMPLEMENTATION PROMPT
PROJECT CONTEXT
You are upgrading the Silver Tier AI Employee to Gold Tier (Autonomous Employee). This is Phase 3 (P3). Create branch P3-Gold-Tier from Silver branch. You must ENHANCE existing Silver code, not rewrite.

🎯 GOLD TIER OBJECTIVES (What to achieve)
- Transform Silver into fully autonomous business assistant
- Add accounting system (Odoo) integration
- Integrate all major social platforms
- Implement business intelligence and audits
- Make system self-healing and production-ready

🔄 UPGRADE SILVER → GOLD
From Silver (Existing):
Filesystem + Gmail + WhatsApp watchers ✓
Email MCP server ✓
LinkedIn automation ✓
Basic scheduling ✓

To Gold (Add these):
Odoo Community - Self-hosted accounting ERP
Social Suite - Facebook + Instagram + Twitter (X)
Business Intelligence - Weekly audits, CEO briefings
Autonomy Engine - Ralph Wiggum loop
Error Recovery - Self-healing system
Enhanced Security - Audit logging, permissions

📋 GOLD TIER REQUIREMENTS CHECKLIST
PREREQUISITES:
[X] Silver Tier complete
[X] Branch: P3-Gold-Tier
[X] Odoo 19+ installed locally
[X] Social media developer accounts
[X] Enhanced Claude API access

TECH STACK ADDITIONS:
# New dependencies for Gold
"odoo-client-lib"     # Odoo JSON-RPC API
"facebook-sdk"        # Facebook Graph API
"instagram-api"       # Instagram Basic Display API
"tweepy"              # Twitter API v2
"sqlalchemy"          # Local database for audit
"redis"               # Task queue for autonomy
"requests"            # Enhanced API calls
"cryptography"        # Enhanced security

🔧 SPECIFIC TASKS FOR GOLD TIER
TASK 1: ODOO ACCOUNTING SYSTEM INTEGRATION
What to do:
1- Install Odoo Community Edition locally (Docker or direct install)
2- Create Odoo MCP server (odoo_mcp_server.py)
3- Set up these Odoo modules: Accounting, Invoicing, CRM, Project
4- Create integration for:
- Automatic invoice creation from emails/WhatsApp
- Payment tracking from bank transactions
- Expense categorization
- Tax calculations
- Financial reporting

Skills needed from .claude/skills/:
- odoo_integration (create if not exists)
- invoice_processor
- accounting_manager
- data_sync
- api_handler

Configuration:
- Odoo URL: http://localhost:8069
- Database: ai_employee_db
- Admin credentials in .env
- JSON-RPC API integration

ASK 2: SOCIAL MEDIA SUITE EXPANSION
What to do:

Facebook Integration:
Post to Facebook Pages
Schedule Facebook posts
Analyze post engagement
Respond to comments (auto-draft)

Instagram Integration:
Post images with captions
Instagram Stories (if API allows)
Hashtag optimization
Engagement analytics

Twitter (X) Integration:
Tweet posting
Thread creation
Tweet scheduling
Trend monitoring
Direct message handling

Create files:
facebook_manager.py
instagram_manager.py
twitter_manager.py
social_suite_orchestrator.py

Skills needed:
social_media_manager
content_scheduler
engagement_analyzer
hashtag_optimizer

TASK 3: BUSINESS INTELLIGENCE & AUDITS
What to do:

1. Weekly Business Audit:
Analyze all transactions (Odoo + bank)
Review task completion rates
Calculate ROI on automation
Identify bottlenecks

2. CEO Briefing Generation:
Automatic Monday morning report
Revenue vs targets
Cash flow analysis
Team productivity (if multiple agents)
Recommendations

3. Predictive Analytics:
Cash flow forecasting
Busy period prediction
Client payment behavior
Resource allocation suggestions

- Create files:
business_auditor.py
ceo_briefing_generator.py
financial_analyzer.py
predictive_analytics.py

- Skills needed:
business_analyst
financial_reporter
data_visualizer
predictive_modeler


TASK 4: AUTONOMY ENGINE (Ralph Wiggum Loop)
What to do:
1. Implement Ralph Wiggum pattern for multi-step tasks
2. Create task persistence system
3. Add interruption recovery
4. Implement state saving/resuming

Key features:
Task checkpointing
Automatic retry on failure
Progress persistence
Deadlock detection
Priority task queuing

Create files:
ralph_wiggum_engine.py
task_persistence.py
autonomy_orchestrator.py

Skills needed:
task_orchestrator
error_handler
state_manager
queue_manager

TASK 5: ERROR RECOVERY & SELF-HEALING
What to do:

Graceful Degradation:

Component failure detection

Fallback mechanisms

Service degradation levels

Manual override protocols

Auto-Recovery:

Process monitoring

Automatic restarts

Data consistency checks

Backup restoration

Health Monitoring:

System vitals dashboard

Alert system (email/SMS)

Performance metrics

Capacity planning

Create files:

error_recovery_system.py

health_monitor.py

backup_manager.py

alert_system.py

Skills needed:

system_monitor

recovery_manager

alert_handler

backup_coordinator

TASK 6: ENHANCED SECURITY & AUDIT
What to do:

Comprehensive Audit Logging:

Every action logged (who, what, when)

Change tracking

Approval trails

Compliance reporting

Permission Boundaries:

Role-based access control

Action whitelisting/blacklisting

Time-based restrictions

Geographical restrictions

Data Protection:

Encryption at rest

Secure credential rotation

Data minimization

Privacy by design

Create files:

audit_logger.py

permission_manager.py

security_compliance.py

data_protection.py

Skills needed:

security_auditor

compliance_checker

encryption_manager

access_controller

TASK 7: CROSS-DOMAIN INTEGRATION
What to do:

Personal + Business Data Fusion:

Unified contact management

Shared calendar integration

Expense categorization (personal vs business)

Time tracking across domains

Intelligent Context Switching:

Detect personal vs business communications

Apply appropriate rules

Maintain separation where needed

Share insights where beneficial

Create files:

cross_domain_integrator.py

context_detector.py

unified_contact_manager.py

domain_orchestrator.py

Skills needed:

context_analyzer

domain_integrator

contact_manager

calendar_syncer

🏗️ ARCHITECTURE ENHANCEMENTS
Gold Tier Folder Structure:
text
AI_Employee_Vault/
├── Gold_Tier/
│   ├── Odoo_Integration/
│   │   ├── Invoices/
│   │   ├── Expenses/
│   │   ├── Reports/
│   │   └── Config/
│   ├── Social_Suite/
│   │   ├── Facebook/
│   │   ├── Instagram/
│   │   ├── Twitter/
│   │   └── Analytics/
│   ├── Business_Intelligence/
│   │   ├── Audits/
│   │   ├── Briefings/
│   │   ├── Forecasts/
│   │   └── Recommendations/
│   ├── Autonomy_Engine/
│   │   ├── Task_Queues/
│   │   ├── Checkpoints/
│   │   ├── State_Logs/
│   │   └── Recovery/
│   └── Security/
│       ├── Audit_Logs/
│       ├── Compliance/
│       ├── Backups/
│       └── Alerts/
🔗 MCP SERVERS TO CREATE
New MCP Servers for Gold:
Odoo MCP Server (odoo_mcp.py)

Invoice creation/management

Expense tracking

Financial reporting

CRM operations

Social Suite MCP (social_mcp.py)

Multi-platform posting

Engagement analytics

Comment management

Content scheduling

Business Intelligence MCP (business_mcp.py)

Report generation

Data analysis

Forecasting

Recommendation engine

Autonomy MCP (autonomy_mcp.py)

Task orchestration

State management

Recovery operations

Queue management

🤖 CLAUDE SKILLS TO CREATE/ENHANCE
New Skills for Gold Tier:
Accounting Skills:

create_invoice - Generate invoices in Odoo

track_expense - Categorize and log expenses

generate_financial_report - Create P&L, balance sheets

process_payment - Record payments and reconcile

Social Media Skills:

cross_post_content - Post to multiple platforms

analyze_engagement - Calculate ROI on posts

manage_comments - Draft responses to comments

optimize_schedule - Best times to post

Business Intelligence Skills:

generate_ceo_briefing - Weekly executive summary

identify_bottlenecks - Find process inefficiencies

forecast_revenue - Predict future income

recommend_actions - Suggest business improvements

Autonomy Skills:

multi_step_orchestration - Manage complex workflows

recover_from_failure - Handle errors gracefully

persist_task_state - Save/restore task progress

queue_optimization - Smart task prioritization

Security Skills:

audit_actions - Log and review all activities

rotate_credentials - Automatic key rotation

detect_anomalies - Spot unusual behavior

generate_compliance_report - Create audit trails

⚙️ CONFIGURATION UPDATES
Update .env file:
env
# GOLD TIER ADDITIONS

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_gold
ODOO_USERNAME=admin
ODOO_PASSWORD=your_odoo_password
ODOO_API_KEY=your_odoo_api_key

# Social Media APIs
FACEBOOK_ACCESS_TOKEN=your_fb_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCESS_TOKEN=your_ig_token
INSTAGRAM_BUSINESS_ID=your_business_id
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Business Intelligence
QUICKBOOKS_CLIENT_ID=your_qb_id  # Optional
QUICKBOOKS_CLIENT_SECRET=your_qb_secret
STRIPE_API_KEY=your_stripe_key  # Optional

# Autonomy Settings
MAX_AUTONOMY_LEVEL=high  # low/medium/high
AUTO_RECOVERY_ENABLED=true
MAX_RETRY_ATTEMPTS=3
TASK_TIMEOUT_SECONDS=3600

# Security
ENABLE_ENCRYPTION=true
AUDIT_LOG_RETENTION_DAYS=365
COMPLIANCE_MODE=strict
ALERT_EMAIL=your@email.com
ALERT_PHONE=+1234567890
📊 DATA FLOW FOR GOLD TIER
Sample Workflow: Client Invoice Processing
text
1. WhatsApp message: "Send invoice for Project X"
2. WhatsApp Watcher → Creates task in /Needs_Action/
3. Claude reads task → Uses Odoo skill to create invoice
4. Odoo MCP → Creates invoice draft in Odoo
5. Claude → Generates PDF, creates approval request
6. Human approves → Email MCP sends invoice
7. System → Logs to audit trail, updates Odoo status
8. Ralph Wiggum loop → Monitors for payment
9. Payment detected → Odoo updated, client notified
10. CEO Briefing → Includes in weekly revenue report

🎯 SUCCESS METRICS FOR GOLD TIER
Functional Requirements (Must have):
Odoo Community installed and running locally
Odoo MCP server operational
Facebook/Instagram/Twitter posting working
Weekly CEO briefing auto-generated
Ralph Wiggum loop implemented
Error recovery system functional
Comprehensive audit logging enabled
All new skills created in .claude/skills/

Performance Metrics:
System uptime: >99%
Task completion rate: >95%
Error recovery time: <5 minutes
Report generation: <2 minutes
API response time: <3 seconds

Security Requirements:
All credentials encrypted
Audit trail immutable
GDPR/Privacy compliance
Regular backup verification

📝 DOCUMENTATION REQUIREMENTS
Create these documents:
ARCHITECTURE_GOLD.md - System design and components
ODOO_SETUP_GUIDE.md - Step-by-step Odoo installation
SOCIAL_MEDIA_INTEGRATION.md - API setup for all platforms
BUSINESS_AUDIT_PROCESS.md - How audits work
ERROR_RECOVERY_PLAN.md - Recovery procedures
SECURITY_PROTOCOLS.md - Security measures
SKILLS_CATALOG.md - All available AI skills
API_REFERENCE.md - MCP server APIs

Include in documentation:
Architecture diagrams
Data flow charts
Security protocols
Troubleshooting guides
Performance benchmarks
Compliance checklists

🔍 TESTING REQUIREMENTS
Test Scenarios:
1. Odoo Integration Test:
Create invoice from email
Record payment from bank transaction
Generate financial report
Export data for tax purposes

2. Social Media Test:
Cross-post to 3 platforms
Schedule weekly content calendar
Analyze engagement metrics
Draft comment responses

3. Autonomy Test:
Complex multi-step task
Simulate failure and recovery
State persistence test
Priority queue management

4. Business Intelligence Test:
Generate CEO briefing
Identify process bottlenecks
Revenue forecasting
Cost optimization suggestions

5. Security Test:
Audit log verification
Credential rotation
Permission boundary testing
Data encryption validation

DEPLOYMENT STEPS
Phase 1: Preparation

# 1. Create Gold branch
git checkout P2-Silver-Tier
git checkout -b P3-Gold-Tier

# 2. Install new dependencies
pip install odoo-client-lib facebook-sdk instagram-api tweepy sqlalchemy redis cryptography

# 3. Set up Odoo (Docker recommended)
docker run -d -p 8069:8069 --name odoo -v odoo-data:/var/lib/odoo odoo:19.0

# 4. Configure social media APIs
#    - Create Facebook Developer App
#    - Set up Instagram Business Account
#    - Apply for Twitter Developer Access
Phase 2: Implementation

# 5. Run Gold setup script
python setup_gold.py

# 6. Update .env with new credentials

# 7. Start enhanced orchestrator
python orchestrator_gold.py

# 8. Test each component
python test_gold_system.py
Phase 3: Validation
bash
# 9. Run comprehensive tests
python run_gold_tests.py --all

# 10. Generate documentation
python generate_docs.py --tier gold

# 11. Performance benchmarking
python benchmark_gold.py

# 12. Security audit
python security_audit.py --tier gold
⚠️ IMPORTANT NOTES FOR CLAUDE CLI
Working Guidelines:
1. DO NOT DELETE SILVER CODE - Enhance and extend only
2. USE EXISTING SKILLS - Check .claude/skills/ first
3. MAINTAIN BACKWARD COMPATIBILITY - Silver features must still work
4. FOLLOW SECURITY BEST PRACTICES - No hardcoded credentials
5. IMPLEMENT GRACEFUL DEGRADATION - If Gold feature fails, fall back to Silver
6. CREATE MODULAR CODE - Each component should be independent
7. ADD EXTENSIVE LOGGING - Debugging will be crucial
8. DOCUMENT EVERYTHING - Future maintenance depends on this

Priority Order:
1. Odoo integration (most important)
2. Ralph Wiggum autonomy engine
3. Error recovery system
4. Social media expansion
5. Business intelligence
6. Enhanced security
7. Documentation


🎉 COMPLETION CRITERIA
Gold Tier is complete when:
✅ Odoo Community is running with sample data
✅ All 3 new social platforms integrated
✅ CEO briefing generates automatically every Monday
✅ System recovers from simulated failures
✅ Audit logs capture every action
✅ Ralph Wiggum loop handles multi-day tasks
✅ All documentation created and updated
✅ System passes all test scenarios
✅ Branch P3-Gold-Tier is ready for merge

Claude CLI, you now have complete instructions for implementing Gold Tier. Start by creating the branch and setting up the enhanced architecture. Remember to work incrementally and test each component thoroughly. Use the existing skills and create new ones as needed. Make this a production-ready autonomous AI Employee! 

