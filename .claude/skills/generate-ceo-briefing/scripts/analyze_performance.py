#!/usr/bin/env python3
"""
analyze_performance.py

Collects data from all sources and calculates performance scores for CEO Briefing.

Usage:
    python analyze_performance.py --period weekly
    python analyze_performance.py --calculate-scores
    python analyze_performance.py --start 2026-01-01 --end 2026-01-07
    python analyze_performance.py --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import re


class PerformanceAnalyzer:
    """Analyzes business performance across financial, operational, social, and goal dimensions."""

    def __init__(self, vault_path: str = "Vault"):
        self.vault_path = Path(vault_path)
        self.today = datetime.now()

    def analyze(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                period: str = "weekly") -> Dict[str, Any]:
        """Main analysis method - collects all data and calculates scores."""

        # Determine date range
        if period == "weekly":
            end_date = self.today
            start_date = end_date - timedelta(days=7)
        elif start_date and end_date:
            pass  # Use provided dates
        else:
            raise ValueError("Must specify period='weekly' or provide start_date and end_date")

        print(f"Analyzing performance from {start_date.date()} to {end_date.date()}...")

        # Collect data from all sources
        financial_data = self.collect_financial_data(start_date, end_date)
        operational_data = self.collect_operational_data(start_date, end_date)
        email_data = self.collect_email_data(start_date, end_date)
        social_data = self.collect_social_data(start_date, end_date)
        goals_data = self.collect_goals_data()

        # Calculate scores
        scores = {
            "financial": self.calculate_financial_score(financial_data, goals_data.get("targets", {})),
            "operational": self.calculate_operational_score(operational_data, email_data, goals_data.get("targets", {})),
            "social": self.calculate_social_score(social_data, goals_data.get("targets", {})),
            "goals": self.calculate_goal_score(goals_data)
        }

        # Calculate overall score
        overall_score, overall_status = self.calculate_overall_score(scores)

        # Load historical data for trends
        trends = self.calculate_trends(scores)

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data": {
                "financial": financial_data,
                "operational": operational_data,
                "email": email_data,
                "social": social_data,
                "goals": goals_data
            },
            "scores": scores,
            "overall_score": overall_score,
            "overall_status": overall_status,
            "trends": trends,
            "generated": self.today.isoformat()
        }

    def collect_financial_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect financial data from manage-accounting skill output."""
        print("  Collecting financial data...")

        accounting_file = self.vault_path / "Accounting" / "Current_Month.md"

        if not accounting_file.exists():
            print(f"    Warning: {accounting_file} not found")
            return self._empty_financial_data()

        content = accounting_file.read_text(encoding='utf-8')

        # Parse transactions
        transactions = self._parse_transactions(content, start_date, end_date)

        # Calculate metrics
        weekly_revenue = sum(t["amount"] for t in transactions if t["type"] == "Revenue" and t["date"] >= start_date)
        weekly_expenses = sum(abs(t["amount"]) for t in transactions if t["type"] == "Expense" and t["date"] >= start_date)

        # MTD
        month_start = datetime(self.today.year, self.today.month, 1)
        mtd_revenue = sum(t["amount"] for t in transactions if t["type"] == "Revenue" and t["date"] >= month_start)
        mtd_expenses = sum(abs(t["amount"]) for t in transactions if t["type"] == "Expense" and t["date"] >= month_start)

        # Outstanding/overdue (would parse from invoice section)
        outstanding_total, outstanding_count, overdue_total, overdue_count = self._parse_invoices(content)

        # Identify subscriptions
        subscriptions = self._identify_subscriptions(transactions)

        print(f"    ✓ Revenue: ${weekly_revenue:.2f} (weekly), ${mtd_revenue:.2f} (MTD)")
        print(f"    ✓ Expenses: ${weekly_expenses:.2f} (weekly), ${mtd_expenses:.2f} (MTD)")

        return {
            "revenue": {
                "weekly": weekly_revenue,
                "mtd": mtd_revenue
            },
            "expenses": {
                "weekly": weekly_expenses,
                "mtd": mtd_expenses,
                "by_category": self._group_by_category(transactions, start_date)
            },
            "cash_flow": {
                "weekly": weekly_revenue - weekly_expenses,
                "mtd": mtd_revenue - mtd_expenses
            },
            "invoices": {
                "outstanding_total": outstanding_total,
                "outstanding_count": outstanding_count,
                "overdue_total": overdue_total,
                "overdue_count": overdue_count
            },
            "subscriptions": subscriptions
        }

    def collect_operational_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect operational data from process-tasks skill output."""
        print("  Collecting operational data...")

        done_folder = self.vault_path / "Done"
        active_folder = self.vault_path / "Tasks" / "Active"

        if not done_folder.exists():
            print(f"    Warning: {done_folder} not found")
            return self._empty_operational_data()

        # Count completed tasks in period
        completed_tasks = []
        if done_folder.exists():
            for task_file in done_folder.glob("*.md"):
                # Check file modification time or parse metadata
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if start_date <= mtime <= end_date:
                    task_data = self._parse_task_metadata(task_file)
                    completed_tasks.append(task_data)

        completed_count = len(completed_tasks)

        # Calculate average cycle time
        cycle_times = [t.get("actual_duration", 0) for t in completed_tasks if "actual_duration" in t]
        avg_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0

        # Count active and overdue tasks
        active_count = len(list(active_folder.glob("*.md"))) if active_folder.exists() else 0
        overdue_tasks = self._count_overdue_tasks(active_folder) if active_folder.exists() else {"high": 0, "medium": 0, "low": 0}

        # Completion rate
        total_tasks = completed_count + active_count
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0

        print(f"    ✓ Completed: {completed_count} tasks")
        print(f"    ✓ Completion rate: {completion_rate:.1f}%")
        print(f"    ✓ Overdue: {sum(overdue_tasks.values())} tasks")

        return {
            "tasks": {
                "completed_weekly": completed_count,
                "active": active_count,
                "completion_rate": completion_rate,
                "avg_cycle_time": avg_cycle_time,
                "overdue_count": sum(overdue_tasks.values()),
                "overdue_priority": overdue_tasks
            },
            "completed_tasks": completed_tasks
        }

    def collect_email_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect email performance data from process-emails skill output."""
        print("  Collecting email data...")

        done_folder = self.vault_path / "Done"

        if not done_folder.exists():
            return self._empty_email_data()

        # Find processed emails in period
        processed_emails = []
        for email_file in done_folder.glob("EMAIL_*.md"):
            mtime = datetime.fromtimestamp(email_file.stat().st_mtime)
            if start_date <= mtime <= end_date:
                email_data = self._parse_email_metadata(email_file)
                processed_emails.append(email_data)

        processed_count = len(processed_emails)

        # Calculate average response time
        response_times = [e.get("response_time", 0) for e in processed_emails if "response_time" in e]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Response time breakdown
        breakdown = {
            "under_1h": sum(1 for t in response_times if t < 1),
            "1_to_4h": sum(1 for t in response_times if 1 <= t < 4),
            "4_to_24h": sum(1 for t in response_times if 4 <= t < 24),
            "over_24h": sum(1 for t in response_times if t >= 24)
        }

        # Count pending high-priority
        needs_action_folder = self.vault_path / "Needs_Action"
        pending_high_priority = 0
        if needs_action_folder.exists():
            for email_file in needs_action_folder.glob("EMAIL_*.md"):
                metadata = self._parse_email_metadata(email_file)
                if metadata.get("priority") == "high":
                    pending_high_priority += 1

        print(f"    ✓ Processed: {processed_count} emails")
        print(f"    ✓ Avg response time: {avg_response_time:.1f} hours")
        print(f"    ✓ Pending high-priority: {pending_high_priority}")

        return {
            "processed_weekly": processed_count,
            "avg_response_time": avg_response_time,
            "pending_high_priority": pending_high_priority,
            "response_time_breakdown": breakdown
        }

    def collect_social_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect social media data from all social media skills."""
        print("  Collecting social media data...")

        social_folder = self.vault_path / "Social_Media"

        if not social_folder.exists():
            print(f"    Warning: {social_folder} not found")
            return self._empty_social_data()

        platforms = ["LinkedIn", "Facebook", "Instagram", "Twitter"]
        platform_data = {}

        for platform in platforms:
            metrics_file = social_folder / platform / "metrics.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    platform_data[platform.lower()] = json.load(f)
                print(f"    ✓ {platform}: {platform_data[platform.lower()].get('posts_published', 0)} posts")
            else:
                print(f"    ⚠ {platform}: metrics.json not found")

        # Aggregate summary
        summary = self._aggregate_social_summary(platform_data)

        return {
            **platform_data,
            "summary": summary
        }

    def collect_goals_data(self) -> Dict[str, Any]:
        """Collect goals and targets from Business_Goals.md."""
        print("  Collecting business goals data...")

        goals_file = self.vault_path / "Business_Goals.md"

        if not goals_file.exists():
            print(f"    Warning: {goals_file} not found")
            return {"targets": {}, "goals": []}

        content = goals_file.read_text(encoding='utf-8')

        # Parse targets
        targets = self._parse_targets(content)

        # Parse individual goals
        goals = self._parse_goals(content)

        print(f"    ✓ Found {len(goals)} goals")

        return {
            "targets": targets,
            "goals": goals
        }

    def calculate_financial_score(self, financial_data: Dict, targets: Dict) -> int:
        """Calculate financial performance score (0-100)."""
        score = 0

        # Revenue performance (40 points)
        revenue_target = targets.get("revenue_monthly", 10000)
        revenue_pct = financial_data["revenue"]["mtd"] / revenue_target
        if revenue_pct >= 0.9:
            score += 40
        elif revenue_pct >= 0.7:
            score += int(40 * revenue_pct / 0.9)

        # Expense control (30 points)
        expense_budget = targets.get("expense_budget", 6000)
        expense_pct = financial_data["expenses"]["mtd"] / expense_budget
        if expense_pct <= 1.0:
            score += 30
        elif expense_pct <= 1.2:
            score += int(30 * (1.2 - expense_pct) / 0.2)

        # Cash flow positive (20 points)
        if financial_data["cash_flow"]["mtd"] > 0:
            score += 20
        elif financial_data["cash_flow"]["mtd"] > -revenue_target * 0.1:
            score += 10

        # No overdue invoices (10 points)
        if financial_data["invoices"]["overdue_count"] == 0:
            score += 10
        elif financial_data["invoices"]["overdue_count"] <= 2:
            score += 5

        return min(score, 100)

    def calculate_operational_score(self, operational_data: Dict, email_data: Dict, targets: Dict) -> int:
        """Calculate operational performance score (0-100)."""
        score = 0

        # Task completion rate (40 points)
        if operational_data["tasks"]["completion_rate"] >= 90:
            score += 40
        elif operational_data["tasks"]["completion_rate"] >= 70:
            score += int(40 * operational_data["tasks"]["completion_rate"] / 100)

        # Task cycle time (30 points)
        avg_cycle_time = operational_data["tasks"].get("avg_cycle_time", 0)
        target_cycle_time = targets.get("avg_cycle_time", 3)
        if avg_cycle_time > 0:
            if avg_cycle_time <= target_cycle_time:
                score += 30
            elif avg_cycle_time <= target_cycle_time * 1.5:
                ratio = avg_cycle_time / target_cycle_time
                score += int(30 * (1.5 - ratio) / 0.5)

        # Email response time (20 points)
        email_target = targets.get("email_response_target", 24)
        if email_data["avg_response_time"] < email_target:
            score += 20
        elif email_data["avg_response_time"] < email_target * 2:
            ratio = email_data["avg_response_time"] / email_target
            score += int(20 * (2 - ratio))

        # No overdue high-priority (10 points)
        if (operational_data["tasks"]["overdue_priority"]["high"] == 0 and
                email_data["pending_high_priority"] == 0):
            score += 10
        elif operational_data["tasks"]["overdue_priority"]["high"] <= 1:
            score += 5

        return min(score, 100)

    def calculate_social_score(self, social_data: Dict, targets: Dict) -> int:
        """Calculate social media performance score (0-100)."""
        if not social_data.get("summary"):
            return None

        score = 0
        summary = social_data["summary"]

        # Posts published vs schedule (25 points)
        posts_target = targets.get("social_posts_per_week", 7)
        posts_ratio = summary["total_posts"] / posts_target if posts_target > 0 else 0
        if posts_ratio >= 0.9:
            score += 25
        elif posts_ratio >= 0.7:
            score += int(25 * posts_ratio / 0.9)

        # Engagement rate (40 points)
        engagement_target = targets.get("social_engagement_target", 0.03)
        if summary["engagement_rate"] >= engagement_target:
            score += 40
        elif summary["engagement_rate"] >= engagement_target * 0.7:
            ratio = summary["engagement_rate"] / engagement_target
            score += int(40 * ratio)

        # Follower growth (20 points)
        if summary["follower_growth"] > 0:
            score += 20

        # Engagement exists (15 points)
        if summary["total_engagement"] > 0:
            score += 15

        return min(score, 100)

    def calculate_goal_score(self, goals_data: Dict) -> Optional[int]:
        """Calculate goal achievement score (0-100)."""
        goals = goals_data.get("goals", [])
        if not goals:
            return None

        total_progress = 0
        total_weight = 0

        for goal in goals:
            weight = goal.get("priority_weight", 1.0)

            if goal["status"] == "on_track":
                goal_score = 100
            elif goal["status"] == "at_risk":
                goal_score = 70
            else:  # behind
                goal_score = max(goal.get("progress_percentage", 0), 40)

            total_progress += goal_score * weight
            total_weight += weight

        return int(total_progress / total_weight) if total_weight > 0 else 0

    def calculate_overall_score(self, scores: Dict) -> tuple:
        """Calculate overall business health score and status."""
        valid_scores = [s for s in scores.values() if s is not None]

        if not valid_scores:
            return None, "insufficient_data"

        overall = sum(valid_scores) / len(valid_scores)

        if overall >= 90:
            status = "excellent"
        elif overall >= 75:
            status = "good"
        elif overall >= 60:
            status = "fair"
        else:
            status = "needs_attention"

        return int(overall), status

    def calculate_trends(self, current_scores: Dict) -> Dict:
        """Calculate trends by comparing to last week's briefing."""
        # This would load the previous briefing and compare scores
        # For now, return placeholder
        return {
            "financial": "→",
            "operational": "→",
            "social": "→",
            "goals": "→"
        }

    # Helper methods for parsing

    def _parse_transactions(self, content: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Parse transactions from accounting file."""
        transactions = []
        # Simplified parsing - in practice would be more robust
        # Pattern: ### YYYY-MM-DD - [Description]
        pattern = r'###\s+(\d{4}-\d{2}-\d{2})\s+-\s+(.+)'
        for match in re.finditer(pattern, content):
            date_str = match.group(1)
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= date <= end_date:
                # Parse transaction details (simplified)
                transactions.append({
                    "date": date,
                    "description": match.group(2),
                    "amount": 0,  # Would parse from following lines
                    "type": "Revenue",  # Would determine from metadata
                    "category": "Unknown"
                })
        return transactions

    def _parse_invoices(self, content: str) -> tuple:
        """Parse invoice information from accounting file."""
        # Simplified - would parse invoice section
        return 0, 0, 0, 0  # outstanding_total, outstanding_count, overdue_total, overdue_count

    def _identify_subscriptions(self, transactions: List[Dict]) -> List[Dict]:
        """Identify recurring subscriptions from transactions."""
        # Simplified - would use pattern matching
        return []

    def _group_by_category(self, transactions: List[Dict], start_date: datetime) -> Dict:
        """Group expenses by category."""
        categories = {}
        for t in transactions:
            if t["type"] == "Expense" and t["date"] >= start_date:
                category = t.get("category", "Uncategorized")
                categories[category] = categories.get(category, 0) + abs(t["amount"])
        return categories

    def _parse_task_metadata(self, task_file: Path) -> Dict:
        """Parse task metadata from task file."""
        content = task_file.read_text(encoding='utf-8')
        # Would parse YAML frontmatter
        return {
            "title": task_file.stem,
            "actual_duration": 3  # Placeholder
        }

    def _count_overdue_tasks(self, active_folder: Path) -> Dict:
        """Count overdue tasks by priority."""
        overdue = {"high": 0, "medium": 0, "low": 0}
        # Would parse each task and check due_date
        return overdue

    def _parse_email_metadata(self, email_file: Path) -> Dict:
        """Parse email metadata."""
        # Would parse YAML frontmatter
        return {
            "response_time": 12  # Placeholder (hours)
        }

    def _aggregate_social_summary(self, platform_data: Dict) -> Dict:
        """Aggregate social media summary across platforms."""
        total_posts = sum(p.get("posts_published", 0) for p in platform_data.values())
        total_engagement = sum(p.get("engagement", {}).get("total", 0) for p in platform_data.values())
        total_followers = sum(p.get("followers", {}).get("current", 0) for p in platform_data.values())
        follower_growth = sum(p.get("followers", {}).get("change", 0) for p in platform_data.values())

        engagement_rate = (total_engagement / (total_posts * total_followers) * 100) if (total_posts * total_followers) > 0 else 0

        return {
            "total_posts": total_posts,
            "total_engagement": total_engagement,
            "engagement_rate": engagement_rate,
            "follower_growth": follower_growth
        }

    def _parse_targets(self, content: str) -> Dict:
        """Parse targets from Business_Goals.md."""
        # Simplified parsing
        return {
            "revenue_monthly": 10000,
            "expense_budget": 6000,
            "email_response_target": 24,
            "social_posts_per_week": 7,
            "social_engagement_target": 0.03
        }

    def _parse_goals(self, content: str) -> List[Dict]:
        """Parse individual goals from Business_Goals.md."""
        # Simplified - would parse goal sections
        return []

    # Empty data structures

    def _empty_financial_data(self) -> Dict:
        return {
            "revenue": {"weekly": 0, "mtd": 0},
            "expenses": {"weekly": 0, "mtd": 0, "by_category": {}},
            "cash_flow": {"weekly": 0, "mtd": 0},
            "invoices": {"outstanding_total": 0, "outstanding_count": 0,
                         "overdue_total": 0, "overdue_count": 0},
            "subscriptions": []
        }

    def _empty_operational_data(self) -> Dict:
        return {
            "tasks": {
                "completed_weekly": 0,
                "active": 0,
                "completion_rate": 0,
                "avg_cycle_time": 0,
                "overdue_count": 0,
                "overdue_priority": {"high": 0, "medium": 0, "low": 0}
            },
            "completed_tasks": []
        }

    def _empty_email_data(self) -> Dict:
        return {
            "processed_weekly": 0,
            "avg_response_time": 0,
            "pending_high_priority": 0,
            "response_time_breakdown": {
                "under_1h": 0,
                "1_to_4h": 0,
                "4_to_24h": 0,
                "over_24h": 0
            }
        }

    def _empty_social_data(self) -> Dict:
        return {
            "summary": {
                "total_posts": 0,
                "total_engagement": 0,
                "engagement_rate": 0,
                "follower_growth": 0
            }
        }


def main():
    parser = argparse.ArgumentParser(description="Analyze business performance for CEO Briefing")
    parser.add_argument("--period", choices=["weekly", "custom"], default="weekly",
                        help="Analysis period (default: weekly)")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD) for custom period")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD) for custom period")
    parser.add_argument("--calculate-scores", action="store_true", help="Calculate scores only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--vault", type=str, default="Vault", help="Path to Obsidian vault")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = PerformanceAnalyzer(vault_path=args.vault)

    # Determine dates
    start_date = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end_date = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None

    # Run analysis
    try:
        results = analyzer.analyze(start_date=start_date, end_date=end_date, period=args.period)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Print formatted results
            print("\n" + "="*60)
            print("PERFORMANCE ANALYSIS RESULTS")
            print("="*60)
            print(f"\nPeriod: {results['period']['start']} to {results['period']['end']}")
            print(f"\nOverall Score: {results['overall_score']}/100 ({results['overall_status'].upper()})")
            print("\nDimension Scores:")
            for dimension, score in results['scores'].items():
                if score is not None:
                    print(f"  {dimension.capitalize():15} {score:3}/100")
                else:
                    print(f"  {dimension.capitalize():15}   N/A")

            print("\n" + "="*60)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
