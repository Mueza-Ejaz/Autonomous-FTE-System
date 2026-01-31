"""
Health Monitor for Gold Tier
Monitors system health, detects issues, and provides health metrics for the autonomous system.
"""

import asyncio
import json
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import os
import subprocess
import time
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class HealthComponent(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    MCP_SERVERS = "mcp_servers"
    FILESYSTEM = "filesystem"
    PROCESSES = "processes"


class HealthMonitor:
    """System health monitoring component"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security"):
        self.storage_path = Path(storage_path)
        (self.storage_path / "Audit_Logs").mkdir(parents=True, exist_ok=True)
        (self.storage_path / "Alerts").mkdir(exist_ok=True)

        # Initialize thresholds
        self.thresholds = {
            HealthComponent.CPU: {"warning": 70, "critical": 90},
            HealthComponent.MEMORY: {"warning": 75, "critical": 90},
            HealthComponent.DISK: {"warning": 80, "critical": 95},
            HealthComponent.NETWORK: {"warning": 50, "critical": 80},  # Mbps threshold
        }

        # Set up logging
        self.logger = self._setup_logging()

        # Component status cache
        self.component_status = {}
        self.health_history = []

        # Watched processes
        self.watched_processes = [
            "claude-code",
            "python",  # Our own processes
            "odoo",    # If running
        ]

    def _setup_logging(self) -> logging.Logger:
        """Set up health monitor logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "Alerts" / "health_monitor.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def get_cpu_health(self) -> Dict[str, Any]:
        """Get CPU health metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        status = HealthStatus.HEALTHY
        if cpu_percent > self.thresholds[HealthComponent.CPU]["critical"]:
            status = HealthStatus.CRITICAL
        elif cpu_percent > self.thresholds[HealthComponent.CPU]["warning"]:
            status = HealthStatus.WARNING

        return {
            "component": HealthComponent.CPU.value,
            "status": status.value,
            "metrics": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "load_average": [x / cpu_count * 100 for x in os.getloadavg()] if hasattr(os, 'getloadavg') else []
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_memory_health(self) -> Dict[str, Any]:
        """Get memory health metrics"""
        memory = psutil.virtual_memory()

        status = HealthStatus.HEALTHY
        if memory.percent > self.thresholds[HealthComponent.MEMORY]["critical"]:
            status = HealthStatus.CRITICAL
        elif memory.percent > self.thresholds[HealthComponent.MEMORY]["warning"]:
            status = HealthStatus.WARNING

        return {
            "component": HealthComponent.MEMORY.value,
            "status": status.value,
            "metrics": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "available_percent": 100 - memory.percent
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_disk_health(self) -> Dict[str, Any]:
        """Get disk health metrics"""
        # Use C: drive on Windows, root on Unix
        disk_path = 'C:\\' if os.name == 'nt' else '/'
        disk_usage = psutil.disk_usage(disk_path)

        status = HealthStatus.HEALTHY
        if disk_usage.percent > self.thresholds[HealthComponent.DISK]["critical"]:
            status = HealthStatus.CRITICAL
        elif disk_usage.percent > self.thresholds[HealthComponent.DISK]["warning"]:
            status = HealthStatus.WARNING

        return {
            "component": HealthComponent.DISK.value,
            "status": status.value,
            "metrics": {
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "usage_percent": disk_usage.percent
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_network_health(self) -> Dict[str, Any]:
        """Get network health metrics"""
        # Get initial network stats
        net_before = psutil.net_io_counters()
        time.sleep(1)
        net_after = psutil.net_io_counters()

        bytes_sent_per_sec = net_after.bytes_sent - net_before.bytes_sent
        bytes_recv_per_sec = net_after.bytes_recv - net_before.bytes_recv

        # Convert to Mbps
        mb_sent_per_sec = round((bytes_sent_per_sec * 8) / (1024 * 1024), 2)
        mb_recv_per_sec = round((bytes_recv_per_sec * 8) / (1024 * 1024), 2)

        # Determine status based on thresholds (these are arbitrary for demo)
        total_mb_per_sec = mb_sent_per_sec + mb_recv_per_sec
        status = HealthStatus.HEALTHY
        if total_mb_per_sec > self.thresholds[HealthComponent.NETWORK]["critical"]:
            status = HealthStatus.CRITICAL
        elif total_mb_per_sec > self.thresholds[HealthComponent.NETWORK]["warning"]:
            status = HealthStatus.WARNING

        return {
            "component": HealthComponent.NETWORK.value,
            "status": status.value,
            "metrics": {
                "bytes_sent_per_sec": bytes_sent_per_sec,
                "bytes_recv_per_sec": bytes_recv_per_sec,
                "mb_sent_per_sec": mb_sent_per_sec,
                "mb_recv_per_sec": mb_recv_per_sec,
                "total_mb_per_sec": total_mb_per_sec
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_process_health(self) -> Dict[str, Any]:
        """Get process health metrics"""
        critical_processes_found = 0
        watched_process_details = []

        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower()

                for watched_proc in self.watched_processes:
                    if watched_proc.lower() in proc_name:
                        watched_process_details.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "status": proc_info['status'],
                            "cpu_percent": proc_info['cpu_percent'],
                            "memory_percent": proc_info['memory_percent']
                        })
                        if proc_info['status'] in ['running', 'sleeping']:
                            critical_processes_found += 1
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process disappeared or access denied, skip
                continue

        status = HealthStatus.HEALTHY if critical_processes_found > 0 else HealthStatus.WARNING

        return {
            "component": HealthComponent.PROCESSES.value,
            "status": status.value,
            "metrics": {
                "critical_processes_running": critical_processes_found,
                "watched_processes": watched_process_details,
                "total_processes": len(list(psutil.process_iter()))
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance (placeholder)"""
        # This would connect to actual databases in a real implementation
        # For now, we'll simulate a healthy database connection

        status = HealthStatus.HEALTHY

        return {
            "component": HealthComponent.DATABASE.value,
            "status": status.value,
            "metrics": {
                "connected": True,
                "response_time_ms": 25,
                "connections": 5,
                "max_connections": 100
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_mcp_server_health(self) -> Dict[str, Any]:
        """Check MCP server health"""
        mcp_servers = [
            {"name": "email_mcp", "port": 8068, "expected_running": True},
            {"name": "odoo_mcp", "port": 8070, "expected_running": True},  # We created this for Gold tier
        ]

        healthy_servers = 0
        server_details = []

        for server in mcp_servers:
            try:
                # Try to connect to the port to see if it's running
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)  # 3 second timeout
                result = sock.connect_ex(('localhost', server['port']))
                sock.close()

                is_running = result == 0
                server_details.append({
                    "name": server['name'],
                    "port": server['port'],
                    "running": is_running,
                    "expected_running": server['expected_running']
                })

                if is_running:
                    healthy_servers += 1
            except Exception as e:
                server_details.append({
                    "name": server['name'],
                    "port": server['port'],
                    "running": False,
                    "expected_running": server['expected_running'],
                    "error": str(e)
                })

        status = HealthStatus.HEALTHY if healthy_servers == len(mcp_servers) else HealthStatus.WARNING

        return {
            "component": HealthComponent.MCP_SERVERS.value,
            "status": status.value,
            "metrics": {
                "healthy_servers": healthy_servers,
                "total_servers": len(mcp_servers),
                "servers": server_details
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        health_components = [
            self.get_cpu_health(),
            self.get_memory_health(),
            self.get_disk_health(),
            self.get_network_health(),
            self.get_process_health(),
            self.get_database_health(),
            self.get_mcp_server_health()
        ]

        # Determine overall status
        critical_count = sum(1 for comp in health_components if comp['status'] == HealthStatus.CRITICAL.value)
        warning_count = sum(1 for comp in health_components if comp['status'] == HealthStatus.WARNING.value)

        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL.value
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING.value
        else:
            overall_status = HealthStatus.HEALTHY.value

        # Add to history
        health_snapshot = {
            "overall_status": overall_status,
            "components": health_components,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "critical": critical_count,
                "warning": warning_count,
                "healthy": len(health_components) - critical_count - warning_count
            }
        }

        self.health_history.append(health_snapshot)
        if len(self.health_history) > 100:  # Keep last 100 snapshots
            self.health_history.pop(0)

        # Save to file
        health_file = self.storage_path / "Audit_Logs" / f"system_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(health_file, 'w') as f:
            json.dump(health_snapshot, f, indent=2)

        return health_snapshot

    def generate_health_report(self) -> str:
        """Generate a human-readable health report"""
        overall_health = self.get_overall_health()

        report_lines = [
            "# System Health Report",
            f"**Generated:** {overall_health['timestamp']}",
            f"**Overall Status:** {overall_health['overall_status'].upper()}",
            "",
            "## Component Status",
        ]

        for component in overall_health['components']:
            status = component['status'].upper()
            emoji = "✅" if status == "HEALTHY" else "⚠️" if status == "WARNING" else "🚨"
            report_lines.append(f"- {emoji} **{component['component'].title()}:** {status}")

        report_lines.extend([
            "",
            "## Detailed Metrics",
        ])

        for component in overall_health['components']:
            report_lines.append(f"### {component['component'].title()}")
            for key, value in component['metrics'].items():
                if isinstance(value, float):
                    report_lines.append(f"- **{key.replace('_', ' ').title()}:** {value:.2f}")
                elif isinstance(value, list):
                    report_lines.append(f"- **{key.replace('_', ' ').title()}:** {len(value)} items")
                else:
                    report_lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            report_lines.append("")  # Empty line after each component

        return "\n".join(report_lines)

    def check_for_alerts(self) -> List[Dict[str, Any]]:
        """Check for conditions that require alerts"""
        alerts = []
        overall_health = self.get_overall_health()

        # Check for critical status
        if overall_health['overall_status'] == HealthStatus.CRITICAL.value:
            alerts.append({
                "level": "critical",
                "message": "System is in critical health state",
                "components": [comp for comp in overall_health['components'] if comp['status'] == HealthStatus.CRITICAL.value],
                "timestamp": datetime.now().isoformat()
            })

        # Check individual components
        for component in overall_health['components']:
            if component['status'] in [HealthStatus.CRITICAL.value, HealthStatus.WARNING.value]:
                alerts.append({
                    "level": component['status'],
                    "message": f"{component['component']} is in {component['status']} state",
                    "component": component['component'],
                    "metrics": component['metrics'],
                    "timestamp": datetime.now().isoformat()
                })

        return alerts

    def create_alert_notification(self, alerts: List[Dict[str, Any]]) -> str:
        """Create an alert notification file"""
        if not alerts:
            return ""

        alert_file = Path("Vault/Needs_Action") / f"ALERT_System_Health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        alert_file.parent.mkdir(parents=True, exist_ok=True)

        with open(alert_file, 'w') as f:
            f.write(f"""---
type: alert
priority: high
category: system_health
generated: {datetime.now().isoformat()}
---

# 🚨 System Health Alert

## Alerts Summary
""")

            for alert in alerts:
                level = alert['level'].upper()
                f.write(f"- **{level}**: {alert['message']}\n")

            f.write(f"""

## Full Health Report
```
{self.generate_health_report()}
```

---
*Generated by Health Monitor System*
""")

        self.logger.warning(f"Created alert notification: {alert_file}")
        return str(alert_file)

    async def run_monitoring_loop(self, interval: int = 60):
        """Run continuous health monitoring"""
        self.logger.info("Starting health monitoring loop...")

        while True:
            try:
                # Get overall health
                health_snapshot = self.get_overall_health()

                # Log health status
                self.logger.info(f"System health: {health_snapshot['overall_status']} "
                               f"(Components: {health_snapshot['summary']})")

                # Check for alerts
                alerts = self.check_for_alerts()
                if alerts:
                    alert_file = self.create_alert_notification(alerts)
                    self.logger.warning(f"Health alerts generated: {len(alerts)} alerts, saved to {alert_file}")

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in health monitoring: {str(e)}")
                await asyncio.sleep(30)  # Wait shorter time if there's an error

    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        relevant_snapshots = [
            snap for snap in self.health_history
            if datetime.fromisoformat(snap['timestamp']) >= cutoff_time
        ]

        if not relevant_snapshots:
            return {"error": "No health data available for the specified time period"}

        # Calculate trends
        status_counts = {"healthy": 0, "warning": 0, "critical": 0}
        for snap in relevant_snapshots:
            status_counts[snap['overall_status']] += 1

        return {
            "time_period_hours": hours,
            "total_snapshots": len(relevant_snapshots),
            "status_distribution": status_counts,
            "latest_snapshot": relevant_snapshots[-1] if relevant_snapshots else None,
            "first_snapshot": relevant_snapshots[0] if relevant_snapshots else None
        }


async def test_health_monitor():
    """Test the health monitoring system"""
    print("Testing Health Monitor...")

    monitor = HealthMonitor()

    # Test individual component checks
    print("\n1. Testing individual component health checks...")

    cpu_health = monitor.get_cpu_health()
    print(f"CPU Health: {cpu_health['status']} - {cpu_health['metrics']['usage_percent']:.1f}%")

    memory_health = monitor.get_memory_health()
    print(f"Memory Health: {memory_health['status']} - {memory_health['metrics']['usage_percent']:.1f}%")

    disk_health = monitor.get_disk_health()
    print(f"Disk Health: {disk_health['status']} - {disk_health['metrics']['usage_percent']:.1f}%")

    network_health = monitor.get_network_health()
    print(f"Network Health: {network_health['status']} - {network_health['metrics']['total_mb_per_sec']:.2f} Mbps")

    process_health = monitor.get_process_health()
    print(f"Process Health: {process_health['status']} - {process_health['metrics']['critical_processes_running']} critical processes")

    # Test overall health
    print("\n2. Testing overall health check...")
    overall_health = monitor.get_overall_health()
    print(f"Overall Health: {overall_health['overall_status']}")
    print(f"Summary: {overall_health['summary']}")

    # Generate health report
    print("\n3. Generating health report...")
    report = monitor.generate_health_report()
    print("Health report generated (first 500 chars):")
    print(report[:500] + "..." if len(report) > 500 else report)

    # Check for alerts
    print("\n4. Checking for alerts...")
    alerts = monitor.check_for_alerts()
    print(f"Found {len(alerts)} alerts")

    # Get health trends
    print("\n5. Getting health trends...")
    trends = monitor.get_health_trends(hours=1)
    print(f"Health trends for last hour: {trends['status_distribution']}")

    return True


if __name__ == "__main__":
    asyncio.run(test_health_monitor())