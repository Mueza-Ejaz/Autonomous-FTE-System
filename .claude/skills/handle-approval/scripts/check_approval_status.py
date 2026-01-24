#!/usr/bin/env python3
"""
check_approval_status.py

Scans approval folders and generates a status report.
Used by the handle-approval skill to monitor approval workflow.

Usage:
    python check_approval_status.py [--json] [--vault-path PATH]

Options:
    --json          Output as JSON (default: human-readable)
    --vault-path    Path to Obsidian vault (default: current directory parent)

Output:
    Reports on pending, approved, rejected, and expired approvals.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import re


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown file."""
    if not content.startswith('---'):
        return {}

    try:
        # Find the second ---
        end_index = content.find('---', 3)
        if end_index == -1:
            return {}

        frontmatter_text = content[3:end_index].strip()

        # Simple YAML parser (basic key: value pairs)
        metadata = {}
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

        return metadata
    except Exception as e:
        print(f"Warning: Error parsing frontmatter: {e}", file=sys.stderr)
        return {}


def is_expired(expires_str: str) -> bool:
    """Check if approval has expired."""
    if not expires_str:
        return False

    try:
        # Parse ISO 8601 timestamp
        expires_dt = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
        now_dt = datetime.now(timezone.utc)
        return now_dt > expires_dt
    except Exception as e:
        print(f"Warning: Could not parse expiration time '{expires_str}': {e}", file=sys.stderr)
        return False


def get_approval_age(created_str: str) -> str:
    """Calculate how long ago the approval was created."""
    if not created_str:
        return "unknown"

    try:
        created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
        now_dt = datetime.now(timezone.utc)
        delta = now_dt - created_dt

        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            days = int(hours / 24)
            return f"{days}d ago"
    except Exception:
        return "unknown"


def scan_folder(folder_path: Path) -> List[Dict[str, Any]]:
    """Scan a folder for approval files and extract metadata."""
    if not folder_path.exists():
        return []

    approvals = []

    for file_path in folder_path.glob("APPROVAL_*.md"):
        try:
            content = file_path.read_text(encoding='utf-8')
            metadata = parse_frontmatter(content)

            # Extract action summary (first heading after frontmatter)
            summary_match = re.search(r'## Action Summary\s+(.+?)(?:\n|$)', content)
            summary = summary_match.group(1).strip() if summary_match else "No summary"

            approval_info = {
                'filename': file_path.name,
                'filepath': str(file_path),
                'action': metadata.get('action', 'unknown'),
                'priority': metadata.get('priority', 'normal'),
                'created': metadata.get('created', ''),
                'expires': metadata.get('expires', ''),
                'status': metadata.get('status', 'unknown'),
                'summary': summary,
                'age': get_approval_age(metadata.get('created', '')),
                'is_expired': is_expired(metadata.get('expires', ''))
            }

            approvals.append(approval_info)
        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)

    return approvals


def generate_report(vault_path: Path) -> Dict[str, Any]:
    """Generate comprehensive approval status report."""

    pending_folder = vault_path / 'Pending_Approval'
    approved_folder = vault_path / 'Approved'
    rejected_folder = vault_path / 'Rejected'

    # Scan all folders
    pending = scan_folder(pending_folder)
    approved = scan_folder(approved_folder)
    rejected = scan_folder(rejected_folder)

    # Separate expired from pending
    expired = [a for a in pending if a['is_expired']]
    active_pending = [a for a in pending if not a['is_expired']]

    # Sort by priority and age
    priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
    active_pending.sort(key=lambda x: (priority_order.get(x['priority'], 4), x['created']))

    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'vault_path': str(vault_path),
        'summary': {
            'pending': len(active_pending),
            'approved': len(approved),
            'rejected': len(rejected),
            'expired': len(expired)
        },
        'pending_approvals': active_pending,
        'awaiting_execution': approved,
        'recently_rejected': rejected,
        'expired_approvals': expired
    }

    return report


def print_human_readable(report: Dict[str, Any]) -> None:
    """Print report in human-readable format."""
    print("\n" + "="*70)
    print("  APPROVAL STATUS REPORT")
    print("="*70)
    print(f"Generated: {report['timestamp']}")
    print(f"Vault: {report['vault_path']}")
    print()

    summary = report['summary']
    print(f"📊 SUMMARY")
    print(f"   Pending Approval: {summary['pending']}")
    print(f"   Awaiting Execution: {summary['approved']}")
    print(f"   Recently Rejected: {summary['rejected']}")
    print(f"   Expired: {summary['expired']}")
    print()

    # Pending Approvals
    if report['pending_approvals']:
        print("⏳ PENDING APPROVALS (Need Human Decision)")
        print("-" * 70)
        for approval in report['pending_approvals']:
            priority_emoji = {
                'urgent': '🔴',
                'high': '🟠',
                'normal': '🟢',
                'low': '🔵'
            }.get(approval['priority'], '⚪')

            print(f"{priority_emoji} [{approval['action'].upper()}] {approval['summary']}")
            print(f"   File: {approval['filename']}")
            print(f"   Age: {approval['age']} | Priority: {approval['priority']}")
            print()
    else:
        print("✅ No pending approvals\n")

    # Awaiting Execution
    if report['awaiting_execution']:
        print("🚀 AWAITING EXECUTION (Approved, Not Yet Executed)")
        print("-" * 70)
        for approval in report['awaiting_execution']:
            print(f"   [{approval['action'].upper()}] {approval['summary']}")
            print(f"   File: {approval['filename']}")
            print()
    else:
        print("✅ No approved actions waiting for execution\n")

    # Expired
    if report['expired_approvals']:
        print("⏰ EXPIRED APPROVALS (No Decision Made in Time)")
        print("-" * 70)
        for approval in report['expired_approvals']:
            print(f"   [{approval['action'].upper()}] {approval['summary']}")
            print(f"   File: {approval['filename']}")
            print(f"   Created: {approval['age']}")
            print()
    else:
        print("✅ No expired approvals\n")

    # Recently Rejected
    if report['recently_rejected']:
        print("❌ RECENTLY REJECTED")
        print("-" * 70)
        for approval in report['recently_rejected'][:5]:  # Show last 5
            print(f"   [{approval['action'].upper()}] {approval['summary']}")
            print(f"   File: {approval['filename']}")
            print()

    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Check approval workflow status"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Output as JSON instead of human-readable format"
    )
    parser.add_argument(
        '--vault-path',
        type=str,
        default=None,
        help="Path to Obsidian vault (default: auto-detect)"
    )

    args = parser.parse_args()

    # Determine vault path
    if args.vault_path:
        vault_path = Path(args.vault_path)
    else:
        # Assume script is in .claude/skills/handle-approval/scripts/
        # So vault is 4 levels up + Vault directory
        script_dir = Path(__file__).parent
        vault_path = script_dir.parent.parent.parent.parent / 'Vault'

    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}", file=sys.stderr)
        sys.exit(1)

    # Generate report
    report = generate_report(vault_path)

    # Output
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_readable(report)


if __name__ == '__main__':
    main()
