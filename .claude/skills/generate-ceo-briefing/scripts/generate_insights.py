#!/usr/bin/env python3
"""
generate_insights.py

Generates proactive recommendations and insights for CEO Briefing.

Usage:
    python generate_insights.py
    python generate_insights.py --focus cost-optimization
    python generate_insights.py --min-savings 100
    python generate_insights.py --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import re


class InsightGenerator:
    """Generates proactive business recommendations across multiple categories."""

    def __init__(self, vault_path: str = "Vault"):
        self.vault_path = Path(vault_path)
        self.today = datetime.now()

    def generate_all(self, focus: str = "all", min_savings: float = 0) -> Dict[str, List[Dict]]:
        """Generate all recommendations."""
        print("Generating insights and recommendations...")

        insights = {
            "cost_optimization": [],
            "process_improvement": [],
            "growth_opportunity": [],
            "risk_alert": []
        }

        if focus in ["all", "cost-optimization"]:
            print("  Analyzing cost optimization opportunities...")
            insights["cost_optimization"] = self.generate_cost_optimizations(min_savings)

        if focus in ["all", "process-improvement"]:
            print("  Analyzing process improvements...")
            insights["process_improvement"] = self.generate_process_improvements()

        if focus in ["all", "growth"]:
            print("  Analyzing growth opportunities...")
            insights["growth_opportunity"] = self.generate_growth_opportunities()

        if focus in ["all", "risk"]:
            print("  Analyzing risk alerts...")
            insights["risk_alert"] = self.generate_risk_alerts()

        # Prioritize recommendations
        for category in insights:
            insights[category] = sorted(
                insights[category],
                key=lambda x: self._calculate_priority_score(x),
                reverse=True
            )

        total_found = sum(len(r) for r in insights.values())
        print(f"\n✓ Generated {total_found} recommendations")

        return insights

    def generate_cost_optimizations(self, min_savings: float = 0) -> List[Dict]:
        """Generate cost optimization recommendations."""
        optimizations = []

        # Subscription audit
        subscription_opportunities = self._audit_subscriptions()
        for opp in subscription_opportunities:
            if opp["annual_savings"] >= min_savings:
                optimizations.append(opp)

        # Budget overruns
        budget_opportunities = self._audit_budget_overruns()
        optimizations.extend(budget_opportunities)

        # Payment terms
        payment_opportunities = self._audit_payment_terms()
        optimizations.extend(payment_opportunities)

        return optimizations

    def generate_process_improvements(self) -> List[Dict]:
        """Generate process improvement recommendations."""
        improvements = []

        # Email management
        email_improvements = self._recommend_email_improvements()
        improvements.extend(email_improvements)

        # Task management
        task_improvements = self._recommend_task_improvements()
        improvements.extend(task_improvements)

        # Communication efficiency
        communication_improvements = self._recommend_communication_improvements()
        improvements.extend(communication_improvements)

        # Automation opportunities
        automation_opportunities = self._identify_automation_opportunities()
        improvements.extend(automation_opportunities)

        return improvements

    def generate_growth_opportunities(self) -> List[Dict]:
        """Generate growth opportunity recommendations."""
        opportunities = []

        # Social media growth
        social_opportunities = self._identify_social_growth()
        opportunities.extend(social_opportunities)

        # Revenue expansion
        revenue_opportunities = self._identify_revenue_opportunities()
        opportunities.extend(revenue_opportunities)

        # Efficiency gains
        efficiency_opportunities = self._identify_efficiency_gains()
        opportunities.extend(efficiency_opportunities)

        # Client expansion
        client_opportunities = self._identify_client_opportunities()
        opportunities.extend(client_opportunities)

        return opportunities

    def generate_risk_alerts(self) -> List[Dict]:
        """Generate risk alert recommendations."""
        risks = []

        # Financial risks
        financial_risks = self._identify_financial_risks()
        risks.extend(financial_risks)

        # Operational risks
        operational_risks = self._identify_operational_risks()
        risks.extend(operational_risks)

        # Goal risks
        goal_risks = self._identify_goal_risks()
        risks.extend(goal_risks)

        # Market/external risks
        external_risks = self._identify_external_risks()
        risks.extend(external_risks)

        return risks

    # Cost Optimization Methods

    def _audit_subscriptions(self) -> List[Dict]:
        """Audit subscriptions for unused or duplicate services."""
        opportunities = []

        # Load financial data
        accounting_file = self.vault_path / "Accounting" / "Current_Month.md"
        if not accounting_file.exists():
            return opportunities

        content = accounting_file.read_text(encoding='utf-8')
        subscriptions = self._identify_subscriptions(content)

        # Check each subscription
        for sub in subscriptions:
            # Rule 1: No activity in 30+ days
            last_activity = self._get_last_activity(sub["vendor"])
            if not last_activity or (self.today - last_activity).days >= 30:
                days_inactive = (self.today - last_activity).days if last_activity else 999

                opportunities.append({
                    "type": "unused_subscription",
                    "service": sub["vendor"],
                    "cost_monthly": sub["amount"],
                    "annual_savings": sub["amount"] * 12,
                    "issue": f"No activity in {days_inactive} days",
                    "alternative": self._suggest_alternative(sub["vendor"]),
                    "action": "Cancel subscription",
                    "priority": self._priority_from_savings(sub["amount"] * 12),
                    "effort": "Low"
                })

            # Rule 2: Duplicate functionality
            duplicate = self._check_duplicate(sub["vendor"], subscriptions)
            if duplicate:
                opportunities.append({
                    "type": "duplicate_subscription",
                    "service": sub["vendor"],
                    "cost_monthly": sub["amount"],
                    "annual_savings": sub["amount"] * 12,
                    "issue": f"Duplicate functionality with {duplicate}",
                    "action": f"Cancel one of: {sub['vendor']} or {duplicate}",
                    "priority": "Medium",
                    "effort": "Low"
                })

        return opportunities

    def _audit_budget_overruns(self) -> List[Dict]:
        """Identify budget overruns with optimization potential."""
        opportunities = []

        # Would analyze expense categories vs budget
        # Placeholder for now
        return opportunities

    def _audit_payment_terms(self) -> List[Dict]:
        """Identify opportunities to improve payment terms."""
        opportunities = []

        # Would analyze payment patterns
        # Placeholder for now
        return opportunities

    # Process Improvement Methods

    def _recommend_email_improvements(self) -> List[Dict]:
        """Recommend email management improvements."""
        improvements = []

        # Analyze email performance
        email_data = self._get_email_metrics()

        # Rule: High response time
        if email_data["avg_response_time"] > 24:
            delay = email_data["avg_response_time"] - 24

            improvements.append({
                "type": "email_response_time",
                "area": "Email Management",
                "current": f"{email_data['avg_response_time']:.1f} hours avg response",
                "target": "24 hours",
                "issue": f"Response time {delay:.1f} hours over target",
                "recommendation": "Schedule dedicated email processing blocks 2-3x daily (9 AM, 2 PM, 5 PM)",
                "expected_benefit": "Reduce response time by 30-50%, improve client satisfaction",
                "investment": "30 minutes per processing block",
                "priority": "High" if delay > 24 else "Medium",
                "effort": "Low"
            })

        # Rule: High email volume suggests FAQ need
        if email_data["weekly_volume"] > 50:
            improvements.append({
                "type": "email_volume",
                "area": "Email Management",
                "current": f"{email_data['weekly_volume']} emails/week",
                "issue": "High email volume with likely repeated questions",
                "recommendation": "Create FAQ document for common questions. Share proactively with clients.",
                "expected_benefit": "Reduce email volume by 20-30%, save 3-5 hours/week",
                "investment": "2-3 hours to create FAQ",
                "priority": "Medium",
                "effort": "Medium"
            })

        return improvements

    def _recommend_task_improvements(self) -> List[Dict]:
        """Recommend task management improvements."""
        improvements = []

        # Analyze task metrics
        task_data = self._get_task_metrics()

        # Rule: Low completion rate
        if task_data["completion_rate"] < 90:
            improvements.append({
                "type": "task_completion",
                "area": "Task Management",
                "current": f"{task_data['completion_rate']:.0f}% completion rate",
                "target": "90%+",
                "issue": "Task completion rate below target",
                "recommendation": "Implement weekly task review: identify blockers, reprioritize, delegate or cancel low-value tasks",
                "expected_benefit": "Increase completion rate to 90%+, reduce task backlog, lower stress",
                "investment": "30 minutes weekly review",
                "priority": "Medium",
                "effort": "Low"
            })

        # Rule: Long cycle times
        if task_data["avg_cycle_time"] > 5:
            improvements.append({
                "type": "task_cycle_time",
                "area": "Task Management",
                "current": f"{task_data['avg_cycle_time']:.1f} days avg cycle time",
                "target": "3-5 days",
                "issue": "Tasks taking longer than optimal",
                "recommendation": "Break large tasks into smaller milestones. Use time-boxing to prevent scope creep.",
                "expected_benefit": f"Reduce cycle time by {(task_data['avg_cycle_time'] - 3) / task_data['avg_cycle_time'] * 100:.0f}%",
                "investment": "Better task planning (10 min per task)",
                "priority": "Medium",
                "effort": "Low"
            })

        return improvements

    def _recommend_communication_improvements(self) -> List[Dict]:
        """Recommend communication improvements."""
        # Placeholder
        return []

    def _identify_automation_opportunities(self) -> List[Dict]:
        """Identify tasks that could be automated."""
        opportunities = []

        # Analyze recurring tasks
        recurring = self._find_recurring_tasks()

        for task in recurring:
            if task["frequency"] >= 4 and task["time_spent"] >= 2:  # 4+ times/month, 2+ hours total
                opportunities.append({
                    "type": "automation",
                    "area": "Process Automation",
                    "current": f"Manual task '{task['name']}' performed {task['frequency']}x/month",
                    "issue": f"Spending {task['time_spent']} hours/month on repetitive task",
                    "recommendation": f"Automate '{task['name']}' using: {self._suggest_automation(task['name'])}",
                    "expected_benefit": f"Save {task['time_spent']} hours/month ({task['time_spent'] * 12} hours/year)",
                    "investment": "5-10 hours setup time",
                    "priority": "High" if task["time_spent"] >= 5 else "Medium",
                    "effort": "Medium"
                })

        return opportunities

    # Growth Opportunity Methods

    def _identify_social_growth(self) -> List[Dict]:
        """Identify social media growth opportunities."""
        opportunities = []

        # Load social media data
        social_data = self._get_social_metrics()

        # Rule: High engagement suggests growth potential
        if social_data["engagement_rate"] > 3.0:
            opportunities.append({
                "type": "social_growth",
                "observation": f"Engagement rate {social_data['engagement_rate']:.1f}% (above 3% benchmark)",
                "opportunity": "Audience highly engaged - prime time to scale content",
                "action": "Increase posting frequency by 50% (e.g., 3 posts/week → 5 posts/week)",
                "expected_impact": "Grow followers 2-3x faster, increase lead generation 40-60%",
                "investment": "2-3 hours/week additional content creation",
                "priority": "High",
                "timeframe": "Implement over next 2 weeks"
            })

        # Rule: Platform outperforming
        top_platform = social_data.get("top_platform")
        if top_platform and social_data.get(f"{top_platform}_engagement") > social_data["avg_engagement"] * 1.5:
            opportunities.append({
                "type": "platform_focus",
                "observation": f"{top_platform} engagement 50%+ higher than average",
                "opportunity": f"{top_platform} audience most engaged - highest ROI platform",
                "action": f"Double down on {top_platform}: Increase to daily posting, test new content formats",
                "expected_impact": "Maximize ROI on best-performing platform",
                "investment": "Reallocate time from low-performing platforms",
                "priority": "Medium",
                "timeframe": "1 month test"
            })

        return opportunities

    def _identify_revenue_opportunities(self) -> List[Dict]:
        """Identify revenue growth opportunities."""
        opportunities = []

        # Load financial data
        financial_data = self._get_financial_metrics()

        # Rule: Revenue growing + capacity available
        if financial_data["revenue_trend"] == "increasing":
            task_data = self._get_task_metrics()
            if task_data["completion_rate"] > 90:
                opportunities.append({
                    "type": "revenue_capacity",
                    "observation": "Revenue growing AND task completion rate >90% (have capacity)",
                    "opportunity": "Can take on additional clients without overloading",
                    "action": "Increase marketing: boost social posts, reach out to warm leads, ask for referrals",
                    "expected_impact": "10-20% revenue increase within 2 months",
                    "investment": "5 hours/week on business development",
                    "priority": "High",
                    "timeframe": "Start immediately"
                })

        return opportunities

    def _identify_efficiency_gains(self) -> List[Dict]:
        """Identify efficiency improvement opportunities."""
        # Placeholder
        return []

    def _identify_client_opportunities(self) -> List[Dict]:
        """Identify client expansion opportunities."""
        opportunities = []

        # Identify high-value clients for upsell
        high_value_clients = self._get_high_value_clients()

        if high_value_clients:
            opportunities.append({
                "type": "client_expansion",
                "observation": f"{len(high_value_clients)} clients account for high percentage of revenue",
                "opportunity": "Existing high-value clients for upsell/cross-sell",
                "action": f"Schedule check-in calls with top clients. Ask about additional needs, offer expanded services.",
                "expected_impact": "15-25% revenue increase from existing clients (lowest acquisition cost)",
                "investment": "3-4 hours for client calls",
                "priority": "High",
                "timeframe": "Next 2 weeks"
            })

        return opportunities

    # Risk Alert Methods

    def _identify_financial_risks(self) -> List[Dict]:
        """Identify financial risks."""
        risks = []

        financial_data = self._get_financial_metrics()

        # Rule: Negative cash flow trend
        if financial_data.get("cash_flow_negative_weeks", 0) >= 2:
            risks.append({
                "risk": "Negative Cash Flow Trend",
                "severity": "Critical",
                "probability": "High",
                "impact": "High",
                "description": "Cash flow negative for 2+ consecutive weeks",
                "current_status": f"${financial_data.get('weekly_cash_flow', 0):.2f} this week",
                "mitigation": [
                    "Follow up on all outstanding invoices immediately",
                    "Review and reduce non-essential expenses",
                    "Consider short-term credit line as safety net",
                    "Accelerate new client acquisition"
                ],
                "timeline": "Act within 3 days",
                "owner": "You (CEO)"
            })

        # Rule: Revenue decline
        if financial_data.get("revenue_trend") == "declining" and financial_data.get("trend_weeks", 0) >= 3:
            risks.append({
                "risk": "Revenue Decline",
                "severity": "High",
                "probability": "High",
                "impact": "High",
                "description": f"Revenue declining for {financial_data.get('trend_weeks')} weeks",
                "current_status": f"Weekly revenue down {financial_data.get('trend_percentage', 0):.0f}% from peak",
                "mitigation": [
                    "Analyze root cause: Lost clients? Seasonality? Market change?",
                    "Increase sales/marketing activity immediately",
                    "Reach out to past clients for repeat business",
                    "Consider promotional offers"
                ],
                "timeline": "Start this week",
                "owner": "You (CEO)"
            })

        return risks

    def _identify_operational_risks(self) -> List[Dict]:
        """Identify operational risks."""
        # Placeholder
        return []

    def _identify_goal_risks(self) -> List[Dict]:
        """Identify goal achievement risks."""
        # Placeholder
        return []

    def _identify_external_risks(self) -> List[Dict]:
        """Identify external/market risks."""
        # Placeholder
        return []

    # Helper Methods

    def _identify_subscriptions(self, content: str) -> List[Dict]:
        """Identify recurring subscriptions from transactions."""
        # Simplified - would use pattern matching
        return []

    def _get_last_activity(self, vendor: str) -> datetime:
        """Get last activity date for a service."""
        # Would check logs/usage data
        return None

    def _suggest_alternative(self, vendor: str) -> str:
        """Suggest alternatives for a subscription."""
        alternatives = {
            "Notion": "Already using Obsidian",
            "Dropbox": "Use Google Drive or OneDrive",
            "Slack": "Use Microsoft Teams or Discord"
        }
        return alternatives.get(vendor, "Free alternative may exist")

    def _check_duplicate(self, vendor: str, all_subs: List[Dict]) -> str:
        """Check for duplicate functionality."""
        # Simplified
        return None

    def _priority_from_savings(self, annual_savings: float) -> str:
        """Calculate priority from savings amount."""
        if annual_savings >= 1200:
            return "High"
        elif annual_savings >= 600:
            return "Medium"
        else:
            return "Low"

    def _get_email_metrics(self) -> Dict:
        """Get email performance metrics."""
        return {
            "avg_response_time": 24,
            "weekly_volume": 30
        }

    def _get_task_metrics(self) -> Dict:
        """Get task management metrics."""
        return {
            "completion_rate": 85,
            "avg_cycle_time": 4
        }

    def _find_recurring_tasks(self) -> List[Dict]:
        """Find recurring manual tasks."""
        return []

    def _suggest_automation(self, task_name: str) -> str:
        """Suggest automation method for task."""
        return "Claude Code skill, Zapier, or Python script"

    def _get_social_metrics(self) -> Dict:
        """Get social media metrics."""
        return {
            "engagement_rate": 2.5,
            "avg_engagement": 2.0,
            "top_platform": None
        }

    def _get_financial_metrics(self) -> Dict:
        """Get financial metrics."""
        return {
            "revenue_trend": "stable"
        }

    def _get_high_value_clients(self) -> List[str]:
        """Identify high-value clients."""
        return []

    def _calculate_priority_score(self, recommendation: Dict) -> float:
        """Calculate priority score for sorting."""
        # Simplified scoring
        priority_map = {"Critical": 10, "High": 7, "Medium": 4, "Low": 2}
        effort_map = {"Low": 8, "Medium": 5, "High": 2}

        priority = priority_map.get(recommendation.get("priority", "Medium"), 4)
        effort = effort_map.get(recommendation.get("effort", "Medium"), 5)

        return (priority * 0.6) + (effort * 0.4)


def main():
    parser = argparse.ArgumentParser(description="Generate business insights and recommendations")
    parser.add_argument("--focus", choices=["all", "cost-optimization", "process-improvement", "growth", "risk"],
                        default="all", help="Focus area (default: all)")
    parser.add_argument("--min-savings", type=float, default=0,
                        help="Minimum annual savings for cost recommendations (default: 0)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--vault", type=str, default="Vault", help="Path to Obsidian vault")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize generator
    generator = InsightGenerator(vault_path=args.vault)

    # Generate insights
    try:
        insights = generator.generate_all(focus=args.focus, min_savings=args.min_savings)

        if args.json:
            print(json.dumps(insights, indent=2))
        else:
            # Print formatted results
            print("\n" + "="*60)
            print("INSIGHTS & RECOMMENDATIONS")
            print("="*60)

            categories = {
                "cost_optimization": ("💰 COST OPTIMIZATION", "Annual Savings"),
                "process_improvement": ("📈 PROCESS IMPROVEMENTS", "Expected Benefit"),
                "growth_opportunity": ("🚀 GROWTH OPPORTUNITIES", "Expected Impact"),
                "risk_alert": ("⚠️ RISK ALERTS", "Severity")
            }

            for cat_key, (cat_title, metric_label) in categories.items():
                items = insights.get(cat_key, [])
                if items:
                    print(f"\n{cat_title} ({len(items)}):\n")
                    for i, item in enumerate(items, 1):
                        print(f"{i}. {item.get('action') or item.get('observation', 'N/A')}")

                        if "annual_savings" in item:
                            print(f"   Savings: ${item['annual_savings']:.2f}/year")
                        if "expected_benefit" in item:
                            print(f"   Benefit: {item['expected_benefit']}")
                        if "expected_impact" in item:
                            print(f"   Impact: {item['expected_impact']}")
                        if "severity" in item:
                            print(f"   Severity: {item['severity'].upper()}")

                        priority = item.get("priority", "Medium")
                        effort = item.get("effort", "Medium")
                        print(f"   Priority: {priority} | Effort: {effort}\n")

            total = sum(len(items) for items in insights.values())
            if total == 0:
                print("\n✅ No recommendations at this time - business running smoothly!")

            print("="*60)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
