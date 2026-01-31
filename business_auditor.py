"""
Business Auditor for Gold Tier
Performs weekly business audits analyzing transactions, task completion, and performance metrics.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from collections import defaultdict


class BusinessAuditor:
    """System for performing business audits and analysis"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Business_Intelligence/Audits"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create additional directories
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Briefings").mkdir(parents=True, exist_ok=True)
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Forecasts").mkdir(parents=True, exist_ok=True)
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Recommendations").mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Business goals and targets
        self.business_goals = self._load_business_goals()
        self.accounting_data = self._load_accounting_data()
        self.task_completion_data = self._load_task_completion_data()

    def _setup_logging(self) -> logging.Logger:
        """Set up business auditor logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "business_auditor.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_business_goals(self) -> Dict[str, Any]:
        """Load business goals and targets"""
        goals_file = Path("Vault/Business_Goals.md")
        if goals_file.exists():
            # In a real implementation, this would parse the goals file
            # For now, we'll return a default structure
            return {
                "monthly_revenue_target": 10000,
                "monthly_expense_budget": 5000,
                "task_completion_rate_target": 0.95,
                "email_response_time_target_hours": 24,
                "social_media_engagement_target": 100,
                "new_client_acquisition_target": 5
            }
        else:
            # Default goals
            return {
                "monthly_revenue_target": 10000,
                "monthly_expense_budget": 5000,
                "task_completion_rate_target": 0.95,
                "email_response_time_target_hours": 24,
                "social_media_engagement_target": 100,
                "new_client_acquisition_target": 5
            }

    def _load_accounting_data(self) -> Dict[str, Any]:
        """Load accounting data for analysis"""
        # This would typically load from the accounting system
        # For now, we'll create sample data
        return {
            "transactions": [
                {"date": "2026-01-25", "type": "revenue", "amount": 2500, "description": "Project Alpha Completion"},
                {"date": "2026-01-26", "type": "expense", "amount": 300, "description": "AWS Hosting"},
                {"date": "2026-01-27", "type": "revenue", "amount": 1800, "description": "Consulting Services"},
                {"date": "2026-01-28", "type": "expense", "amount": 150, "description": "Software Licenses"},
            ],
            "current_month": {
                "revenue": 4300,
                "expenses": 450,
                "profit": 3850
            }
        }

    def _load_task_completion_data(self) -> Dict[str, Any]:
        """Load task completion data"""
        # This would load from the task system
        # For now, we'll create sample data
        return {
            "completed_this_week": [
                {"id": "task_001", "name": "Project Alpha", "duration_hours": 15, "expected_duration": 20},
                {"id": "task_002", "name": "Client Meeting Prep", "duration_hours": 3, "expected_duration": 2},
                {"id": "task_003", "name": "System Updates", "duration_hours": 5, "expected_duration": 4}
            ],
            "pending": [
                {"id": "task_004", "name": "Project Beta", "estimated_remaining_hours": 40}
            ],
            "completion_rate": 0.85,
            "average_cycle_time": 12.5  # hours
        }

    def _load_social_media_data(self) -> Dict[str, Any]:
        """Load social media performance data"""
        # This would load from social media managers
        # For now, we'll create sample data
        return {
            "facebook": {
                "posts_this_week": 3,
                "likes": 45,
                "comments": 12,
                "shares": 8,
                "reach": 1200
            },
            "instagram": {
                "posts_this_week": 5,
                "likes": 120,
                "comments": 25,
                "saves": 15,
                "reach": 2100
            },
            "twitter": {
                "posts_this_week": 7,
                "likes": 65,
                "retweets": 18,
                "replies": 9,
                "impressions": 3500
            }
        }

    def _load_email_data(self) -> Dict[str, Any]:
        """Load email performance data"""
        # This would load from email system
        # For now, we'll create sample data
        return {
            "emails_processed": 24,
            "emails_received": 31,
            "average_response_time_hours": 18.5,
            "urgent_emails_handled": 5,
            "response_rate": 0.77
        }

    def _calculate_weekly_metrics(self) -> Dict[str, Any]:
        """Calculate weekly business metrics"""
        # Get current week data
        start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Revenue and expenses
        weekly_revenue = sum(t["amount"] for t in self.accounting_data["transactions"]
                           if t["type"] == "revenue" and
                           datetime.strptime(t["date"], "%Y-%m-%d").date() >= start_of_week.date())

        weekly_expenses = sum(t["amount"] for t in self.accounting_data["transactions"]
                            if t["type"] == "expense" and
                            datetime.strptime(t["date"], "%Y-%m-%d").date() >= start_of_week.date())

        # Social media metrics
        social_data = self._load_social_media_data()
        total_engagement = (social_data["facebook"]["likes"] + social_data["facebook"]["comments"] + social_data["facebook"]["shares"] +
                           social_data["instagram"]["likes"] + social_data["instagram"]["comments"] + social_data["instagram"]["saves"] +
                           social_data["twitter"]["likes"] + social_data["twitter"]["retweets"] + social_data["twitter"]["replies"])

        # Email metrics
        email_data = self._load_email_data()

        # Task metrics
        task_data = self.task_completion_data

        metrics = {
            "period_start": start_of_week.strftime("%Y-%m-%d"),
            "period_end": end_of_week.strftime("%Y-%m-%d"),
            "revenue": {
                "this_week": weekly_revenue,
                "target": self.business_goals["monthly_revenue_target"] / 4,  # Approximate weekly target
                "variance": weekly_revenue - (self.business_goals["monthly_revenue_target"] / 4),
                "trend": "positive" if weekly_revenue > (self.business_goals["monthly_revenue_target"] / 4) else "negative"
            },
            "expenses": {
                "this_week": weekly_expenses,
                "budget": self.business_goals["monthly_expense_budget"] / 4,  # Approximate weekly budget
                "variance": weekly_expenses - (self.business_goals["monthly_expense_budget"] / 4),
                "trend": "positive" if weekly_expenses < (self.business_goals["monthly_expense_budget"] / 4) else "negative"
            },
            "profit": {
                "this_week": weekly_revenue - weekly_expenses,
                "margin": round(((weekly_revenue - weekly_expenses) / max(weekly_revenue, 1)) * 100, 2)
            },
            "operations": {
                "task_completion_rate": task_data["completion_rate"],
                "target_rate": self.business_goals["task_completion_rate_target"],
                "cycle_time_hours": task_data["average_cycle_time"],
                "email_response_time_hours": email_data["average_response_time_hours"],
                "target_response_time": self.business_goals["email_response_time_target_hours"]
            },
            "engagement": {
                "social_media_engagement": total_engagement,
                "target_engagement": self.business_goals["social_media_engagement_target"],
                "email_response_rate": email_data["response_rate"]
            },
            "outstanding": {
                "pending_tasks": len(task_data["pending"]),
                "unpaid_invoices": 2,  # This would come from accounting system
                "urgent_emails": email_data["urgent_emails_handled"]
            }
        }

        return metrics

    def _identify_bottlenecks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify business bottlenecks and issues"""
        bottlenecks = []

        # Task completion bottleneck
        if metrics["operations"]["task_completion_rate"] < 0.90:
            bottlenecks.append({
                "type": "operational",
                "severity": "high",
                "area": "task_completion",
                "description": f"Task completion rate is {metrics['operations']['task_completion_rate']:.2%}, below 90% target",
                "impact": "Delays in project delivery",
                "suggestion": "Review task assignments and workload distribution"
            })

        # Email response time bottleneck
        if metrics["operations"]["email_response_time_hours"] > metrics["operations"]["target_response_time"]:
            bottlenecks.append({
                "type": "communication",
                "severity": "medium",
                "area": "email_response",
                "description": f"Average email response time is {metrics['operations']['email_response_time_hours']:.1f} hours, above {metrics['operations']['target_response_time']} hour target",
                "impact": "Potential client dissatisfaction",
                "suggestion": "Implement email processing schedule"
            })

        # Revenue bottleneck
        if metrics["revenue"]["trend"] == "negative":
            bottlenecks.append({
                "type": "financial",
                "severity": "high",
                "area": "revenue",
                "description": f"Weekly revenue is below target by ${abs(metrics['revenue']['variance']):,.2f}",
                "impact": "Reduced cash flow and profitability",
                "suggestion": "Review sales pipeline and client acquisition efforts"
            })

        # Expense bottleneck
        if metrics["expenses"]["trend"] == "negative":
            bottlenecks.append({
                "type": "financial",
                "severity": "medium",
                "area": "expenses",
                "description": f"Weekly expenses are above budget by ${abs(metrics['expenses']['variance']):,.2f}",
                "impact": "Reduced profitability",
                "suggestion": "Review expense categories and spending patterns"
            })

        # Outstanding items bottleneck
        if metrics["outstanding"]["unpaid_invoices"] > 3:
            bottlenecks.append({
                "type": "financial",
                "severity": "medium",
                "area": "accounts_receivable",
                "description": f"There are {metrics['outstanding']['unpaid_invoices']} unpaid invoices",
                "impact": "Cash flow issues",
                "suggestion": "Follow up on outstanding payments"
            })

        return bottlenecks

    def _generate_recommendations(self, metrics: Dict[str, Any], bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate business recommendations based on metrics and bottlenecks"""
        recommendations = []

        # Cost optimization recommendations
        if metrics["expenses"]["trend"] == "negative":
            recommendations.append({
                "category": "cost_optimization",
                "priority": "high",
                "title": "Review Expense Categories",
                "description": "Weekly expenses are above budget, suggesting opportunities for cost reduction",
                "action_items": [
                    "Analyze expense categories to identify largest spenders",
                    "Review subscription services for unused licenses",
                    "Negotiate better rates for high-cost services"
                ],
                "expected_impact": "Reduce monthly expenses by 10-15%"
            })

        # Process improvement recommendations
        if bottlenecks:
            recommendations.append({
                "category": "process_improvement",
                "priority": "high",
                "title": "Address Identified Bottlenecks",
                "description": f"{len(bottlenecks)} bottlenecks identified requiring attention",
                "action_items": [f"{b['area']}: {b['suggestion']}" for b in bottlenecks],
                "expected_impact": "Improved operational efficiency"
            })

        # Growth opportunity recommendations
        if metrics["revenue"]["trend"] == "positive":
            recommendations.append({
                "category": "growth_opportunity",
                "priority": "medium",
                "title": "Capitalize on Revenue Growth",
                "description": "Positive revenue trend indicates market demand for services",
                "action_items": [
                    "Scale marketing efforts to acquire more clients",
                    "Expand service offerings based on successful areas",
                    "Invest in tools to improve productivity"
                ],
                "expected_impact": "Accelerate business growth"
            })

        # Operational efficiency recommendations
        if metrics["operations"]["cycle_time_hours"] > 20:
            recommendations.append({
                "category": "operational_efficiency",
                "priority": "medium",
                "title": "Reduce Task Cycle Time",
                "description": f"Average task cycle time is {metrics['operations']['cycle_time_hours']:.1f} hours, indicating potential inefficiencies",
                "action_items": [
                    "Implement task batching to reduce context switching",
                    "Streamline approval processes",
                    "Automate repetitive tasks where possible"
                ],
                "expected_impact": "Reduce average task completion time by 25%"
            })

        return recommendations

    def perform_weekly_audit(self) -> Dict[str, Any]:
        """Perform a comprehensive weekly business audit"""
        self.logger.info("Starting weekly business audit...")

        # Calculate metrics
        metrics = self._calculate_weekly_metrics()
        self.logger.info(f"Audit metrics calculated for {metrics['period_start']} to {metrics['period_end']}")

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(metrics)
        self.logger.info(f"Identified {len(bottlenecks)} bottlenecks")

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, bottlenecks)
        self.logger.info(f"Generated {len(recommendations)} recommendations")

        # Calculate health scores
        financial_score = self._calculate_financial_health_score(metrics)
        operational_score = self._calculate_operational_health_score(metrics)
        engagement_score = self._calculate_engagement_health_score(metrics)

        overall_score = round((financial_score + operational_score + engagement_score) / 3, 1)

        # Create audit report
        audit_report = {
            "audit_date": datetime.now().isoformat(),
            "period": {
                "start": metrics["period_start"],
                "end": metrics["period_end"]
            },
            "metrics": metrics,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "health_scores": {
                "financial": financial_score,
                "operational": operational_score,
                "engagement": engagement_score,
                "overall": overall_score
            },
            "status": self._determine_business_status(overall_score),
            "next_actions": self._prioritize_next_actions(bottlenecks, recommendations)
        }

        # Save audit report
        audit_file = self.storage_path / f"audit_{metrics['period_start']}_to_{metrics['period_end']}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit_report, f, indent=2)

        self.logger.info(f"Weekly audit completed. Report saved to {audit_file}")

        return audit_report

    def _calculate_financial_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate financial health score (0-100)"""
        score = 50  # Base score

        # Revenue performance (30 points)
        revenue_target_met = min(1.0, metrics["revenue"]["this_week"] / max(metrics["revenue"]["target"], 1))
        score += int(revenue_target_met * 30)

        # Expense control (25 points)
        expense_target_met = 1.0 - min(1.0, abs(metrics["expenses"]["variance"]) / max(metrics["expenses"]["budget"], 1))
        score += int(expense_target_met * 25)

        # Profit margin (20 points)
        profit_margin_score = min(1.0, metrics["profit"]["margin"] / 50)  # Assume 50% as excellent margin
        score += int(profit_margin_score * 20)

        # Cash flow (25 points)
        if metrics["outstanding"]["unpaid_invoices"] == 0:
            score += 25
        elif metrics["outstanding"]["unpaid_invoices"] <= 2:
            score += 15
        elif metrics["outstanding"]["unpaid_invoices"] <= 5:
            score += 5

        return min(100, score)

    def _calculate_operational_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate operational health score (0-100)"""
        score = 50  # Base score

        # Task completion rate (40 points)
        completion_score = min(1.0, metrics["operations"]["task_completion_rate"] / 0.95)  # 95% as target
        score += int(completion_score * 40)

        # Email response time (30 points)
        response_time_score = max(0, 1.0 - (metrics["operations"]["email_response_time_hours"] / 48))  # 48 hours as max acceptable
        score += int(response_time_score * 30)

        # Cycle time efficiency (30 points)
        cycle_time_score = max(0, 1.0 - (metrics["operations"]["cycle_time_hours"] / 40))  # 40 hours as max acceptable
        score += int(cycle_time_score * 30)

        return min(100, score)

    def _calculate_engagement_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate engagement health score (0-100)"""
        score = 50  # Base score

        # Social media engagement (50 points)
        engagement_target_met = min(1.0, metrics["engagement"]["social_media_engagement"] / max(metrics["engagement"]["target_engagement"], 1))
        score += int(engagement_target_met * 50)

        # Email response rate (50 points)
        email_response_score = metrics["engagement"]["email_response_rate"]
        score += int(email_response_score * 50)

        return min(100, score)

    def _determine_business_status(self, overall_score: float) -> str:
        """Determine business status based on overall health score"""
        if overall_score >= 85:
            return "excellent"
        elif overall_score >= 70:
            return "good"
        elif overall_score >= 50:
            return "fair"
        else:
            return "needs_attention"

    def _prioritize_next_actions(self, bottlenecks: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> List[str]:
        """Prioritize next actions based on severity and impact"""
        actions = []

        # High severity bottlenecks first
        high_severity_bottlenecks = [b for b in bottlenecks if b["severity"] == "high"]
        for bottleneck in high_severity_bottlenecks:
            actions.append(f"URGENT: {bottleneck['description']} - {bottleneck['suggestion']}")

        # High priority recommendations next
        high_priority_recs = [r for r in recommendations if r["priority"] == "high"]
        for rec in high_priority_recs:
            actions.append(f"IMPORTANT: {rec['title']} - {rec['description']}")

        # Medium priority items
        medium_priority_recs = [r for r in recommendations if r["priority"] == "medium"]
        for rec in medium_priority_recs:
            actions.append(f"RECOMMENDED: {rec['title']} - {rec['description']}")

        return actions[:5]  # Return top 5 actions

    def get_historical_trends(self, weeks: int = 8) -> Dict[str, Any]:
        """Get historical business performance trends"""
        # This would load from historical audit reports
        # For now, we'll create sample trend data
        trends = {
            "weeks_analyzed": weeks,
            "revenue_trend": {
                "slope": 0.05,  # 5% growth per week
                "volatility": 0.15,
                "projection_4w": 5200  # Projected revenue for next 4 weeks
            },
            "expense_trend": {
                "slope": 0.02,  # 2% growth per week
                "volatility": 0.08,
                "projection_4w": 520  # Projected expenses for next 4 weeks
            },
            "profit_trend": {
                "slope": 0.08,  # 8% growth per week
                "volatility": 0.12,
                "projection_4w": 4680  # Projected profit for next 4 weeks
            },
            "operational_trend": {
                "task_completion_trend": 0.01,  # 1% improvement per week
                "response_time_trend": -0.5,  # 0.5 hour improvement per week
                "projection_4w": {
                    "completion_rate": 0.92,
                    "response_time": 16.0
                }
            }
        }

        # Save trends
        trends_file = self.storage_path / "historical_trends.json"
        with open(trends_file, 'w') as f:
            json.dump(trends, f, indent=2)

        return trends

    def generate_cost_analysis(self) -> Dict[str, Any]:
        """Generate detailed cost analysis and optimization opportunities"""
        # This would analyze accounting data for cost optimization
        # For now, we'll create sample analysis
        cost_analysis = {
            "total_monthly_expenses": 2100,
            "expense_categories": {
                "subscriptions": {"amount": 800, "percentage": 38.1, "providers": ["AWS", "Slack", "Notion", "GitHub"]},
                "software_licenses": {"amount": 450, "percentage": 21.4, "providers": ["Adobe", "Microsoft", "Specialized Tools"]},
                "services": {"amount": 350, "percentage": 16.7, "providers": ["Freelancers", "Consultants", "Contractors"]},
                "utilities": {"amount": 250, "percentage": 11.9, "providers": ["Internet", "Electricity", "Phone"]},
                "miscellaneous": {"amount": 250, "percentage": 11.9, "providers": ["Office Supplies", "Meals", "Travel"]}
            },
            "optimization_opportunities": [
                {
                    "opportunity": "Consolidate cloud services",
                    "potential_savings_monthly": 150,
                    "implementation_effort": "medium",
                    "timeline": "2-4 weeks",
                    "description": "Evaluate if we can consolidate AWS services or negotiate better rates"
                },
                {
                    "opportunity": "Review subscription usage",
                    "potential_savings_monthly": 100,
                    "implementation_effort": "low",
                    "timeline": "1-2 weeks",
                    "description": "Audit all subscriptions for usage and eliminate unused services"
                },
                {
                    "opportunity": "Negotiate software licenses",
                    "potential_savings_monthly": 200,
                    "implementation_effort": "high",
                    "timeline": "4-8 weeks",
                    "description": "Renegotiate enterprise license agreements for better rates"
                }
            ],
            "total_potential_savings": 450,
            "savings_percentage": 21.4,
            "analysis_date": datetime.now().isoformat()
        }

        # Save cost analysis
        analysis_file = self.storage_path / "cost_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(cost_analysis, f, indent=2)

        return cost_analysis


async def test_business_auditor():
    """Test the business auditor"""
    print("Testing Business Auditor...")

    auditor = BusinessAuditor()

    # Perform a sample audit
    print("\n1. Performing weekly audit...")
    audit_report = auditor.perform_weekly_audit()
    print(f"Audit completed for period: {audit_report['period']['start']} to {audit_report['period']['end']}")
    print(f"Overall health score: {audit_report['health_scores']['overall']}/100")
    print(f"Business status: {audit_report['status']}")

    # Show bottlenecks found
    print(f"\n2. Bottlenecks identified: {len(audit_report['bottlenecks'])}")
    for bottleneck in audit_report['bottlenecks']:
        print(f"  - {bottleneck['severity'].upper()}: {bottleneck['description']}")

    # Show recommendations
    print(f"\n3. Recommendations generated: {len(audit_report['recommendations'])}")
    for rec in audit_report['recommendations']:
        print(f"  - {rec['priority'].upper()}: {rec['title']}")

    # Show next actions
    print(f"\n4. Priority actions:")
    for action in audit_report['next_actions']:
        print(f"  - {action}")

    # Get historical trends
    print(f"\n5. Getting historical trends...")
    trends = auditor.get_historical_trends(weeks=8)
    print(f"Revenue trend slope: {trends['revenue_trend']['slope']*100:.1f}% per week")
    print(f"Projected revenue (4w): ${trends['revenue_trend']['projection_4w']:,.2f}")

    # Generate cost analysis
    print(f"\n6. Generating cost analysis...")
    cost_analysis = auditor.generate_cost_analysis()
    print(f"Total monthly expenses: ${cost_analysis['total_monthly_expenses']:,.2f}")
    print(f"Total potential savings: ${cost_analysis['total_potential_savings']:,.2f} ({cost_analysis['savings_percentage']:.1f}%)")

    # Show optimization opportunities
    print(f"\n7. Cost optimization opportunities:")
    for opp in cost_analysis['optimization_opportunities']:
        print(f"  - {opp['opportunity']}: ${opp['potential_savings_monthly']}/mo ({opp['timeline']})")

    return True


if __name__ == "__main__":
    asyncio.run(test_business_auditor())