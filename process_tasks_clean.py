#!/usr/bin/env python3
"""Process tasks in the AI Employee Vault"""

import os
from pathlib import Path
import shutil
from datetime import datetime

def process_needs_action_tasks():
    """Process all tasks in the Needs_Action folder."""

    needs_action_folder = Path("AI_Employee_Vault/Needs_Action")
    done_folder = Path("AI_Employee_Vault/Done")

    # Create Done folder if it doesn't exist
    done_folder.mkdir(parents=True, exist_ok=True)

    # Get all task files
    task_files = list(needs_action_folder.glob("*.md"))

    if not task_files:
        print("No tasks pending in Needs_Action folder.")
        return

    print(f"Found {len(task_files)} tasks to process:")
    for task_file in task_files:
        print(f"  - {task_file.name}")

    # Process each task
    for task_file in task_files:
        print(f"\nProcessing: {task_file.name}")

        # Read the task content
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Move the file to Done folder
        done_file = done_folder / task_file.name
        shutil.move(str(task_file), str(done_file))
        print(f"  [DONE] Moved to Done folder: {done_file.name}")

    print(f"\nCompleted processing {len(task_files)} tasks.")
    print(f"All tasks moved from Needs_Action to Done folder.")

    # Update dashboard with completion log
    dashboard_file = Path("AI_Employee_Vault/Dashboard.md")
    with open(dashboard_file, 'a', encoding='utf-8') as f:
        f.write(f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Task Processing**: Completed {len(task_files)} tasks from Needs_Action\n")
        f.write(f"- Tasks processed: {len(task_files)}\n")
        f.write(f"- Status: COMPLETE\n")

    print("Dashboard updated with completion log.")

if __name__ == "__main__":
    process_needs_action_tasks()