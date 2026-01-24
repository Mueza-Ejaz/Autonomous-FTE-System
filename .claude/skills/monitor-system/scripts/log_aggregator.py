#!/usr/bin/env python3
"""
Log Aggregator Script
Handles log rotation, compression, and archiving
"""

import json
import gzip
import shutil
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tarfile


# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/AI_Employee_Vault'))
LOG_DIR = VAULT_PATH / 'Logs'

# Retention policies (days)
RETENTION_POLICIES = {
    'actions': {
        'active': 90,
        'compressed': 365,
        'permanent': False
    },
    'system': {
        'active': 60,
        'compressed': 180,
        'permanent': False
    },
    'financial': {
        'active': 2555,  # ~7 years
        'compressed': 2555,
        'permanent': True
    },
    'security': {
        'active': 365,
        'compressed': 2555,
        'permanent': True
    }
}


class LogAggregator:
    def __init__(self):
        self.today = datetime.now()
        self.stats = {
            'files_rotated': 0,
            'files_compressed': 0,
            'files_archived': 0,
            'space_freed_mb': 0
        }

    def create_daily_log_files(self):
        """Create new daily log files for today"""
        today_str = self.today.strftime('%Y-%m-%d')

        log_types = ['actions', 'system', 'security']
        for log_type in log_types:
            log_file = LOG_DIR / log_type / f'{today_str}.json'
            log_file.parent.mkdir(parents=True, exist_ok=True)

            if not log_file.exists():
                log_file.touch()
                print(f"Created new log file: {log_file}")
                self.stats['files_rotated'] += 1

        # Financial logs are monthly
        if self.today.day == 1:  # First of month
            month_str = self.today.strftime('%Y-%m')
            financial_log = LOG_DIR / 'financial' / f'{month_str}.json'
            financial_log.parent.mkdir(parents=True, exist_ok=True)
            if not financial_log.exists():
                financial_log.touch()
                print(f"Created new financial log: {financial_log}")
                self.stats['files_rotated'] += 1

    def compress_old_logs(self):
        """Compress logs older than 7 days"""
        cutoff_date = self.today - timedelta(days=7)

        log_types = ['actions', 'system', 'security']
        for log_type in log_types:
            log_dir = LOG_DIR / log_type
            if not log_dir.exists():
                continue

            for log_file in log_dir.glob('*.json'):
                # Skip if already compressed
                if log_file.suffix == '.gz':
                    continue

                # Check file age
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < cutoff_date:
                    self.compress_file(log_file)

    def compress_file(self, file_path: Path):
        """Compress a single file with gzip"""
        try:
            original_size = file_path.stat().st_size
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Verify compression worked
            if compressed_path.exists():
                compressed_size = compressed_path.stat().st_size
                file_path.unlink()  # Delete original

                space_freed = (original_size - compressed_size) / (1024 * 1024)  # MB
                self.stats['files_compressed'] += 1
                self.stats['space_freed_mb'] += space_freed

                print(f"Compressed: {file_path.name} ({space_freed:.2f} MB freed)")

        except Exception as e:
            print(f"Error compressing {file_path}: {str(e)}")

    def archive_old_compressed_logs(self):
        """Move old compressed logs to archives folder"""
        cutoff_date = self.today - timedelta(days=30)

        log_types = ['actions', 'system', 'security']
        for log_type in log_types:
            log_dir = LOG_DIR / log_type
            archive_dir = log_dir / 'archives'
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Find compressed logs older than 30 days
            for log_file in log_dir.glob('*.json.gz'):
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < cutoff_date:
                    dest = archive_dir / log_file.name
                    shutil.move(str(log_file), str(dest))
                    self.stats['files_archived'] += 1
                    print(f"Archived: {log_file.name}")

    def create_monthly_archives(self):
        """Create monthly tar.gz archives (run on first of month)"""
        if self.today.day != 1:
            return  # Only run on first day of month

        last_month = self.today - timedelta(days=1)
        month_str = last_month.strftime('%Y-%m')

        log_types = ['actions', 'system', 'security']
        for log_type in log_types:
            archive_dir = LOG_DIR / log_type / 'archives'
            if not archive_dir.exists():
                continue

            # Find all logs from last month
            month_files = list(archive_dir.glob(f'{month_str}-*.json.gz'))

            if month_files:
                archive_name = archive_dir / f'{month_str}.tar.gz'
                with tarfile.open(archive_name, 'w:gz') as tar:
                    for file in month_files:
                        tar.add(file, arcname=file.name)

                # Delete individual files after successful archive
                for file in month_files:
                    file.unlink()

                print(f"Created monthly archive: {archive_name.name}")

    def enforce_retention_policies(self):
        """Delete logs older than retention policy"""
        for log_type, policy in RETENTION_POLICIES.items():
            log_dir = LOG_DIR / log_type

            # Active logs retention
            active_cutoff = self.today - timedelta(days=policy['active'])
            for log_file in log_dir.glob('*.json'):
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < active_cutoff:
                    print(f"Deleting old active log: {log_file.name}")
                    log_file.unlink()

            # Compressed/archive retention
            if not policy['permanent']:
                archive_dir = log_dir / 'archives'
                if archive_dir.exists():
                    compressed_cutoff = self.today - timedelta(days=policy['compressed'])

                    for archive_file in archive_dir.glob('*'):
                        file_date = datetime.fromtimestamp(archive_file.stat().st_mtime)
                        if file_date < compressed_cutoff:
                            print(f"Deleting old archive: {archive_file.name}")
                            archive_file.unlink()

    def generate_log_stats(self) -> dict:
        """Generate statistics about log storage"""
        stats = {}

        for log_type in RETENTION_POLICIES.keys():
            log_dir = LOG_DIR / log_type

            if not log_dir.exists():
                continue

            # Count active logs
            active_logs = list(log_dir.glob('*.json'))
            active_size = sum(f.stat().st_size for f in active_logs)

            # Count compressed logs
            compressed_logs = list(log_dir.glob('*.json.gz'))
            compressed_size = sum(f.stat().st_size for f in compressed_logs)

            # Count archives
            archive_dir = log_dir / 'archives'
            archive_size = 0
            archive_count = 0
            if archive_dir.exists():
                archives = list(archive_dir.glob('*'))
                archive_size = sum(f.stat().st_size for f in archives)
                archive_count = len(archives)

            stats[log_type] = {
                'active_count': len(active_logs),
                'active_size_mb': active_size / (1024 * 1024),
                'compressed_count': len(compressed_logs),
                'compressed_size_mb': compressed_size / (1024 * 1024),
                'archive_count': archive_count,
                'archive_size_mb': archive_size / (1024 * 1024),
                'total_size_mb': (active_size + compressed_size + archive_size) / (1024 * 1024)
            }

        return stats

    def write_stats_report(self, stats: dict):
        """Write log statistics to a report file"""
        report_file = LOG_DIR / 'log_stats.md'

        report_content = f"""# Log Storage Statistics

**Generated:** {self.today.strftime('%Y-%m-%d %H:%M:%S')}

## Storage by Type

| Type | Active Logs | Compressed | Archives | Total Size |
|------|-------------|------------|----------|------------|
"""

        for log_type, data in stats.items():
            report_content += f"| {log_type} | {data['active_count']} ({data['active_size_mb']:.1f} MB) | {data['compressed_count']} ({data['compressed_size_mb']:.1f} MB) | {data['archive_count']} ({data['archive_size_mb']:.1f} MB) | {data['total_size_mb']:.1f} MB |\n"

        total_size = sum(data['total_size_mb'] for data in stats.values())
        report_content += f"""
**Total Storage Used:** {total_size:.1f} MB

## Retention Policies

| Type | Active | Compressed | Permanent |
|------|--------|------------|-----------|
"""

        for log_type, policy in RETENTION_POLICIES.items():
            report_content += f"| {log_type} | {policy['active']} days | {policy['compressed']} days | {'Yes' if policy['permanent'] else 'No'} |\n"

        report_content += f"""
## Recent Activity

- Files rotated: {self.stats['files_rotated']}
- Files compressed: {self.stats['files_compressed']}
- Files archived: {self.stats['files_archived']}
- Space freed: {self.stats['space_freed_mb']:.2f} MB

---
*Generated by monitor-system skill - log_aggregator.py*
"""

        report_file.write_text(report_content)
        print(f"Statistics report written to: {report_file}")

    def verify_log_integrity(self):
        """Verify that logs are being written correctly"""
        issues = []

        # Check that today's logs exist
        today_str = self.today.strftime('%Y-%m-%d')
        for log_type in ['actions', 'system', 'security']:
            log_file = LOG_DIR / log_type / f'{today_str}.json'
            if not log_file.exists():
                issues.append(f"Missing today's log: {log_file}")

        # Check that logs are valid JSON
        for log_type in ['actions', 'system', 'security']:
            log_dir = LOG_DIR / log_type
            if not log_dir.exists():
                continue

            for log_file in log_dir.glob('*.json'):
                try:
                    with open(log_file, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            if line.strip():  # Skip empty lines
                                json.loads(line)
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in {log_file.name} line {line_num}: {str(e)}")
                except Exception as e:
                    issues.append(f"Error reading {log_file.name}: {str(e)}")

        if issues:
            print("⚠️  Log integrity issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Log integrity check passed")

        return len(issues) == 0


def main():
    """Main log aggregation execution"""
    print(f"Starting log aggregation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    aggregator = LogAggregator()

    # 1. Create new daily log files
    print("\n1. Creating daily log files...")
    aggregator.create_daily_log_files()

    # 2. Compress old logs (>7 days)
    print("\n2. Compressing old logs...")
    aggregator.compress_old_logs()

    # 3. Archive compressed logs (>30 days)
    print("\n3. Archiving compressed logs...")
    aggregator.archive_old_compressed_logs()

    # 4. Create monthly archives (if first of month)
    print("\n4. Creating monthly archives...")
    aggregator.create_monthly_archives()

    # 5. Enforce retention policies
    print("\n5. Enforcing retention policies...")
    aggregator.enforce_retention_policies()

    # 6. Verify log integrity
    print("\n6. Verifying log integrity...")
    aggregator.verify_log_integrity()

    # 7. Generate and write statistics
    print("\n7. Generating statistics...")
    stats = aggregator.generate_log_stats()
    aggregator.write_stats_report(stats)

    # Print summary
    print("\n" + "="*50)
    print("Log Aggregation Complete")
    print("="*50)
    print(f"Files rotated: {aggregator.stats['files_rotated']}")
    print(f"Files compressed: {aggregator.stats['files_compressed']}")
    print(f"Files archived: {aggregator.stats['files_archived']}")
    print(f"Space freed: {aggregator.stats['space_freed_mb']:.2f} MB")
    print("="*50)


if __name__ == '__main__':
    main()
