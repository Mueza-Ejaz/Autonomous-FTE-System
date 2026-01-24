"""
Bronze Tier Setup Script
Run this first to set up the environment
"""
import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("Checking prerequisites...")

    checks = [
        ("Python 3.13+", "python --version"),
        ("Node.js v24+", "node --version"),
        ("Git", "git --version"),
        ("Claude CLI", "claude --version")
    ]

    all_ok = True
    for name, cmd in checks:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  OK {name}: {result.stdout.strip()}")
            else:
                print(f"  FAIL {name}: Not found")
                all_ok = False
        except:
            print(f"  FAIL {name}: Not found")
            all_ok = False

    return all_ok

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")

    packages = [
        "watchdog",
        "python-dotenv",
        "playwright",
        "google-generativeai"
    ]

    for package in packages:
        print(f"  Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package])

    # Install Playwright browsers
    print("  Installing Playwright browsers...")
    subprocess.run([sys.executable, "-m", "playwright", "install"])

def setup_vault():
    """Set up the Obsidian vault structure"""
    print("Setting up vault structure...")

    vault_path = Path("D:/Autonomous-FTE-System/AI_Employee_Vault")

    # Create main directories
    dirs = [
        vault_path,
        vault_path / "Config",
        vault_path / "Skills",
        vault_path / "Drop_Folder",  # For file watcher
        vault_path / "MCP_Servers"
    ]

    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")

    # Create .gitignore
    gitignore = vault_path / ".gitignore"
    gitignore.write_text("""
# Secrets
.env
*.key
*.pem
credentials.json
token.json

# System files
.DS_Store
Thumbs.db
__pycache__/
*.pyc

# Logs
logs/
*.log

# Temporary files
temp/
tmp/
    """)

    print("  Created .gitignore")

def create_environment_file():
    """Create .env file template"""
    print("Creating environment template...")

    env_template = """# AI Employee Configuration
# NEVER commit this file to Git!

# Claude Configuration
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet

# Paths
VAULT_PATH=D:/Autonomous-FTE-System/AI_Employee_Vault
DROP_FOLDER=D:/Autonomous-FTE-System/AI_Employee_Vault/Drop_Folder

# System Settings
DRY_RUN=true
CHECK_INTERVAL=60
MAX_ITERATIONS=5

# Security
ENCRYPTION_KEY=your_encryption_key_here

# Add your API keys below:
# GMAIL_API_KEY=
# BANK_API_TOKEN=
# WHATSAPP_SESSION_PATH=
"""

    env_file = Path("D:/Autonomous-FTE-System/.env")
    env_file.write_text(env_template)

    print(f"  Created: {env_file}")
    print("  WARNING: Fill in your actual API keys!")

def setup_git():
    """Initialize Git repository"""
    print("Setting up Git...")

    repo_path = Path("D:/Autonomous-FTE-System")

    # Initialize if not already a repo
    if not (repo_path / ".git").exists():
        subprocess.run(["git", "init"], cwd=repo_path)
        print("  Initialized Git repository")

    # Create bronze tier branch
    subprocess.run(["git", "checkout", "-b", "P1-Bronze-Tier"], cwd=repo_path)
    print("  Created and switched to branch: P1-Bronze-Tier")

def main():
    print("=" * 60)
    print("Personal AI Employee - Bronze Tier Setup")
    print("=" * 60)

    # Check prerequisites
    if not check_prerequisites():
        print("\nSome prerequisites are missing.")
        print("Please install them before continuing.")
        return

    # Install dependencies
    install_dependencies()

    # Setup vault
    setup_vault()

    # Create environment file
    create_environment_file()

    # Setup Git
    setup_git()

    print("\n" + "=" * 60)
    print("Bronze Tier Setup Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Edit D:/Autonomous-FTE-System/.env and add your API keys")
    print("2. Review the created files in AI_Employee_Vault")
    print("3. Run: python orchestrator.py")
    print("4. Drop files in Drop_Folder to test the system")
    print("\nYour branch: P1-Bronze-Tier")
    print("All work is isolated in this branch.")

if __name__ == "__main__":
    main()