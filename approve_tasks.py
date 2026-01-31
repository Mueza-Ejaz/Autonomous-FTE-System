#!/usr/bin/env python3
"""Script to approve pending tasks by moving them to the Approved folder."""

import os
import shutil
from pathlib import Path

def approve_pending_tasks():
    """Move all pending approval files to the Approved folder."""

    # Define folder paths
    pending_folder = Path("AI_Employee_Vault/Pending_Approval")
    approved_folder = Path("AI_Employee_Vault/Approved")

    # Create approved folder if it doesn't exist
    approved_folder.mkdir(parents=True, exist_ok=True)

    # Get all pending approval files
    pending_files = list(pending_folder.glob("APPROVAL_*.md"))

    if not pending_files:
        print("No pending approval files found.")
        return

    print(f"Found {len(pending_files)} pending approval files:")
    for file_path in pending_files:
        print(f"  - {file_path.name}")

    # Move each file to the Approved folder
    for file_path in pending_files:
        destination = approved_folder / file_path.name
        shutil.move(str(file_path), str(destination))
        print(f"✓ Moved {file_path.name} to Approved folder")

    print(f"\nAll {len(pending_files)} approval requests have been approved!")
    print(f"You can now run the tasks that require these approvals.")

if __name__ == "__main__":
    approve_pending_tasks()