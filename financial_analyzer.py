"""
Financial Analyzer for Gold Tier
Performs detailed financial analysis, reporting, and forecasting for the business.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


class FinancialAnalyzer:
    """System for performing financial analysis and reporting"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Business_Intelligence/Analytics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create additional directories
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Reports").mkdir(parents=True, exist_ok=True)
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Charts").mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Load financial data
        self.transactions = self._load_transaction_data()
        self.goals = self._load_business_goals()

    def _setup_logging(self) -> logging.Logger:
        """Set up financial analyzer logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "financial_analyzer.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_transaction_data(self) -> List[Dict[str, Any]]:
        """Load transaction data for analysis"""
        # This would typically load from the accounting system
        # For now, we'll create sample data
        return [
            {"date": "2025-10-01", "type": "revenue", "amount": 5200, "category": "consulting", "description": "Q4 Consulting Project"},
            {"date": "2025-10-15", "type": "expense", "amount": 1200, "category": "cloud", "description": "AWS Hosting"},
            {"date": "2025-10-20", "type": "revenue", "amount": 3800, "category": "product_sales", "description": "Software License"},
            {"date": "2025-11-01", "type": "revenue", "amount": 4500, "category": "consulting", "description": "November Project"},
            {"date": "2025-11-05", "type": "expense", "amount": 800, "category": "software", "description": "License Renewals"},
            {"date": "2025-11-15", "type": "revenue", "amount": 6200, "category": "training", "description": "Corporate Training"},
            {"date": "2025-12-01", "type": "revenue", "amount": 5800, "category": "consulting", "description": "December Project"},
            {"date": "2025-12-10", "type": "expense", "amount": 1500, "category": "marketing", "description": "Campaign"},
            {"date": "2025-12-20", "type": "revenue", "amount": 7200, "category": "product_sales", "description": "Enterprise License"},
            {"date": "2026-01-01", "type": "revenue", "amount": 4800, "category": "consulting", "description": "New Year Project"},
            {"date": "2026-01-05", "type": "expense", "amount": 950, "category": "office", "description": "Supplies"},
            {"date": "2026-01-15", "type": "revenue", "amount": 5500, "category": "consulting", "description": "January Project"},
            {"date": "2026-01-20", "type": "expense", "amount": 1100, "category": "cloud", "description": "AWS Upgrade"},
            {"date": "2026-01-25", "type": "revenue", "amount": 2500, "category": "consulting", "description": "Project Alpha Completion"},
            {"date": "2026-01-27", "type": "revenue", "amount": 1800, "category": "product_sales", "description": "Consulting Services"},
        ]

    def _load_business_goals(self) -> Dict[str, Any]:
        """Load business financial goals"""
        return {
            "monthly_revenue_target": 15000,
            "monthly_expense_budget": 8000,
            "quarterly_growth_target": 0.15,  # 15% quarterly growth
            "annual_revenue_target": 180000,
            "profit_margin_target": 0.50  # 50% target
        }

    def analyze_cash_flow(self, period_months: int = 6) -> Dict[str, Any]:
        """Analyze cash flow over the specified period"""
        # Calculate period start date
        period_start = datetime.now() - timedelta(days=period_months * 30)

        # Filter transactions for the period
        period_transactions = [
            t for t in self.transactions
            if datetime.strptime(t["date"], "%Y-%m-%d") >= period_start
        ]

        # Group by month
        monthly_data = {}
        for trans in period_transactions:
            month_year = trans["date"][:7]  # YYYY-MM
            if month_year not in monthly_data:
                monthly_data[month_year] = {"revenue": 0, "expenses": 0}

            if trans["type"] == "revenue":
                monthly_data[month_year]["revenue"] += trans["amount"]
            else:
                monthly_data[month_year]["expenses"] += trans["amount"]

        # Calculate cash flow metrics
        cash_flow_data = {
            "period_months": period_months,
            "months_analyzed": list(monthly_data.keys()),
            "monthly_breakdown": monthly_data,
            "total_revenue": sum(m["revenue"] for m in monthly_data.values()),
            "total_expenses": sum(m["expenses"] for m in monthly_data.values()),
            "net_cash_flow": sum(m["revenue"] - m["expenses"] for m in monthly_data.values()),
            "average_monthly_revenue": sum(m["revenue"] for m in monthly_data.values()) / len(monthly_data),
            "average_monthly_expenses": sum(m["expenses"] for m in monthly_data.values()) / len(monthly_data),
            "cash_flow_trend": self._calculate_trend([m["revenue"] - m["expenses"] for m in monthly_data.values()])
        }

        return cash_flow_data

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction based on values"""
        if len(values) < 2:
            return "insufficient_data"

        if values[-1] > values[0]:
            return "increasing"
        elif values[-1] < values[0]:
            return "decreasing"
        else:
            return "stable"

    def analyze_profitability(self) -> Dict[str, Any]:
        """Analyze overall profitability"""
        total_revenue = sum(t["amount"] for t in self.transactions if t["type"] == "revenue")
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == "expense")
        profit = total_revenue - total_expenses
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

        # Calculate by category
        revenue_by_category = {}
        expenses_by_category = {}

        for trans in self.transactions:
            category = trans["category"]
            if trans["type"] == "revenue":
                revenue_by_category[category] = revenue_by_category.get(category, 0) + trans["amount"]
            else:
                expenses_by_category[category] = expenses_by_category.get(category, 0) + trans["amount"]

        # Calculate category profitability
        category_profitability = {}
        all_categories = set(list(revenue_by_category.keys()) + list(expenses_by_category.keys()))

        for cat in all_categories:
            rev = revenue_by_category.get(cat, 0)
            exp = expenses_by_category.get(cat, 0)
            cat_profit = rev - exp
            margin = (cat_profit / rev * 100) if rev > 0 else 0

            category_profitability[cat] = {
                "revenue": rev,
                "expenses": exp,
                "profit": cat_profit,
                "margin": margin
            }

        profitability_data = {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "total_profit": profit,
            "overall_margin": round(profit_margin, 2),
            "target_margin": self.goals["profit_margin_target"] * 100,
            "margin_variance": round(profit_margin - (self.goals["profit_margin_target"] * 100), 2),
            "revenue_by_category": revenue_by_category,
            "expenses_by_category": expenses_by_category,
            "category_profitability": category_profitability,
            "top_performing_category": max(category_profitability.items(), key=lambda x: x[1]["profit"])[0] if category_profitability else None
        }

        return profitability_data

    def analyze_expenses(self) -> Dict[str, Any]:
        """Analyze expense patterns and identify optimization opportunities"""
        expenses = [t for t in self.transactions if t["type"] == "expense"]

        # Group expenses by category
        category_totals = {}
        category_monthly = {}

        for exp in expenses:
            cat = exp["category"]
            month = exp["date"][:7]  # YYYY-MM

            category_totals[cat] = category_totals.get(cat, 0) + exp["amount"]

            if cat not in category_monthly:
                category_monthly[cat] = {}
            if month not in category_monthly[cat]:
                category_monthly[cat][month] = 0
            category_monthly[cat][month] += exp["amount"]

        # Identify recurring expenses
        recurring_expenses = {}
        for cat, monthly in category_monthly.items():
            if len(monthly) > 1:  # Appears in multiple months
                avg_monthly = sum(monthly.values()) / len(monthly)
                recurring_expenses[cat] = {
                    "total": category_totals[cat],
                    "avg_monthly": avg_monthly,
                    "months_active": len(monthly),
                    "is_recurring": True
                }
            else:
                recurring_expenses[cat] = {
                    "total": category_totals[cat],
                    "avg_monthly": category_totals[cat],
                    "months_active": 1,
                    "is_recurring": False
                }

        # Identify optimization opportunities
        optimization_opportunities = []
        for cat, data in recurring_expenses.items():
            if data["is_recurring"] and data["avg_monthly"] > 500:  # Significant recurring expense
                optimization_opportunities.append({
                    "category": cat,
                    "current_cost": data["avg_monthly"],
                    "potential_savings": round(data["avg_monthly"] * 0.15, 2),  # 15% potential savings
                    "optimization_strategy": "Review service necessity and negotiate better rates"
                })

        expense_data = {
            "total_expenses": sum(category_totals.values()),
            "expenses_by_category": category_totals,
            "recurring_expenses": recurring_expenses,
            "optimization_opportunities": optimization_opportunities,
            "total_potential_savings": sum(opp["potential_savings"] for opp in optimization_opportunities),
            "top_expense_categories": sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        }

        return expense_data

    def generate_financial_report(self, report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate a comprehensive financial report"""
        self.logger.info(f"Generating {report_type} financial report...")

        # Get all analyses
        cash_flow = self.analyze_cash_flow(period_months=6)
        profitability = self.analyze_profitability()
        expenses = self.analyze_expenses()

        # Create report
        report = {
            "report_date": datetime.now().isoformat(),
            "report_type": report_type,
            "cash_flow_analysis": cash_flow,
            "profitability_analysis": profitability,
            "expense_analysis": expenses,
            "key_metrics": {
                "total_revenue": profitability["total_revenue"],
                "total_expenses": profitability["total_expenses"],
                "net_profit": profitability["total_profit"],
                "profit_margin": profitability["overall_margin"],
                "cash_flow_6m": cash_flow["net_cash_flow"],
                "potential_savings": expenses["total_potential_savings"]
            },
            "targets_vs_actual": self._compare_targets_vs_actual(),
            "recommendations": self._generate_financial_recommendations(expenses, profitability)
        }

        # Save report
        report_file = self.storage_path / f"financial_report_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Financial report generated: {report_file}")

        return report

    def _compare_targets_vs_actual(self) -> Dict[str, Any]:
        """Compare financial targets versus actual performance"""
        total_revenue = sum(t["amount"] for t in self.transactions if t["type"] == "revenue")
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == "expense")

        # Calculate YTD months (assuming data starts from beginning of year)
        months_in_data = len(set(t["date"][:7] for t in self.transactions if t["date"].startswith("2026")))

        ytd_revenue = total_revenue
        ytd_expenses = total_expenses

        # Project annual figures
        projected_annual_revenue = ytd_revenue * (12 / max(months_in_data, 1))
        projected_annual_expenses = ytd_expenses * (12 / max(months_in_data, 1))

        target_vs_actual = {
            "annual_revenue": {
                "actual_ytd": ytd_revenue,
                "projected_annual": projected_annual_revenue,
                "target": self.goals["annual_revenue_target"],
                "variance": projected_annual_revenue - self.goals["annual_revenue_target"],
                "variance_percent": round((projected_annual_revenue - self.goals["annual_revenue_target"]) / self.goals["annual_revenue_target"] * 100, 2)
            },
            "monthly_expense": {
                "actual_avg": total_expenses / max(len(set(t["date"][:7] for t in self.transactions)), 1),
                "target": self.goals["monthly_expense_budget"],
                "variance": (total_expenses / max(len(set(t["date"][:7] for t in self.transactions)), 1)) - self.goals["monthly_expense_budget"],
                "variance_percent": round(((total_expenses / max(len(set(t["date"][:7] for t in self.transactions)), 1)) - self.goals["monthly_expense_budget"]) / self.goals["monthly_expense_budget"] * 100, 2)
            },
            "profit_margin": {
                "actual": self.analyze_profitability()["overall_margin"],
                "target": self.goals["profit_margin_target"] * 100,
                "variance": self.analyze_profitability()["overall_margin"] - (self.goals["profit_margin_target"] * 100)
            }
        }

        return target_vs_actual

    def _generate_financial_recommendations(self, expenses: Dict[str, Any], profitability: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate financial recommendations based on analysis"""
        recommendations = []

        # Cost optimization recommendations
        if expenses["total_potential_savings"] > 0:
            recommendations.append({
                "category": "cost_optimization",
                "priority": "high",
                "title": "Implement Expense Optimization",
                "description": f"Potential to save ${expenses['total_potential_savings']:,.2f} monthly through expense optimization",
                "action_items": [f"Review {opp['category']} expenses (${opp['current_cost']:,.2f}/mo)" for opp in expenses["optimization_opportunities"]],
                "expected_impact": f"Reduce monthly expenses by ${expenses['total_potential_savings']:,.2f}"
            })

        # Revenue enhancement recommendations
        if profitability["overall_margin"] < self.goals["profit_margin_target"] * 100:
            recommendations.append({
                "category": "revenue_enhancement",
                "priority": "high",
                "title": "Improve Profit Margins",
                "description": f"Current margin {profitability['overall_margin']:.1f}% below target of {self.goals['profit_margin_target']*100:.1f}%",
                "action_items": [
                    "Analyze pricing strategy",
                    "Focus on higher-margin services",
                    "Optimize cost structure"
                ],
                "expected_impact": f"Increase profit margins by 5-10 percentage points"
            })

        # Cash flow recommendations
        cash_flow = self.analyze_cash_flow(period_months=6)
        if cash_flow["cash_flow_trend"] == "decreasing":
            recommendations.append({
                "category": "cash_flow",
                "priority": "medium",
                "title": "Stabilize Cash Flow",
                "description": "Cash flow showing decreasing trend over recent months",
                "action_items": [
                    "Accelerate receivables collection",
                    "Manage payables timing",
                    "Review seasonal patterns"
                ],
                "expected_impact": "Stabilize monthly cash flow"
            })

        return recommendations

    def generate_p_and_l_statement(self) -> str:
        """Generate a Profit & Loss statement"""
        profitability = self.analyze_profitability()

        p_and_l = f"""
# Profit & Loss Statement
## Period: January 1, 2025 to {datetime.now().strftime('%B %d, %Y')}

### Revenue
"""
        for cat, amount in profitability["revenue_by_category"].items():
            p_and_l += f"- {cat.title()}: ${amount:,.2f}\n"

        p_and_l += f"\n**Total Revenue: ${profitability['total_revenue']:,.2f}**\n\n"

        p_and_l += "### Expenses\n"
        for cat, amount in profitability["expenses_by_category"].items():
            p_and_l += f"- {cat.title()}: ${amount:,.2f}\n"

        p_and_l += f"\n**Total Expenses: ${profitability['total_expenses']:,.2f}**\n\n"
        p_and_l += f"**Net Profit: ${profitability['total_profit']:,.2f}**\n"
        p_and_l += f"**Profit Margin: {profitability['overall_margin']:.2f}%**\n"

        # Save P&L
        pl_file = self.storage_path / f"P_and_L_Statement_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(pl_file, 'w') as f:
            f.write(p_and_l)

        return str(pl_file)

    def generate_balance_sheet(self) -> str:
        """Generate a simplified balance sheet"""
        # For this simplified version, we'll focus on assets and liabilities
        # In a real system, this would connect to actual accounting data
        profitability = self.analyze_profitability()

        # Estimate assets based on revenue and profits
        estimated_assets = profitability["total_revenue"] * 0.6  # Simplified estimation
        estimated_liabilities = profitability["total_expenses"] * 0.4  # Simplified estimation
        equity = estimated_assets - estimated_liabilities

        balance_sheet = f"""
# Balance Sheet
## As of {datetime.now().strftime('%B %d, %Y')}

### Assets
- Accounts Receivable (Estimated): ${profitability['total_revenue'] * 0.3:,.2f}
- Cash and Equivalents (Estimated): ${profitability['total_profit'] * 0.7:,.2f}
- Equipment and Software (Estimated): ${profitability['total_expenses'] * 0.2:,.2f}

**Total Assets: ${estimated_assets:,.2f}**

### Liabilities
- Accounts Payable (Estimated): ${profitability['total_expenses'] * 0.2:,.2f}
- Accrued Expenses (Estimated): ${profitability['total_expenses'] * 0.2:,.2f}

**Total Liabilities: ${estimated_liabilities:,.2f}**

### Equity
**Owner's Equity: ${equity:,.2f}**

### Accounting Equation
Assets ({estimated_assets:,.2f}) = Liabilities ({estimated_liabilities:,.2f}) + Equity ({equity:,.2f})

---

*Note: This is an estimated balance sheet based on transaction analysis. For official figures, consult actual accounting records.*
        """

        # Save balance sheet
        bs_file = self.storage_path / f"Balance_Sheet_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(bs_file, 'w') as f:
            f.write(balance_sheet)

        return str(bs_file)

    def create_financial_dashboard(self) -> str:
        """Create a financial dashboard with key metrics"""
        profitability = self.analyze_profitability()
        cash_flow = self.analyze_cash_flow(period_months=6)
        expenses = self.analyze_expenses()

        dashboard = f"""
# Financial Dashboard
## As of {datetime.now().strftime('%B %d, %Y')}

### Key Metrics
| Metric | Value | Target | Variance |
|--------|-------|--------|----------|
| Total Revenue | ${profitability['total_revenue']:,.2f} | - | - |
| Total Expenses | ${profitability['total_expenses']:,.2f} | - | - |
| Net Profit | ${profitability['total_profit']:,.2f} | - | - |
| Profit Margin | {profitability['overall_margin']:.2f}% | {self.goals['profit_margin_target']*100:.2f}% | {profitability['margin_variance']:+.2f}% |
| 6-Month Cash Flow | ${cash_flow['net_cash_flow']:,.2f} | - | - |
| Potential Savings | ${expenses['total_potential_savings']:,.2f}/mo | - | - |

### Revenue by Category
"""
        for cat, amount in profitability["revenue_by_category"].items():
            dashboard += f"- {cat.title()}: ${amount:,.2f} ({amount/profitability['total_revenue']*100:.1f}%)\n"

        dashboard += f"\n### Expense Categories\n"
        for cat, amount in profitability["expenses_by_category"].items():
            dashboard += f"- {cat.title()}: ${amount:,.2f} ({amount/profitability['total_expenses']*100:.1f}%)\n"

        dashboard += f"\n### Top Performing Category\n"
        dashboard += f"- {profitability['top_performing_category']} with ${profitability['category_profitability'][profitability['top_performing_category']]['profit']:,.2f} profit\n"

        # Save dashboard
        dash_file = self.storage_path / f"Financial_Dashboard_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(dash_file, 'w') as f:
            f.write(dashboard)

        return str(dash_file)

    def forecast_revenue(self, months_ahead: int = 6) -> Dict[str, Any]:
        """Forecast revenue for the specified number of months ahead"""
        # Prepare data for forecasting
        monthly_revenue = {}
        for trans in self.transactions:
            if trans["type"] == "revenue":
                month = trans["date"][:7]  # YYYY-MM
                if month not in monthly_revenue:
                    monthly_revenue[month] = 0
                monthly_revenue[month] += trans["amount"]

        # Sort by date and prepare for modeling
        sorted_months = sorted(monthly_revenue.keys())
        monthly_values = [monthly_revenue[m] for m in sorted_months]

        # Create time series data
        X = np.array(range(len(monthly_values))).reshape(-1, 1)
        y = np.array(monthly_values)

        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict future values
        future_X = np.array(range(len(monthly_values), len(monthly_values) + months_ahead)).reshape(-1, 1)
        predictions = model.predict(future_X)

        # Calculate confidence intervals (simplified)
        mse = mean_squared_error(y, model.predict(X))
        std_error = np.sqrt(mse)

        forecast_data = {
            "historical_months": sorted_months,
            "historical_revenue": monthly_values,
            "predictions": predictions.tolist(),
            "prediction_months": [(datetime.strptime(sorted_months[-1], "%Y-%m") + timedelta(days=30*(i+1))).strftime("%Y-%m") for i in range(months_ahead)],
            "confidence_interval_plus": (predictions + 1.96 * std_error).tolist(),
            "confidence_interval_minus": (predictions - 1.96 * std_error).tolist(),
            "trend_slope": model.coef_[0],
            "r_squared": model.score(X, y),
            "total_predicted_revenue": sum(predictions),
            "model_accuracy": "high" if model.score(X, y) > 0.7 else "medium" if model.score(X, y) > 0.5 else "low"
        }

        # Save forecast
        forecast_file = self.storage_path / f"Revenue_Forecast_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(forecast_file, 'w') as f:
            json.dump(forecast_data, f, indent=2)

        return forecast_data

    def create_financial_chart(self, chart_type: str = "revenue_trend") -> str:
        """Create a financial chart visualization"""
        # This would typically create an actual chart file
        # For now, we'll just return a description of what would be created
        chart_description = f"""
Chart Created: {chart_type}
Date: {datetime.now().strftime('%Y-%m-%d')}
Location: {self.storage_path}/Charts/

This would be a {chart_type} chart showing financial trends based on the available transaction data.
The chart would visualize revenue, expenses, and profit trends over time.
        """

        # In a real implementation, this would use matplotlib/seaborn to create actual charts
        chart_file = self.storage_path / "Charts" / f"{chart_type}_{datetime.now().strftime('%Y-%m-%d')}.png"
        chart_file.parent.mkdir(exist_ok=True)

        # Create a placeholder file
        with open(chart_file, 'w') as f:
            f.write(f"Placeholder for {chart_type} chart\nGenerated on {datetime.now().strftime('%Y-%m-%d')}\n")

        self.logger.info(f"Chart created: {chart_file}")

        return str(chart_file)


async def test_financial_analyzer():
    """Test the financial analyzer"""
    print("Testing Financial Analyzer...")

    analyzer = FinancialAnalyzer()

    # Perform cash flow analysis
    print("\n1. Performing cash flow analysis...")
    cash_flow = analyzer.analyze_cash_flow(period_months=6)
    print(f"6-month cash flow: ${cash_flow['net_cash_flow']:,.2f}")
    print(f"Trend: {cash_flow['cash_flow_trend']}")
    print(f"Average monthly revenue: ${cash_flow['average_monthly_revenue']:,.2f}")

    # Perform profitability analysis
    print("\n2. Performing profitability analysis...")
    profitability = analyzer.analyze_profitability()
    print(f"Total revenue: ${profitability['total_revenue']:,.2f}")
    print(f"Total expenses: ${profitability['total_expenses']:,.2f}")
    print(f"Net profit: ${profitability['total_profit']:,.2f}")
    print(f"Profit margin: {profitability['overall_margin']:.2f}%")
    print(f"Top performing category: {profitability['top_performing_category']}")

    # Perform expense analysis
    print("\n3. Performing expense analysis...")
    expenses = analyzer.analyze_expenses()
    print(f"Total expenses: ${expenses['total_expenses']:,.2f}")
    print(f"Top expense categories: {expenses['top_expense_categories'][:3]}")
    print(f"Potential savings: ${expenses['total_potential_savings']:,.2f}/month")

    # Generate comprehensive financial report
    print("\n4. Generating financial report...")
    report = analyzer.generate_financial_report()
    print(f"Report generated with {len(report['recommendations'])} recommendations")

    # Generate P&L statement
    print("\n5. Generating P&L statement...")
    pl_file = analyzer.generate_p_and_l_statement()
    print(f"P&L statement created: {pl_file}")

    # Generate balance sheet
    print("\n6. Generating balance sheet...")
    bs_file = analyzer.generate_balance_sheet()
    print(f"Balance sheet created: {bs_file}")

    # Create financial dashboard
    print("\n7. Creating financial dashboard...")
    dash_file = analyzer.create_financial_dashboard()
    print(f"Dashboard created: {dash_file}")

    # Perform revenue forecasting
    print("\n8. Performing revenue forecasting...")
    forecast = analyzer.forecast_revenue(months_ahead=6)
    print(f"Predicted revenue for next 6 months: ${forecast['total_predicted_revenue']:,.2f}")
    print(f"Trend slope: {forecast['trend_slope']:.2f}")
    print(f"Model accuracy: {forecast['model_accuracy']} (R²: {forecast['r_squared']:.3f})")

    # Create financial chart
    print("\n9. Creating financial chart...")
    chart_file = analyzer.create_financial_chart("revenue_trend")
    print(f"Chart created: {chart_file}")

    return True


if __name__ == "__main__":
    asyncio.run(test_financial_analyzer())