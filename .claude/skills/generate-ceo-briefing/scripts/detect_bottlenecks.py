#!/usr/bin/env python3
"""
detect_bottlenecks.py

Identifies process, financial, and communication bottlenecks for CEO Briefing.

Usage:
    python detect_bottlenecks.py
    python detect_bottlenecks.py --category financial
    python detect_bottlenecks.py --min-severity high
    python detect_bottlenecks.py --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re


class BottleneckDetector:
    """Detects bottlenecks across process, financial, and communication dimensions."""

    def __init__(self, vault_path: str = "Vault"):
        self.vault_path = Path(vault_path)
        self.today = datetime.now()

    def detect_all(self, min_severity: str = "low", category: str = "all") -> Dict[str, List[Dict]]:
        """Detect all bottlenecks across categories."""
        print("Detecting bottlenecks...")

        bottlenecks = {
            "process": [],
            "financial": [],
            "communication": [],
            "resource": []
        }

        if category in ["all", "process"]:
            print("  Analyzing process bottlenecks...")
            bottlenecks["process"] = self.detect_process_bottlenecks()

        if category in ["all", "financial"]:
            print("  Analyzing financial bottlenecks...")
            bottlenecks["financial"] = self.detect_financial_bottlenecks()

        if category in ["all", "communication"]:
            print("  Analyzing communication bottlenecks...")
            bottlenecks["communication"] = self.detect_communication_bottlenecks()

        if category in ["all", "resource"]:
            print("  Analyzing resource bottlenecks...")
            bottlenecks["resource"] = self.detect_resource_bottlenecks()

        # Filter by severity
        if min_severity != "low":
            bottlenecks = self._filter_by_severity(bottlenecks, min_severity)

        # Sort by severity
        for category in bottlenecks:
            bottlenecks[category] = sorted(
                bottlenecks[category],
                key=lambda x: self._severity_priority(x["severity"]),
                reverse=True
            )

        total_found = sum(len(b) for b in bottlenecks.values())
        print(f"\n✓ Found {total_found} bottlenecks")

        return bottlenecks

    def detect_process_bottlenecks(self) -> List[Dict]:
        """Detect process and task management bottlenecks."""
        bottlenecks = []

        # Load completed tasks
        done_folder = self.vault_path / "Done"
        if not done_folder.exists():
            return bottlenecks

        # Analyze tasks that took longer than expected
        for task_file in done_folder.glob("*.md"):
            task_data = self._parse_task_metadata(task_file)

            expected = task_data.get("expected_duration", 0)
            actual = task_data.get("actual_duration", 0)

            if expected > 0 and actual > expected * 1.5:
                delay = actual - expected

                # Classify severity
                if delay > expected:  # 100%+ delay
                    severity = "critical"
                elif delay > expected * 0.5:  # 50%+ delay
                    severity = "high"
                else:
                    severity = "medium"

                # Identify root cause
                root_cause = self._identify_root_cause(task_data)

                # Calculate impact
                impact = self._classify_impact(task_data)

                bottlenecks.append({
                    "type": "process_delay",
                    "task": task_data.get("title", task_file.stem),
                    "expected": expected,
                    "actual": actual,
                    "delay": delay,
                    "delay_percentage": int((delay / expected) * 100),
                    "severity": severity,
                    "impact": impact,
                    "root_cause": root_cause,
                    "recommendation": self._recommend_process_fix(root_cause)
                })

        return bottlenecks

    def detect_financial_bottlenecks(self) -> List[Dict]:
        """Detect financial bottlenecks and issues."""
        bottlenecks = []

        # Load accounting data
        accounting_file = self.vault_path / "Accounting" / "Current_Month.md"
        if not accounting_file.exists():
            return bottlenecks

        content = accounting_file.read_text(encoding='utf-8')

        # Check for overdue invoices
        overdue_invoices = self._parse_overdue_invoices(content)
        if overdue_invoices["count"] > 0:
            severity = "high" if overdue_invoices["total"] > 1000 else "medium"
            bottlenecks.append({
                "type": "overdue_invoices",
                "severity": severity,
                "count": overdue_invoices["count"],
                "total": overdue_invoices["total"],
                "average_days": overdue_invoices["average_days"],
                "description": f"{overdue_invoices['count']} invoices overdue",
                "impact": f"${overdue_invoices['total']:.2f} cash flow impact",
                "recommendation": "Follow up on overdue invoices immediately. Consider implementing stricter payment terms."
            })

        # Check for budget overruns
        budget_overruns = self._check_budget_overruns(content)
        for overrun in budget_overruns:
            bottlenecks.append({
                "type": "budget_overrun",
                "severity": "medium",
                "category": overrun["category"],
                "budget": overrun["budget"],
                "actual": overrun["actual"],
                "overrun_amount": overrun["overrun"],
                "overrun_percentage": overrun["overrun_pct"],
                "description": f"{overrun['category']} expenses {overrun['overrun_pct']}% over budget",
                "impact": f"${overrun['overrun']:.2f} over budget",
                "recommendation": f"Review {overrun['category']} expenses and identify cost savings opportunities."
            })

        # Check for recurring failed payments
        failed_payments = self._identify_failed_payments(content)
        if failed_payments:
            bottlenecks.append({
                "type": "failed_payments",
                "severity": "medium",
                "count": len(failed_payments),
                "description": f"{len(failed_payments)} failed payment attempts",
                "impact": "Vendor relationship risk, potential service disruption",
                "recommendation": "Review account balance and payment methods. Contact vendors to resolve."
            })

        return bottlenecks

    def detect_communication_bottlenecks(self) -> List[Dict]:
        """Detect communication bottlenecks (email, social media)."""
        bottlenecks = []

        # Check email response times
        email_data = self._analyze_email_performance()

        if email_data["avg_response_time"] > 48:
            bottlenecks.append({
                "type": "slow_email_response",
                "severity": "high",
                "avg_response_time": email_data["avg_response_time"],
                "target": 24,
                "description": f"Average email response time: {email_data['avg_response_time']:.1f} hours",
                "impact": "Client satisfaction at risk, potential business loss",
                "recommendation": "Set aside dedicated email processing time 2-3x daily. Use templates for common responses."
            })

        # Check for pending high-priority emails
        if email_data["pending_high_priority"] > 2:
            bottlenecks.append({
                "type": "pending_high_priority_emails",
                "severity": "critical",
                "count": email_data["pending_high_priority"],
                "description": f"{email_data['pending_high_priority']} high-priority emails pending",
                "impact": "Urgent matters not addressed, escalation risk",
                "recommendation": "Process high-priority emails immediately. Consider emergency response protocol."
            })

        # Check for email backlog
        if email_data["backlog_count"] > 20:
            bottlenecks.append({
                "type": "email_backlog",
                "severity": "medium",
                "count": email_data["backlog_count"],
                "description": f"{email_data['backlog_count']} emails in backlog",
                "impact": "Delayed responses, increased stress",
                "recommendation": "Schedule email clearing session. Implement inbox zero methodology."
            })

        # Check social media response rate
        social_data = self._analyze_social_response()
        if social_data["response_rate"] < 80 and social_data["mentions"] > 5:
            bottlenecks.append({
                "type": "low_social_engagement",
                "severity": "low",
                "response_rate": social_data["response_rate"],
                "mentions": social_data["mentions"],
                "description": f"Only responding to {social_data['response_rate']}% of social media mentions",
                "impact": "Missed community engagement opportunities",
                "recommendation": "Allocate 15 minutes daily to respond to comments/mentions across platforms."
            })

        return bottlenecks

    def detect_resource_bottlenecks(self) -> List[Dict]:
        """Detect resource constraint bottlenecks."""
        bottlenecks = []

        # Check task backlog growth
        task_data = self._analyze_task_backlog()
        if task_data["backlog_growing"]:
            bottlenecks.append({
                "type": "task_backlog_growth",
                "severity": "medium",
                "active_tasks": task_data["active"],
                "completed_last_month": task_data["completed_last_month"],
                "description": f"{task_data['active']} active tasks vs {task_data['completed_last_month']} completed last month",
                "impact": "Tasks accumulating faster than completion, capacity constraint",
                "recommendation": "Conduct task audit: cancel/delegate/defer low-priority items. Consider hiring support."
            })

        # Check for over-commitment
        if task_data["high_priority_count"] > 5:
            bottlenecks.append({
                "type": "over_commitment",
                "severity": "high",
                "high_priority_count": task_data["high_priority_count"],
                "description": f"{task_data['high_priority_count']} high-priority tasks simultaneously",
                "impact": "Diluted focus, increased stress, quality risk",
                "recommendation": "Reassess priorities. Focus on top 3 high-priority items. Defer or delegate others."
            })

        # Check for skill gaps (tasks taking much longer than expected)
        skill_gaps = self._identify_skill_gaps()
        for gap in skill_gaps:
            bottlenecks.append({
                "type": "skill_gap",
                "severity": "low",
                "area": gap["area"],
                "avg_delay": gap["avg_delay"],
                "description": f"{gap['area']} tasks consistently taking {gap['avg_delay']:.0f}% longer",
                "impact": "Reduced efficiency in specific area",
                "recommendation": f"Consider training or automation in {gap['area']}. Alternatively, delegate to specialist."
            })

        return bottlenecks

    # Helper methods

    def _parse_task_metadata(self, task_file: Path) -> Dict:
        """Parse task metadata from file."""
        try:
            content = task_file.read_text(encoding='utf-8')
            # Simplified - would parse YAML frontmatter
            return {
                "title": task_file.stem,
                "expected_duration": 3,  # Placeholder
                "actual_duration": 5,  # Placeholder
                "notes": content[:200]  # First 200 chars
            }
        except:
            return {}

    def _identify_root_cause(self, task_data: Dict) -> str:
        """Identify root cause of delay from task notes."""
        notes = task_data.get("notes", "").lower()

        if "waiting" in notes or "blocked" in notes:
            return "Waiting on external party"
        elif "unclear" in notes or "requirements" in notes:
            return "Unclear requirements"
        elif "time" in notes or "capacity" in notes:
            return "Insufficient capacity"
        elif "technical" in notes or "bug" in notes:
            return "Technical blocker"
        else:
            return "Unknown - review task notes"

    def _classify_impact(self, task_data: Dict) -> str:
        """Classify impact level of task delay."""
        priority = task_data.get("priority", "medium").lower()

        if priority == "high":
            return "High - Client/revenue impact"
        elif priority == "medium":
            return "Medium - Process efficiency"
        else:
            return "Low - Internal only"

    def _recommend_process_fix(self, root_cause: str) -> str:
        """Generate recommendation based on root cause."""
        recommendations = {
            "Waiting on external party": "Set clear deadlines with stakeholders. Follow up proactively. Build buffer time.",
            "Unclear requirements": "Implement requirement clarification checklist before starting tasks.",
            "Insufficient capacity": "Assess workload. Delegate or defer lower-priority tasks.",
            "Technical blocker": "Document blockers. Escalate if recurring. Consider technical consultation.",
            "Unknown - review task notes": "Add detailed notes during task execution to identify patterns."
        }
        return recommendations.get(root_cause, "Review task execution process")

    def _parse_overdue_invoices(self, content: str) -> Dict:
        """Parse overdue invoice information."""
        # Simplified - would parse invoice section
        return {
            "count": 0,
            "total": 0,
            "average_days": 0
        }

    def _check_budget_overruns(self, content: str) -> List[Dict]:
        """Check for budget overruns by category."""
        # Simplified - would compare actual vs budget
        return []

    def _identify_failed_payments(self, content: str) -> List[Dict]:
        """Identify failed payment attempts."""
        return []

    def _analyze_email_performance(self) -> Dict:
        """Analyze email performance metrics."""
        # Simplified - would analyze email data
        return {
            "avg_response_time": 24,
            "pending_high_priority": 0,
            "backlog_count": 5
        }

    def _analyze_social_response(self) -> Dict:
        """Analyze social media response rate."""
        return {
            "response_rate": 85,
            "mentions": 10
        }

    def _analyze_task_backlog(self) -> Dict:
        """Analyze task backlog."""
        active_folder = self.vault_path / "Tasks" / "Active"
        active_count = len(list(active_folder.glob("*.md"))) if active_folder.exists() else 0

        high_priority_count = 0  # Would count from metadata

        return {
            "active": active_count,
            "completed_last_month": 20,  # Placeholder
            "backlog_growing": active_count > 20,
            "high_priority_count": high_priority_count
        }

    def _identify_skill_gaps(self) -> List[Dict]:
        """Identify skill gaps from task performance."""
        return []

    def _filter_by_severity(self, bottlenecks: Dict, min_severity: str) -> Dict:
        """Filter bottlenecks by minimum severity."""
        severity_levels = ["low", "medium", "high", "critical"]
        min_level = severity_levels.index(min_severity)

        filtered = {}
        for category, items in bottlenecks.items():
            filtered[category] = [
                item for item in items
                if severity_levels.index(item["severity"]) >= min_level
            ]

        return filtered

    def _severity_priority(self, severity: str) -> int:
        """Convert severity to priority score for sorting."""
        return {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }.get(severity, 0)


def main():
    parser = argparse.ArgumentParser(description="Detect business bottlenecks for CEO Briefing")
    parser.add_argument("--category", choices=["all", "process", "financial", "communication", "resource"],
                        default="all", help="Bottleneck category to analyze (default: all)")
    parser.add_argument("--min-severity", choices=["low", "medium", "high", "critical"],
                        default="low", help="Minimum severity to report (default: low)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--vault", type=str, default="Vault", help="Path to Obsidian vault")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize detector
    detector = BottleneckDetector(vault_path=args.vault)

    # Run detection
    try:
        bottlenecks = detector.detect_all(min_severity=args.min_severity, category=args.category)

        if args.json:
            print(json.dumps(bottlenecks, indent=2))
        else:
            # Print formatted results
            print("\n" + "="*60)
            print("BOTTLENECK DETECTION RESULTS")
            print("="*60)

            for category, items in bottlenecks.items():
                if items:
                    print(f"\n{category.upper()} BOTTLENECKS ({len(items)}):")
                    for i, bottleneck in enumerate(items, 1):
                        severity_emoji = {
                            "critical": "🔴",
                            "high": "🟠",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(bottleneck["severity"], "⚪")

                        print(f"\n{i}. {severity_emoji} {bottleneck.get('description', 'N/A')} ({bottleneck['severity'].upper()})")
                        print(f"   Type: {bottleneck['type']}")
                        if "impact" in bottleneck:
                            print(f"   Impact: {bottleneck['impact']}")
                        if "recommendation" in bottleneck:
                            print(f"   Recommendation: {bottleneck['recommendation']}")

            total = sum(len(items) for items in bottlenecks.values())
            if total == 0:
                print("\n✅ No significant bottlenecks detected!")

            print("\n" + "="*60)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
