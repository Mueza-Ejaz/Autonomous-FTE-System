#!/usr/bin/env python3
"""Simple script to move the remaining approval file."""

import os
import shutil
from pathlib import Path

# Move the social media approval to Approved folder
pending_file = Path("AI_Employee_Vault/Pending_Approval/APPROVAL_SOCIAL_MEDIA_GOLD_TIER_ANNOUNCEMENT_2026-01-30.md")
approved_folder = Path("AI_Employee_Vault/Approved")

# Create approved folder if it doesn't exist
approved_folder.mkdir(parents=True, exist_ok=True)

# Move the file
if pending_file.exists():
    destination = approved_folder / pending_file.name
    shutil.move(str(pending_file), str(destination))
    print(f"Successfully moved {pending_file.name} to Approved folder")
else:
    print(f"File {pending_file.name} does not exist in Pending_Approval folder")

print("Checking contents of Approved folder:")
for file in approved_folder.glob("APPROVAL_*.md"):
    print(f"- {file.name}")