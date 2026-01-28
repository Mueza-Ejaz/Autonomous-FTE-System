# Personal AI Employee - Bronze Tier

## Overview
This is the Bronze Tier implementation of the Autonomous AI Employee system. It provides basic automation capabilities with one watcher, Claude Code integration as primary AI, Gemini API as fallback, and file-based task management.

## Features
- ✅ File system watcher for automatic task creation
- ✅ Claude Code integration for task processing (primary AI)
- ✅ Gemini API fallback when Claude unavailable
- ✅ Obsidian vault as knowledge base and dashboard
- ✅ Basic human-in-the-loop approval system
- ✅ Automated logging and monitoring
- ✅ Skill-based task execution

## Directory Structure
D:/Autonomous-FTE-System/
├── AI_Employee_Vault/ # Obsidian vault
│ ├── Dashboard.md # Live status dashboard
│ ├── Company_Handbook.md # Rules and guidelines
│ ├── Needs_Action/ # New tasks detected
│ ├── Plans/ # Task plans created by Claude
│ ├── Pending_Approval/ # Actions needing approval
│ ├── Approved/ # Approved actions
│ ├── Rejected/ # Rejected actions
│ ├── Done/ # Completed tasks
│ ├── Logs/ # System logs
│ └── Skills/ # Agent skills
├── .claude/skills/ # Claude skills directory
├── orchestrator.py # Main coordination script
├── filesystem_watcher.py # File watcher
└── setup_bronze.py # Setup script


## Setup Instructions

1. **Run the setup script:**
   ```bash
   python setup_bronze.py

2. Configure environment variables:
- Edit D:/Autonomous-FTE-System/.env
- Add your Claude API key and other credentials

3. Start the system:
# Terminal 1 - Start file watcher
python filesystem_watcher.py

# Terminal 2 - Start orchestrator
python orchestrator.py

4. Test the system:
- Drop a file in AI_Employee_Vault/Drop_Folder/
- Watch Claude process it automatically
- Check Dashboard.md for updates

Available Skills:
The system can use skills from D:\Autonomous-FTE-System\.claude\skills:
- file_processor: Read and write files
- text_analyzer: Analyze text content
- task_planner: Create detailed task plans
- email_drafter: Draft email responses
- data_extractor: Extract structured data

How It Works:
Detection: File watcher monitors Drop_Folder
Task Creation: Creates .md file in Needs_Action
Processing: Orchestrator triggers Claude to process
Planning: Claude creates plan in /Plans/
Approval: If needed, creates approval request
Execution: After approval, actions are taken
Completion: Files moved to /Done/, dashboard updated

Bronze Tier Requirements Met:
One watcher script (File System Watcher)
Basic task processing with Claude Code
One MCP server (filesystem built-in)
Dashboard.md updates automatically
All AI functionality as Agent Skills
Human-in-the-loop for approvals

Next Steps (Silver Tier):
Add Gmail and WhatsApp watchers
Implement email sending via MCP
Add scheduling capabilities
Create LinkedIn automation
Enhance approval workflows