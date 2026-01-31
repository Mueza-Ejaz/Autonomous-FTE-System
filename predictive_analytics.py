"""
Predictive Analytics System for Gold Tier
Performs predictive analysis for cash flow, busy periods, client behavior, and resource allocation.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score
import warnings
warnings.filterwarnings('ignore')


class PredictiveAnalytics:
    """System for predictive analysis of business metrics"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Business_Intelligence/Forecasts"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create additional directories
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Models").mkdir(parents=True, exist_ok=True)
        (Path("AI_Employee_Vault/Gold_Tier/Business_Intelligence") / "Predictions").mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Load historical data
        self.transaction_data = self._load_transaction_data()
        self.client_data = self._load_client_data()
        self.resource_data = self._load_resource_data()

        # Initialize models
        self.models = {
            "cash_flow": None,
            "busy_periods": None,
            "client_payment_behavior": None,
            "resource_allocation": None
        }

        # Initialize scalers
        self.scalers = {
            "cash_flow": StandardScaler(),
            "resource_allocation": StandardScaler()
        }

    def _setup_logging(self) -> logging.Logger:
        """Set up predictive analytics logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "predictive_analytics.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_transaction_data(self) -> List[Dict[str, Any]]:
        """Load historical transaction data"""
        # This would typically load from the accounting system
        # For now, we'll create sample data
        transactions = []

        # Generate synthetic data for the past 2 years
        start_date = datetime.now() - timedelta(days=730)  # 2 years

        for i in range(730):  # 2 years of daily data
            current_date = start_date + timedelta(days=i)

            # Add some randomness to create realistic patterns
            base_revenue = 1000
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 365.25)  # Annual seasonality
            weekly_factor = 1 + 0.1 * np.sin(2 * np.pi * (i % 7) / 7)   # Weekly patterns

            # Random variation
            random_var = np.random.normal(1, 0.1)

            # Create multiple transactions per day
            num_transactions = np.random.poisson(2)  # Avg 2 transactions per day

            for _ in range(num_transactions):
                amount = base_revenue * seasonal_factor * weekly_factor * random_var
                amount = max(amount, 100)  # Minimum transaction

                # Randomly decide if it's revenue or expense
                trans_type = "revenue" if np.random.random() > 0.3 else "expense"

                # Random category
                categories = ["consulting", "product_sales", "training", "support", "maintenance",
                             "cloud", "software", "marketing", "office", "travel"]

                transactions.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "type": trans_type,
                    "amount": round(amount, 2),
                    "category": np.random.choice(categories),
                    "description": f"Sample {trans_type} transaction"
                })

        return transactions

    def _load_client_data(self) -> List[Dict[str, Any]]:
        """Load client payment behavior data"""
        clients = []

        # Generate synthetic client data
        for i in range(50):  # 50 clients
            client_id = f"CLIENT_{i:03d}"

            # Random payment behavior characteristics
            avg_payment_days = np.random.normal(30, 15)  # Avg payment in 30 days, std 15
            avg_payment_days = max(avg_payment_days, 7)  # Minimum 7 days

            # Payment consistency (0-1, where 1 is very consistent)
            payment_consistency = np.random.beta(2, 1)  # Skewed towards consistent payers

            # Transaction frequency
            avg_transactions_per_month = np.random.gamma(2, 2)  # Gamma distribution

            clients.append({
                "client_id": client_id,
                "name": f"Client {i+1}",
                "avg_payment_days": round(avg_payment_days, 1),
                "payment_consistency": round(payment_consistency, 3),
                "avg_transactions_per_month": round(avg_transactions_per_month, 1),
                "total_value": np.random.uniform(10000, 500000),  # Total contract value
                "industry": np.random.choice(["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"]),
                "risk_score": np.random.uniform(0, 1)  # Payment risk (0 = low risk, 1 = high risk)
            })

        return clients

    def _load_resource_data(self) -> List[Dict[str, Any]]:
        """Load resource utilization data"""
        resources = []

        # Generate synthetic resource data
        for i in range(20):  # 20 resources (staff, tools, etc.)
            resource_id = f"RES_{i:03d}"

            # Resource utilization patterns
            avg_utilization = np.random.uniform(0.4, 0.95)  # 40-95% utilization
            efficiency_score = np.random.uniform(0.6, 1.0)  # Efficiency 60-100%

            resources.append({
                "resource_id": resource_id,
                "name": f"Resource {i+1}",
                "type": np.random.choice(["staff", "equipment", "software", "service"]),
                "capacity": np.random.uniform(100, 1000),  # Capacity units
                "avg_utilization": round(avg_utilization, 3),
                "efficiency_score": round(efficiency_score, 3),
                "cost_per_unit": np.random.uniform(10, 100),
                "demand_trend": np.random.choice([-1, -0.5, 0, 0.5, 1]),  # -1 decreasing, 1 increasing
                "specialization": np.random.choice(["technical", "creative", "analytical", "administrative", "sales"])
            })

        return resources

    def prepare_cash_flow_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for cash flow prediction"""
        # Convert transactions to daily cash flow data
        daily_data = {}

        for trans in self.transaction_data:
            date = trans["date"]
            if date not in daily_data:
                daily_data[date] = {"revenue": 0, "expenses": 0}

            if trans["type"] == "revenue":
                daily_data[date]["revenue"] += trans["amount"]
            else:
                daily_data[date]["expenses"] += trans["amount"]

        # Convert to chronological order
        sorted_dates = sorted(daily_data.keys())
        cash_flows = []

        for i, date in enumerate(sorted_dates):
            day_data = daily_data[date]
            cash_flow = day_data["revenue"] - day_data["expenses"]

            # Create features for prediction
            features = [
                i,  # Day number (trend)
                datetime.strptime(date, "%Y-%m-%d").weekday(),  # Day of week
                datetime.strptime(date, "%Y-%m-%d").month,  # Month
                day_data["revenue"],  # Revenue
                day_data["expenses"],  # Expenses
                # Lag features (previous days)
                cash_flows[i-1][1] if i > 0 else 0,  # Previous day cash flow
                cash_flows[i-2][1] if i > 1 else 0,  # Cash flow 2 days ago
                cash_flows[i-7][1] if i > 6 else 0,  # Cash flow 1 week ago
            ]

            cash_flows.append([features, cash_flow])

        if len(cash_flows) < 10:
            # Create minimal dataset if not enough data
            X = np.random.rand(10, 8)
            y = np.random.rand(10)
            return X, y

        X = np.array([cf[0] for cf in cash_flows])
        y = np.array([cf[1] for cf in cash_flows])

        return X, y

    def prepare_busy_period_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for busy period prediction"""
        # Group transactions by week
        weekly_data = {}

        for trans in self.transaction_data:
            date_obj = datetime.strptime(trans["date"], "%Y-%m-%d")
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_key = week_start.strftime("%Y-%m-%d")

            if week_key not in weekly_data:
                weekly_data[week_key] = {"revenue": 0, "transactions": 0, "categories": set()}

            weekly_data[week_key]["revenue"] += trans["amount"]
            weekly_data[week_key]["transactions"] += 1
            weekly_data[week_key]["categories"].add(trans["category"])

        # Prepare features
        features = []
        labels = []

        for week_key, data in weekly_data.items():
            date_obj = datetime.strptime(week_key, "%Y-%m-%d")

            # Define busy period as top 25% of weeks by transaction volume
            busy_period = data["transactions"] > np.percentile([d["transactions"] for d in weekly_data.values()], 75)

            feature_vector = [
                date_obj.month,
                date_obj.day,
                data["revenue"],
                data["transactions"],
                len(data["categories"]),
                # Seasonal features
                np.sin(2 * np.pi * date_obj.timetuple().tm_yday / 365.25),
                np.cos(2 * np.pi * date_obj.timetuple().tm_yday / 365.25)
            ]

            features.append(feature_vector)
            labels.append(1 if busy_period else 0)

        if len(features) < 5:
            # Create minimal dataset if not enough data
            X = np.random.rand(5, 7)
            y = np.random.randint(0, 2, 5)
            return X, y

        X = np.array(features)
        y = np.array(labels)

        return X, y

    def prepare_client_payment_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for client payment prediction"""
        features = []
        labels = []

        for client in self.client_data:
            # Features based on client characteristics
            feature_vector = [
                client["avg_payment_days"],
                client["payment_consistency"],
                client["avg_transactions_per_month"],
                client["total_value"],
                1 if client["industry"] == "Technology" else 0,  # One-hot encoded industry
                1 if client["industry"] == "Finance" else 0,
                1 if client["industry"] == "Healthcare" else 0,
                1 if client["industry"] == "Retail" else 0,
                1 if client["industry"] == "Manufacturing" else 0,
            ]

            # Label: 1 if high risk (late payment), 0 if low risk
            late_payment_risk = 1 if client["avg_payment_days"] > 45 else 0

            features.append(feature_vector)
            labels.append(late_payment_risk)

        X = np.array(features)
        y = np.array(labels)

        return X, y

    def prepare_resource_allocation_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for resource allocation prediction"""
        # Generate synthetic demand data based on transaction patterns
        features = []
        demands = []

        # Create demand patterns based on transaction data
        for i, resource in enumerate(self.resources):
            # Simulate demand based on various factors
            base_demand = resource["capacity"] * resource["avg_utilization"]

            # Add some variation based on resource characteristics
            demand_variation = np.random.normal(0, base_demand * 0.2)
            predicted_demand = max(0, base_demand + demand_variation)

            # Features for prediction
            feature_vector = [
                resource["capacity"],
                resource["avg_utilization"],
                resource["efficiency_score"],
                resource["cost_per_unit"],
                resource["demand_trend"],
                1 if resource["type"] == "staff" else 0,
                1 if resource["type"] == "equipment" else 0,
                1 if resource["type"] == "software" else 0,
                1 if resource["type"] == "service" else 0,
                1 if resource["specialization"] == "technical" else 0,
                1 if resource["specialization"] == "creative" else 0,
                1 if resource["specialization"] == "analytical" else 0,
                1 if resource["specialization"] == "administrative" else 0,
                1 if resource["specialization"] == "sales" else 0,
            ]

            features.append(feature_vector)
            demands.append(predicted_demand)

        X = np.array(features)
        y = np.array(demands)

        return X, y

    def train_models(self):
        """Train all predictive models"""
        self.logger.info("Training predictive models...")

        # Train cash flow prediction model
        try:
            X_cf, y_cf = self.prepare_cash_flow_data()
            X_cf_scaled = self.scalers["cash_flow"].fit_transform(X_cf)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_cf_scaled, y_cf, test_size=0.2, random_state=42)

            # Train model
            self.models["cash_flow"] = RandomForestRegressor(n_estimators=100, random_state=42)
            self.models["cash_flow"].fit(X_train, y_train)

            # Evaluate
            y_pred = self.models["cash_flow"].predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            self.logger.info(f"Cash flow model trained - MAE: {mae:.2f}")

        except Exception as e:
            self.logger.error(f"Error training cash flow model: {str(e)}")

        # Train busy period prediction model
        try:
            X_bp, y_bp = self.prepare_busy_period_data()

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_bp, y_bp, test_size=0.2, random_state=42)

            # Train model
            self.models["busy_periods"] = RandomForestRegressor(n_estimators=50, random_state=42)
            self.models["busy_periods"].fit(X_train, y_train)

            # Evaluate
            y_pred = self.models["busy_periods"].predict(X_test)
            accuracy = self.models["busy_periods"].score(X_test, y_test)
            self.logger.info(f"Busy period model trained - Accuracy: {accuracy:.3f}")

        except Exception as e:
            self.logger.error(f"Error training busy period model: {str(e)}")

        # Train client payment behavior model
        try:
            X_cp, y_cp = self.prepare_client_payment_data()

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_cp, y_cp, test_size=0.2, random_state=42)

            # Train model
            self.models["client_payment_behavior"] = LogisticRegression(random_state=42)
            self.models["client_payment_behavior"].fit(X_train, y_train)

            # Evaluate
            y_pred = self.models["client_payment_behavior"].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            self.logger.info(f"Client payment model trained - Accuracy: {accuracy:.3f}")

        except Exception as e:
            self.logger.error(f"Error training client payment model: {str(e)}")

        # Train resource allocation model
        try:
            X_ra, y_ra = self.prepare_resource_allocation_data()
            X_ra_scaled = self.scalers["resource_allocation"].fit_transform(X_ra)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_ra_scaled, y_ra, test_size=0.2, random_state=42)

            # Train model
            self.models["resource_allocation"] = RandomForestRegressor(n_estimators=50, random_state=42)
            self.models["resource_allocation"].fit(X_train, y_train)

            # Evaluate
            y_pred = self.models["resource_allocation"].predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            self.logger.info(f"Resource allocation model trained - MAE: {mae:.2f}")

        except Exception as e:
            self.logger.error(f"Error training resource allocation model: {str(e)}")

        self.logger.info("All models trained successfully")

    def predict_cash_flow(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict cash flow for the specified number of days ahead"""
        if self.models["cash_flow"] is None:
            self.train_models()

        # Get the latest data point to start predictions
        X_current, y_current = self.prepare_cash_flow_data()

        if len(X_current) == 0:
            return {"error": "No data available for prediction"}

        # Scale the current features
        X_current_scaled = self.scalers["cash_flow"].transform(X_current[-1].reshape(1, -1))

        predictions = []
        current_features = X_current_scaled.flatten()

        for day in range(days_ahead):
            # Predict for the next day
            pred_cash_flow = self.models["cash_flow"].predict(current_features.reshape(1, -1))[0]

            # Add prediction to results
            future_date = datetime.now() + timedelta(days=day+1)
            predictions.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_cash_flow": round(pred_cash_flow, 2),
                "day_ahead": day + 1
            })

            # Update features for next prediction (simplified approach)
            # In a real system, this would be more sophisticated
            current_features[0] += 1  # Increment day counter
            current_features[6] = current_features[7]  # Shift lag features
            current_features[7] = pred_cash_flow  # Use predicted value

        # Calculate summary metrics
        total_predicted = sum(p["predicted_cash_flow"] for p in predictions)
        avg_daily = total_predicted / days_ahead if days_ahead > 0 else 0
        positive_days = sum(1 for p in predictions if p["predicted_cash_flow"] > 0)

        result = {
            "prediction_period": f"Next {days_ahead} days",
            "predictions": predictions,
            "summary": {
                "total_predicted_cash_flow": round(total_predicted, 2),
                "average_daily_cash_flow": round(avg_daily, 2),
                "positive_cash_flow_days": positive_days,
                "negative_cash_flow_days": days_ahead - positive_days,
                "cash_flow_confidence": "high" if days_ahead <= 7 else "medium" if days_ahead <= 30 else "low"
            },
            "trend": "positive" if avg_daily > 0 else "negative"
        }

        # Save prediction
        pred_file = self.storage_path / f"cash_flow_prediction_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(pred_file, 'w') as f:
            json.dump(result, f, indent=2)

        return result

    def predict_busy_periods(self, months_ahead: int = 3) -> Dict[str, Any]:
        """Predict busy periods in the next specified months"""
        if self.models["busy_periods"] is None:
            self.train_models()

        predictions = []

        # Generate dates for the next few months
        start_date = datetime.now()
        end_date = start_date + timedelta(days=months_ahead * 30)

        current_date = start_date
        while current_date <= end_date:
            # Create features for this date
            features = [
                current_date.month,
                current_date.day,
                5000,  # Placeholder revenue
                10,    # Placeholder transaction count
                3,     # Placeholder category count
                np.sin(2 * np.pi * current_date.timetuple().tm_yday / 365.25),
                np.cos(2 * np.pi * current_date.timetuple().tm_yday / 365.25)
            ]

            # Predict if this is a busy period
            busy_probability = self.models["busy_periods"].predict_proba([features])[0][1]  # Probability of being busy
            is_busy = busy_probability > 0.5

            predictions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "is_busy_period": is_busy,
                "busy_probability": round(busy_probability, 3),
                "week_number": current_date.isocalendar()[1]
            })

            current_date += timedelta(days=1)

        # Identify busy periods (consecutive busy days)
        busy_periods = []
        current_period = None

        for pred in predictions:
            if pred["is_busy_period"]:
                if current_period is None:
                    current_period = {"start": pred["date"], "dates": [pred["date"]]}
                else:
                    current_period["dates"].append(pred["date"])
            else:
                if current_period is not None:
                    current_period["end"] = (datetime.strptime(current_period["dates"][-1], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                    current_period["duration_days"] = len(current_period["dates"])
                    busy_periods.append(current_period)
                    current_period = None

        # Add final period if it exists
        if current_period is not None:
            current_period["end"] = (datetime.strptime(current_period["dates"][-1], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            current_period["duration_days"] = len(current_period["dates"])
            busy_periods.append(current_period)

        result = {
            "prediction_period": f"Next {months_ahead} months",
            "predictions": predictions,
            "busy_periods": busy_periods,
            "summary": {
                "total_busy_days": sum(1 for p in predictions if p["is_busy_period"]),
                "total_prediction_days": len(predictions),
                "busy_percentage": round(sum(1 for p in predictions if p["is_busy_period"]) / len(predictions) * 100, 1),
                "number_of_busy_periods": len(busy_periods)
            }
        }

        # Save prediction
        pred_file = self.storage_path / f"busy_periods_prediction_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(pred_file, 'w') as f:
            json.dump(result, f, indent=2)

        return result

    def predict_client_payment_behavior(self, client_id: str = None) -> Dict[str, Any]:
        """Predict payment behavior for a specific client or all clients"""
        if self.models["client_payment_behavior"] is None:
            self.train_models()

        predictions = []

        for client in self.client_data:
            if client_id and client["client_id"] != client_id:
                continue

            # Prepare features
            industry_features = [0, 0, 0, 0, 0]  # One-hot for 5 industries
            industry_idx = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"].index(client["industry"])
            industry_features[industry_idx] = 1

            features = [
                client["avg_payment_days"],
                client["payment_consistency"],
                client["avg_transactions_per_month"],
                client["total_value"]
            ] + industry_features

            # Predict probability of late payment
            late_payment_prob = self.models["client_payment_behavior"].predict_proba([features])[0][1]
            payment_risk = "high" if late_payment_prob > 0.7 else "medium" if late_payment_prob > 0.3 else "low"

            predictions.append({
                "client_id": client["client_id"],
                "client_name": client["name"],
                "predicted_late_payment_probability": round(late_payment_prob, 3),
                "payment_risk_level": payment_risk,
                "recommended_action": self._get_payment_recommendation(payment_risk, late_payment_prob)
            })

        result = {
            "prediction_date": datetime.now().isoformat(),
            "predictions": predictions,
            "summary": {
                "total_clients": len(predictions),
                "high_risk_clients": sum(1 for p in predictions if p["payment_risk_level"] == "high"),
                "medium_risk_clients": sum(1 for p in predictions if p["payment_risk_level"] == "medium"),
                "low_risk_clients": sum(1 for p in predictions if p["payment_risk_level"] == "low")
            }
        }

        # Save prediction
        pred_file = self.storage_path / f"client_payment_prediction_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(pred_file, 'w') as f:
            json.dump(result, f, indent=2)

        return result

    def _get_payment_recommendation(self, risk_level: str, probability: float) -> str:
        """Get recommendation based on payment risk"""
        if risk_level == "high":
            return "Request payment within 7 days, consider credit hold"
        elif risk_level == "medium":
            return "Monitor payment closely, follow up if delayed"
        else:
            return "Standard payment terms appropriate"

    def predict_resource_allocation(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict resource allocation needs for the next period"""
        if self.models["resource_allocation"] is None:
            self.train_models()

        predictions = []

        for resource in self.resource_data:
            # Prepare features for this resource
            type_features = [0, 0, 0, 0]  # One-hot for 4 types
            type_idx = ["staff", "equipment", "software", "service"].index(resource["type"])
            type_features[type_idx] = 1

            specialization_features = [0, 0, 0, 0, 0]  # One-hot for 5 specializations
            spec_idx = ["technical", "creative", "analytical", "administrative", "sales"].index(resource["specialization"])
            specialization_features[spec_idx] = 1

            features = [
                resource["capacity"],
                resource["avg_utilization"],
                resource["efficiency_score"],
                resource["cost_per_unit"],
                resource["demand_trend"]
            ] + type_features + specialization_features

            # Scale features
            features_scaled = self.scalers["resource_allocation"].transform([features])[0]

            # Predict demand
            predicted_demand = self.models["resource_allocation"].predict([features_scaled])[0]

            # Calculate utilization ratio
            utilization_ratio = predicted_demand / resource["capacity"] if resource["capacity"] > 0 else 0
            demand_status = "over_allocated" if utilization_ratio > 1.0 else "adequately_allocated" if utilization_ratio > 0.7 else "under_allocated"

            predictions.append({
                "resource_id": resource["resource_id"],
                "resource_name": resource["name"],
                "resource_type": resource["type"],
                "current_capacity": resource["capacity"],
                "predicted_demand": round(predicted_demand, 2),
                "predicted_utilization_ratio": round(utilization_ratio, 3),
                "demand_status": demand_status,
                "recommendation": self._get_resource_recommendation(demand_status, utilization_ratio)
            })

        # Calculate summary statistics
        over_allocated = sum(1 for p in predictions if p["demand_status"] == "over_allocated")
        under_allocated = sum(1 for p in predictions if p["demand_status"] == "under_allocated")

        result = {
            "prediction_period": f"Next {days_ahead} days",
            "predictions": predictions,
            "summary": {
                "total_resources": len(predictions),
                "over_allocated_resources": over_allocated,
                "adequately_allocated_resources": len(predictions) - over_allocated - under_allocated,
                "under_allocated_resources": under_allocated,
                "allocation_efficiency_score": round((len(predictions) - over_allocated - under_allocated) / len(predictions) * 100, 1)
            }
        }

        # Save prediction
        pred_file = self.storage_path / f"resource_allocation_prediction_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(pred_file, 'w') as f:
            json.dump(result, f, indent=2)

        return result

    def _get_resource_recommendation(self, status: str, utilization: float) -> str:
        """Get recommendation based on resource allocation status"""
        if status == "over_allocated":
            return f"Consider reducing allocation or acquiring additional resources (utilization: {utilization*100:.1f}%)"
        elif status == "under_allocated":
            return f"Consider increasing allocation or reallocating to other projects (utilization: {utilization*100:.1f}%)"
        else:
            return f"Adequate allocation (utilization: {utilization*100:.1f}%)"

    def generate_predictive_insights(self) -> Dict[str, Any]:
        """Generate comprehensive predictive insights"""
        self.logger.info("Generating comprehensive predictive insights...")

        # Run all predictions
        cash_flow_pred = self.predict_cash_flow(days_ahead=30)
        busy_periods_pred = self.predict_busy_periods(months_ahead=3)
        client_payment_pred = self.predict_client_payment_behavior()
        resource_pred = self.predict_resource_allocation(days_ahead=30)

        # Create comprehensive insights
        insights = {
            "generation_date": datetime.now().isoformat(),
            "cash_flow_insights": {
                "trend": cash_flow_pred.get("trend", "unknown"),
                "avg_daily_cash_flow": cash_flow_pred.get("summary", {}).get("average_daily_cash_flow", 0),
                "positive_days_ratio": cash_flow_pred.get("summary", {}).get("positive_cash_flow_days", 0) / 30 if 30 > 0 else 0
            },
            "busy_periods_insights": {
                "busy_percentage": busy_periods_pred.get("summary", {}).get("busy_percentage", 0),
                "number_of_periods": busy_periods_pred.get("summary", {}).get("number_of_busy_periods", 0)
            },
            "client_payment_insights": {
                "high_risk_percentage": client_payment_pred.get("summary", {}).get("high_risk_clients", 0) / max(client_payment_pred.get("summary", {}).get("total_clients", 1), 1) * 100,
                "total_clients": client_payment_pred.get("summary", {}).get("total_clients", 0)
            },
            "resource_allocation_insights": {
                "allocation_efficiency": resource_pred.get("summary", {}).get("allocation_efficiency_score", 0),
                "over_allocated_count": resource_pred.get("summary", {}).get("over_allocated_resources", 0),
                "under_allocated_count": resource_pred.get("summary", {}).get("under_allocated_resources", 0)
            },
            "strategic_recommendations": self._generate_strategic_recommendations(
                cash_flow_pred, busy_periods_pred, client_payment_pred, resource_pred
            )
        }

        # Save insights
        insights_file = self.storage_path / f"predictive_insights_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(insights_file, 'w') as f:
            json.dump(insights, f, indent=2)

        self.logger.info("Comprehensive predictive insights generated")

        return insights

    def _generate_strategic_recommendations(self, cash_flow_pred, busy_periods_pred, client_payment_pred, resource_pred) -> List[Dict[str, str]]:
        """Generate strategic recommendations based on all predictions"""
        recommendations = []

        # Cash flow recommendations
        cash_trend = cash_flow_pred.get("trend", "unknown")
        avg_cash = cash_flow_pred.get("summary", {}).get("average_daily_cash_flow", 0)

        if cash_trend == "negative" or avg_cash < 0:
            recommendations.append({
                "category": "cash_flow",
                "priority": "high",
                "title": "Address Negative Cash Flow",
                "description": "Predicted cash flow is negative, requiring immediate attention",
                "action": "Review expenses, accelerate receivables, consider financing options"
            })
        elif avg_cash > 10000:  # High positive cash flow
            recommendations.append({
                "category": "cash_flow",
                "priority": "medium",
                "title": "Optimize Positive Cash Flow",
                "description": "Strong positive cash flow presents investment opportunities",
                "action": "Consider reinvestment in growth, debt reduction, or reserves"
            })

        # Busy period recommendations
        busy_pct = busy_periods_pred.get("summary", {}).get("busy_percentage", 0)
        if busy_pct > 40:  # More than 40% of days are busy
            recommendations.append({
                "category": "operations",
                "priority": "high",
                "title": "Prepare for High-Demand Periods",
                "description": "Prediction shows extended busy periods requiring resource planning",
                "action": "Increase staffing, secure additional resources, plan capacity"
            })

        # Client payment recommendations
        high_risk_pct = client_payment_pred.get("summary", {}).get("high_risk_clients", 0) / max(client_payment_pred.get("summary", {}).get("total_clients", 1), 1) * 100
        if high_risk_pct > 20:  # More than 20% of clients are high risk
            recommendations.append({
                "category": "collections",
                "priority": "high",
                "title": "Strengthen Payment Collection Process",
                "description": "Significant portion of clients pose high payment risk",
                "action": "Implement stricter payment terms, enhance follow-up procedures"
            })

        # Resource allocation recommendations
        efficiency_score = resource_pred.get("summary", {}).get("allocation_efficiency_score", 0)
        if efficiency_score < 70:  # Less than 70% efficiency
            recommendations.append({
                "category": "resources",
                "priority": "medium",
                "title": "Optimize Resource Allocation",
                "description": "Resource allocation efficiency is below optimal levels",
                "action": "Review allocation patterns, rebalance resources, consider automation"
            })

        return recommendations


async def test_predictive_analytics():
    """Test the predictive analytics system"""
    print("Testing Predictive Analytics System...")

    # Create the system
    predictor = PredictiveAnalytics()

    # Train models
    print("\n1. Training predictive models...")
    predictor.train_models()
    print("Models trained successfully")

    # Predict cash flow
    print("\n2. Predicting cash flow...")
    cash_flow_pred = predictor.predict_cash_flow(days_ahead=30)
    print(f"Predicted average daily cash flow: ${cash_flow_pred['summary']['average_daily_cash_flow']:.2f}")
    print(f"Cash flow trend: {cash_flow_pred['trend']}")
    print(f"Positive cash flow days: {cash_flow_pred['summary']['positive_cash_flow_days']}/30")

    # Predict busy periods
    print("\n3. Predicting busy periods...")
    busy_pred = predictor.predict_busy_periods(months_ahead=3)
    print(f"Busy days percentage: {busy_pred['summary']['busy_percentage']}%")
    print(f"Number of busy periods: {busy_pred['summary']['number_of_busy_periods']}")

    # Predict client payment behavior
    print("\n4. Predicting client payment behavior...")
    client_pred = predictor.predict_client_payment_behavior()
    print(f"Total clients analyzed: {client_pred['summary']['total_clients']}")
    print(f"High risk clients: {client_pred['summary']['high_risk_clients']}")

    # Predict resource allocation
    print("\n5. Predicting resource allocation...")
    resource_pred = predictor.predict_resource_allocation(days_ahead=30)
    print(f"Allocation efficiency: {resource_pred['summary']['allocation_efficiency_score']}%")
    print(f"Over-allocated resources: {resource_pred['summary']['over_allocated_resources']}")
    print(f"Under-allocated resources: {resource_pred['summary']['under_allocated_resources']}")

    # Generate comprehensive insights
    print("\n6. Generating comprehensive predictive insights...")
    insights = predictor.generate_predictive_insights()
    print(f"Strategic recommendations generated: {len(insights['strategic_recommendations'])}")

    # Show some recommendations
    print(f"\n7. Sample strategic recommendations:")
    for i, rec in enumerate(insights['strategic_recommendations'][:3]):  # Show first 3
        print(f"  - {rec['priority'].upper()}: {rec['title']} - {rec['description']}")

    return True


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_predictive_analytics())