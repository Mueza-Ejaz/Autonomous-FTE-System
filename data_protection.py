"""
Data Protection System for Gold Tier
Manages encryption, data minimization, privacy controls, and secure data handling.
"""

import json
import asyncio
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os


class DataProtection:
    """System for protecting data through encryption, minimization, and privacy controls"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create data protection directories
        (self.storage_path / "Audit_Logs").mkdir(exist_ok=True)
        (self.storage_path / "Encryption_Keys").mkdir(exist_ok=True)
        (self.storage_path / "Data_Classification").mkdir(exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Initialize encryption
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)

        # Initialize data classification system
        self.classification_rules = self._load_classification_rules()
        self.data_inventory = self._load_data_inventory()

        # Initialize privacy controls
        self.privacy_settings = self._load_privacy_settings()

    def _setup_logging(self) -> logging.Logger:
        """Set up data protection logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "data_protection.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _get_or_create_encryption_key(self) -> bytes:
        """Get existing encryption key or create a new one"""
        key_file = self.storage_path / "Encryption_Keys" / "master.key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create a new key
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            self.logger.info("Created new encryption key")
            return key

    def _load_classification_rules(self) -> Dict[str, Any]:
        """Load data classification rules"""
        rules_file = self.storage_path / "Data_Classification" / "classification_rules.json"

        default_rules = {
            "data_patterns": {
                "personal_identifiers": [
                    "ssn", "social_security", "national_id", "passport", "driver_license"
                ],
                "financial_data": [
                    "credit_card", "bank_account", "routing_number", "paypal", "stripe"
                ],
                "health_information": [
                    "medical_record", "health_insurance", "patient_id", "diagnosis", "treatment"
                ],
                "biometric_data": [
                    "fingerprint", "face_scan", "iris_scan", "voice_print", "dna"
                ],
                "credentials": [
                    "password", "api_key", "access_token", "refresh_token", "secret"
                ]
            },
            "classification_levels": {
                "public": {
                    "description": "Publicly available information",
                    "handling_requirements": "No special handling required",
                    "retention_period_days": 3650,
                    "encryption_required": False
                },
                "internal": {
                    "description": "Internal business information",
                    "handling_requirements": "Access limited to employees",
                    "retention_period_days": 1825,
                    "encryption_required": True
                },
                "confidential": {
                    "description": "Confidential business information",
                    "handling_requirements": "Need-to-know basis only",
                    "retention_period_days": 730,
                    "encryption_required": True
                },
                "restricted": {
                    "description": "Highly sensitive information",
                    "handling_requirements": "Strict access controls, audit required",
                    "retention_period_days": 365,
                    "encryption_required": True
                }
            }
        }

        if rules_file.exists():
            with open(rules_file, 'r') as f:
                return json.load(f)
        else:
            # Create default rules file
            rules_file.parent.mkdir(parents=True, exist_ok=True)
            with open(rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            return default_rules

    def _load_data_inventory(self) -> Dict[str, Any]:
        """Load data inventory"""
        inventory_file = self.storage_path / "Data_Classification" / "data_inventory.json"

        default_inventory = {
            "datasets": {},
            "last_scanned": datetime.now().isoformat(),
            "total_datasets": 0,
            "sensitive_datasets": 0
        }

        if inventory_file.exists():
            with open(inventory_file, 'r') as f:
                return json.load(f)
        else:
            # Create default inventory file
            with open(inventory_file, 'w') as f:
                json.dump(default_inventory, f, indent=2)
            return default_inventory

    def _load_privacy_settings(self) -> Dict[str, Any]:
        """Load privacy settings"""
        settings_file = self.storage_path / "Data_Classification" / "privacy_settings.json"

        default_settings = {
            "data_minimization_enabled": True,
            "automatic_deletion_enabled": True,
            "retention_periods": {
                "temporary_data": 30,
                "user_sessions": 90,
                "logs": 180,
                "backups": 365
            },
            "privacy_controls": {
                "anonymization_enabled": True,
                "pseudonymization_enabled": True,
                "data_masking_enabled": True
            }
        }

        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        else:
            # Create default settings file
            with open(settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
            return default_settings

    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data using Fernet symmetric encryption"""
        if isinstance(data, str):
            data = data.encode()

        encrypted_data = self.cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet symmetric encryption"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()

    def classify_data(self, data: Union[str, Dict, List]) -> Dict[str, Any]:
        """Classify data based on content patterns and sensitivity"""
        classification_result = {
            "classification_level": "public",
            "sensitivity_score": 0,
            "identified_patterns": [],
            "recommended_actions": [],
            "pii_detected": False,
            "financial_data_detected": False,
            "health_data_detected": False
        }

        # Convert data to string for pattern matching
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, default=str)
        else:
            data_str = str(data).lower()

        # Check for sensitive patterns
        sensitivity_score = 0

        # Check for personal identifiers
        for pattern in self.classification_rules["data_patterns"]["personal_identifiers"]:
            if pattern in data_str:
                classification_result["identified_patterns"].append(pattern)
                classification_result["pii_detected"] = True
                sensitivity_score += 30
                if classification_result["classification_level"] == "public":
                    classification_result["classification_level"] = "restricted"

        # Check for financial data
        for pattern in self.classification_rules["data_patterns"]["financial_data"]:
            if pattern in data_str:
                classification_result["identified_patterns"].append(pattern)
                classification_result["financial_data_detected"] = True
                sensitivity_score += 25
                if classification_result["classification_level"] in ["public", "internal"]:
                    classification_result["classification_level"] = "confidential"

        # Check for health information
        for pattern in self.classification_rules["data_patterns"]["health_information"]:
            if pattern in data_str:
                classification_result["identified_patterns"].append(pattern)
                classification_result["health_data_detected"] = True
                sensitivity_score += 35
                classification_result["classification_level"] = "restricted"

        # Check for credentials
        for pattern in self.classification_rules["data_patterns"]["credentials"]:
            if pattern in data_str:
                classification_result["identified_patterns"].append(pattern)
                sensitivity_score += 40
                classification_result["classification_level"] = "restricted"

        classification_result["sensitivity_score"] = min(sensitivity_score, 100)

        # Add recommended actions based on classification
        if classification_result["classification_level"] == "restricted":
            classification_result["recommended_actions"].extend([
                "Encrypt all instances of this data",
                "Implement strict access controls",
                "Enable audit logging for access",
                "Apply data loss prevention controls"
            ])
        elif classification_result["classification_level"] == "confidential":
            classification_result["recommended_actions"].extend([
                "Encrypt data at rest and in transit",
                "Limit access to authorized personnel",
                "Apply retention policies"
            ])
        elif classification_result["classification_level"] == "internal":
            classification_result["recommended_actions"].extend([
                "Apply access controls",
                "Monitor access patterns"
            ])

        return classification_result

    def protect_sensitive_data(self, data: Any, classification: str = None) -> Dict[str, Any]:
        """Protect sensitive data based on classification"""
        if classification is None:
            classification_result = self.classify_data(data)
            classification = classification_result["classification_level"]
        else:
            classification_result = {"classification_level": classification}

        protected_data = data
        protection_applied = []

        if classification in ["confidential", "restricted"]:
            # Apply encryption
            if isinstance(data, str):
                protected_data = self.encrypt_data(data)
                protection_applied.append("encryption")
            elif isinstance(data, (dict, list)):
                protected_data = self._encrypt_nested_data(data)
                protection_applied.append("encryption")

        # Apply data minimization if enabled
        if self.privacy_settings["data_minimization_enabled"]:
            minimized_data = self._apply_data_minimization(protected_data, classification)
            if minimized_data != protected_data:
                protected_data = minimized_data
                protection_applied.append("minimization")

        result = {
            "original_data": data,
            "protected_data": protected_data,
            "classification": classification,
            "protection_applied": protection_applied,
            "needs_additional_protection": classification in ["confidential", "restricted"]
        }

        # Log protection action
        self.logger.info(f"Applied protection {protection_applied} for classification {classification}")

        return result

    def _encrypt_nested_data(self, data: Union[Dict, List]) -> Union[Dict, List]:
        """Recursively encrypt nested data structures"""
        if isinstance(data, dict):
            encrypted_dict = {}
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    if isinstance(value, str) and len(value) > 10:  # Likely sensitive string
                        encrypted_dict[key] = self.encrypt_data(str(value))
                    else:
                        encrypted_dict[key] = value
                elif isinstance(value, (dict, list)):
                    encrypted_dict[key] = self._encrypt_nested_data(value)
                else:
                    encrypted_dict[key] = value
            return encrypted_dict
        elif isinstance(data, list):
            encrypted_list = []
            for item in data:
                if isinstance(item, (str, int, float, bool)):
                    if isinstance(item, str) and len(item) > 10:  # Likely sensitive string
                        encrypted_list.append(self.encrypt_data(item))
                    else:
                        encrypted_list.append(item)
                elif isinstance(item, (dict, list)):
                    encrypted_list.append(self._encrypt_nested_data(item))
                else:
                    encrypted_list.append(item)
            return encrypted_list
        else:
            return data

    def _apply_data_minimization(self, data: Any, classification: str) -> Any:
        """Apply data minimization principles"""
        if classification not in ["confidential", "restricted"]:
            return data

        if isinstance(data, dict):
            minimized = {}
            # Keep only essential fields based on classification
            for key, value in data.items():
                # Skip certain fields that might be too sensitive
                if key.lower() in ["password", "secret", "token", "key", "credential"]:
                    continue
                elif isinstance(value, str) and len(value) > 1000:  # Very long strings might be minimized
                    minimized[key] = value[:100] + "..."  # Truncate long strings
                else:
                    minimized[key] = value
            return minimized
        elif isinstance(data, str) and len(data) > 1000:
            # For very long strings, consider truncating
            return data[:500] + "..."
        else:
            return data

    def anonymize_data(self, data: Union[Dict, List, str]) -> Union[Dict, List, str]:
        """Anonymize data by removing or obfuscating personally identifiable information"""
        if not self.privacy_settings["privacy_controls"]["anonymization_enabled"]:
            return data

        if isinstance(data, str):
            # Simple pattern replacement for strings
            import re
            # Replace email addresses
            data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', data)
            # Replace potential phone numbers
            data = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', data)
            # Replace potential names (simple heuristic)
            data = re.sub(r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b', '[NAME]', data)
            return data
        elif isinstance(data, dict):
            anonymized_dict = {}
            for key, value in data.items():
                if isinstance(value, str):
                    anonymized_dict[key] = self.anonymize_data(value)
                elif isinstance(value, (dict, list)):
                    anonymized_dict[key] = self.anonymize_data(value)
                else:
                    anonymized_dict[key] = value
            return anonymized_dict
        elif isinstance(data, list):
            return [self.anonymize_data(item) for item in data]
        else:
            return data

    def pseudonymize_data(self, data: Union[Dict, List, str]) -> Union[Dict, List, str]:
        """Pseudonymize data by replacing identifying information with pseudonyms"""
        if not self.privacy_settings["privacy_controls"]["pseudonymization_enabled"]:
            return data

        if isinstance(data, str):
            import re
            # Create consistent pseudonyms for the same values
            import hashlib

            # Replace email addresses with pseudonyms
            def replace_email(match):
                email = match.group(0)
                hash_obj = hashlib.md5(email.encode())
                pseudonym = f"pseudonym_{hash_obj.hexdigest()[:8]}@example.com"
                return pseudonym

            data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', replace_email, data)
            return data
        elif isinstance(data, dict):
            pseudonymized_dict = {}
            for key, value in data.items():
                if isinstance(value, str):
                    pseudonymized_dict[key] = self.pseudonymize_data(value)
                elif isinstance(value, (dict, list)):
                    pseudonymized_dict[key] = self.pseudonymize_data(value)
                else:
                    pseudonymized_dict[key] = value
            return pseudonymized_dict
        elif isinstance(data, list):
            return [self.pseudonymize_data(item) for item in data]
        else:
            return data

    def scan_directory_for_sensitive_data(self, directory_path: str) -> Dict[str, Any]:
        """Scan a directory for sensitive data and classify it"""
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        scan_results = {
            "directory": str(directory),
            "scanned_files": 0,
            "sensitive_files_found": 0,
            "total_sensitive_items": 0,
            "findings": [],
            "scan_timestamp": datetime.now().isoformat()
        }

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.json', '.csv', '.log', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    classification = self.classify_data(content)
                    if classification["sensitivity_score"] > 0:
                        scan_results["sensitive_files_found"] += 1
                        scan_results["total_sensitive_items"] += len(classification["identified_patterns"])

                        scan_results["findings"].append({
                            "file_path": str(file_path),
                            "classification": classification["classification_level"],
                            "sensitivity_score": classification["sensitivity_score"],
                            "patterns_found": classification["identified_patterns"],
                            "pii_detected": classification["pii_detected"],
                            "financial_detected": classification["financial_data_detected"],
                            "health_detected": classification["health_data_detected"]
                        })

                    scan_results["scanned_files"] += 1

                    # Prevent excessive scanning
                    if scan_results["scanned_files"] > 1000:
                        scan_results["truncated"] = True
                        break

                except Exception as e:
                    self.logger.warning(f"Could not scan file {file_path}: {str(e)}")

        # Update data inventory
        self._update_data_inventory(scan_results)

        # Save scan results
        scan_file = self.storage_path / "Data_Classification" / f"data_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(scan_file, 'w') as f:
            json.dump(scan_results, f, indent=2)

        self.logger.info(f"Completed data scan of {directory_path}: {scan_results['scanned_files']} files, {scan_results['sensitive_files_found']} sensitive")

        return scan_results

    def _update_data_inventory(self, scan_results: Dict[str, Any]):
        """Update the data inventory with scan results"""
        for finding in scan_results["findings"]:
            file_path = finding["file_path"]
            self.data_inventory["datasets"][file_path] = {
                "classification": finding["classification"],
                "sensitivity_score": finding["sensitivity_score"],
                "patterns_found": finding["patterns_found"],
                "last_scanned": scan_results["scan_timestamp"],
                "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0
            }

        self.data_inventory["last_scanned"] = scan_results["scan_timestamp"]
        self.data_inventory["total_datasets"] = len(self.data_inventory["datasets"])
        self.data_inventory["sensitive_datasets"] = len([d for d in self.data_inventory["datasets"].values() if d["sensitivity_score"] > 0])

        # Save updated inventory
        inventory_file = self.storage_path / "Data_Classification" / "data_inventory.json"
        with open(inventory_file, 'w') as f:
            json.dump(self.data_inventory, f, indent=2)

    def apply_retention_policy(self, data_location: str, classification: str) -> bool:
        """Apply retention policy based on data classification"""
        retention_days = self.classification_rules["classification_levels"][classification]["retention_period_days"]

        # Calculate expiry date
        expiry_date = datetime.now() + timedelta(days=retention_days)

        # In a real implementation, this would manage the actual data lifecycle
        # For now, we'll just log the retention policy application

        self.logger.info(f"Applied retention policy for {data_location}: {retention_days} days (expires {expiry_date.strftime('%Y-%m-%d')})")
        return True

    def generate_data_map(self) -> Dict[str, Any]:
        """Generate a data map showing where sensitive data is located"""
        data_map = {
            "map_generated": datetime.now().isoformat(),
            "total_datasets": self.data_inventory["total_datasets"],
            "sensitive_datasets": self.data_inventory["sensitive_datasets"],
            "classification_distribution": {},
            "datasets": []
        }

        # Count classification distribution
        for dataset_info in self.data_inventory["datasets"].values():
            classification = dataset_info["classification"]
            data_map["classification_distribution"][classification] = data_map["classification_distribution"].get(classification, 0) + 1

        # Add dataset information
        for file_path, info in self.data_inventory["datasets"].items():
            data_map["datasets"].append({
                "file_path": file_path,
                "classification": info["classification"],
                "sensitivity_score": info["sensitivity_score"],
                "patterns_found": info["patterns_found"],
                "file_size": info["file_size"],
                "last_scanned": info["last_scanned"]
            })

        # Save data map
        map_file = self.storage_path / "Data_Classification" / f"data_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(map_file, 'w') as f:
            json.dump(data_map, f, indent=2)

        return data_map

    def create_data_processing_record(self, data_subject: str, data_categories: List[str],
                                   processing_purposes: List[str], legal_basis: str) -> str:
        """Create a record of data processing activities"""
        record = {
            "record_id": f"processing_record_{int(datetime.now().timestamp())}_{hash(data_subject) % 10000}",
            "data_subject": data_subject,
            "data_categories": data_categories,
            "processing_purposes": processing_purposes,
            "legal_basis": legal_basis,
            "processing_start_date": datetime.now().isoformat(),
            "data_recipients": [],
            "international_transfers": False,
            "retention_period": self.privacy_settings["retention_periods"].get("user_sessions", 90),
            "security_measures": ["encryption", "access_controls", "audit_logging"],
            "data_subject_rights": ["access", "rectification", "erasure", "portability"]
        }

        # Save processing record
        records_dir = self.storage_path / "Data_Classification" / "Processing_Records"
        records_dir.mkdir(exist_ok=True)

        record_file = records_dir / f"{record['record_id']}.json"
        with open(record_file, 'w') as f:
            json.dump(record, f, indent=2)

        self.logger.info(f"Created data processing record for {data_subject}")

        return record["record_id"]

    def conduct_privacy_impact_assessment(self, processing_activity: str) -> Dict[str, Any]:
        """Conduct a privacy impact assessment for a processing activity"""
        assessment = {
            "assessment_id": f"pia_{int(datetime.now().timestamp())}_{hash(processing_activity) % 10000}",
            "processing_activity": processing_activity,
            "assessment_date": datetime.now().isoformat(),
            "data_types_involved": [],
            "data_subjects": [],
            "purposes": [],
            "necessity_evaluation": {
                "lawful_basis_valid": True,
                "purpose_specified": True,
                "data_minimized": True,
                "storage_limitation_applied": True
            },
            "risk_assessment": {
                "high_risks": [],
                "medium_risks": [],
                "mitigation_measures": [],
                "residual_risk_level": "low"
            },
            "recommended_measures": [],
            "approval_status": "pending",
            "review_date": (datetime.now() + timedelta(days=365)).isoformat()
        }

        # Add some default risks based on processing activity
        if "personal" in processing_activity.lower():
            assessment["risk_assessment"]["medium_risks"].append("Risk of unauthorized access to personal data")
            assessment["recommended_measures"].append("Implement role-based access controls")
        if "financial" in processing_activity.lower():
            assessment["risk_assessment"]["high_risks"].append("Risk of financial fraud")
            assessment["recommended_measures"].append("Implement transaction monitoring")

        # Save assessment
        assessment_dir = self.storage_path / "Data_Classification" / "PIA_Assessments"
        assessment_dir.mkdir(exist_ok=True)

        assessment_file = assessment_dir / f"{assessment['assessment_id']}.json"
        with open(assessment_file, 'w') as f:
            json.dump(assessment, f, indent=2)

        self.logger.info(f"Conducted privacy impact assessment for {processing_activity}")

        return assessment

    def generate_privacy_compliance_report(self) -> str:
        """Generate a privacy compliance report"""
        report = {
            "report_date": datetime.now().isoformat(),
            "data_inventory_summary": {
                "total_datasets": self.data_inventory["total_datasets"],
                "sensitive_datasets": self.data_inventory["sensitive_datasets"],
                "by_classification": {}
            },
            "processing_activities": len(list((self.storage_path / "Data_Classification" / "Processing_Records").glob("*.json"))),
            "recent_pi_as": len(list((self.storage_path / "Data_Classification" / "PIA_Assessments").glob("*.json"))),
            "data_breaches": [],  # Would be populated from actual breach records
            "compliance_status": "partial",  # Would be calculated based on various factors
            "recommendations": [
                "Review and update data classification rules",
                "Conduct regular data discovery scans",
                "Implement automated retention policies",
                "Review and update privacy notices"
            ]
        }

        # Add classification distribution
        for dataset_info in self.data_inventory["datasets"].values():
            classification = dataset_info["classification"]
            report["data_inventory_summary"]["by_classification"][classification] = report["data_inventory_summary"]["by_classification"].get(classification, 0) + 1

        # Save report
        report_file = self.storage_path / "Data_Classification" / f"privacy_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Generated privacy compliance report: {report_file}")

        return str(report_file)

    def delete_personal_data(self, data_subject_id: str, categories_to_delete: List[str] = None) -> Dict[str, Any]:
        """Delete personal data for a data subject"""
        deletion_record = {
            "deletion_id": f"deletion_{int(datetime.now().timestamp())}_{hash(data_subject_id) % 10000}",
            "data_subject_id": data_subject_id,
            "categories_deleted": categories_to_delete or ["all"],
            "deletion_timestamp": datetime.now().isoformat(),
            "affected_datasets": [],
            "verification_status": "pending",
            "deletion_method": "secure_erase"
        }

        # In a real implementation, this would search for and delete the actual data
        # For now, we'll just simulate the deletion process
        for dataset_path, dataset_info in self.data_inventory["datasets"].items():
            if categories_to_delete is None or any(cat in dataset_info["patterns_found"] for cat in categories_to_delete):
                deletion_record["affected_datasets"].append({
                    "dataset_path": dataset_path,
                    "classification": dataset_info["classification"],
                    "sensitivity_score": dataset_info["sensitivity_score"]
                })

        # Save deletion record
        deletions_dir = self.storage_path / "Data_Classification" / "Deletion_Records"
        deletions_dir.mkdir(exist_ok=True)

        deletion_file = deletions_dir / f"{deletion_record['deletion_id']}.json"
        with open(deletion_file, 'w') as f:
            json.dump(deletion_record, f, indent=2)

        self.logger.info(f"Recorded data deletion request for {data_subject_id}")

        return deletion_record


async def test_data_protection():
    """Test the data protection system"""
    print("Testing Data Protection System...")

    dp = DataProtection()

    # Test data encryption
    print("\n1. Testing data encryption...")
    original_data = "This is sensitive information that needs encryption"
    encrypted = dp.encrypt_data(original_data)
    decrypted = dp.decrypt_data(encrypted)

    print(f"Original: {original_data}")
    print(f"Encrypted: {encrypted[:50]}...")  # Show first 50 chars
    print(f"Decrypted: {decrypted}")
    print(f"Encryption successful: {original_data == decrypted}")

    # Test data classification
    print("\n2. Testing data classification...")
    test_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "ssn": "123-45-6789",
        "credit_card": "4111-1111-1111-1111",
        "message": "This is a regular message"
    }

    classification = dp.classify_data(test_data)
    print(f"Classification level: {classification['classification_level']}")
    print(f"Sensitivity score: {classification['sensitivity_score']}")
    print(f"Identified patterns: {classification['identified_patterns']}")
    print(f"PII detected: {classification['pii_detected']}")
    print(f"Financial data detected: {classification['financial_data_detected']}")

    # Test data protection
    print("\n3. Testing data protection...")
    protected = dp.protect_sensitive_data(test_data)
    print(f"Protection applied: {protected['protection_applied']}")
    print(f"Needs additional protection: {protected['needs_additional_protection']}")

    # Test anonymization
    print("\n4. Testing data anonymization...")
    sensitive_text = "Contact John Doe at john.doe@example.com or call 555-123-4567"
    anonymized = dp.anonymize_data(sensitive_text)
    print(f"Original: {sensitive_text}")
    print(f"Anonymized: {anonymized}")

    # Test pseudonymization
    print("\n5. Testing data pseudonymization...")
    pseudonymized = dp.pseudonymize_data(sensitive_text)
    print(f"Original: {sensitive_text}")
    print(f"Pseudonymized: {pseudonymized}")

    # Test data processing record creation
    print("\n6. Testing data processing record creation...")
    record_id = dp.create_data_processing_record(
        "Customer Data Processing",
        ["personal_data", "financial_data"],
        ["service_provision", "billing"],
        "contract_performance"
    )
    print(f"Processing record created: {record_id}")

    # Generate a privacy compliance report
    print("\n7. Generating privacy compliance report...")
    report_file = dp.generate_privacy_compliance_report()
    print(f"Privacy compliance report generated: {report_file}")

    # Generate a data map
    print("\n8. Generating data map...")
    data_map = dp.generate_data_map()
    print(f"Data map generated with {data_map['total_datasets']} datasets")
    print(f"Sensitive datasets: {data_map['sensitive_datasets']}")
    print(f"Classification distribution: {data_map['classification_distribution']}")

    # Conduct a privacy impact assessment
    print("\n9. Conducting privacy impact assessment...")
    pia = dp.conduct_privacy_impact_assessment("Customer Account Management")
    print(f"PIA completed with {len(pia['recommended_measures'])} recommendations")
    print(f"High risks identified: {len(pia['risk_assessment']['high_risks'])}")

    # Show privacy settings
    print("\n10. Privacy settings:")
    print(f"Data minimization enabled: {dp.privacy_settings['data_minimization_enabled']}")
    print(f"Automatic deletion enabled: {dp.privacy_settings['automatic_deletion_enabled']}")
    print(f"Privacy controls: {dp.privacy_settings['privacy_controls']}")

    return True


if __name__ == "__main__":
    asyncio.run(test_data_protection())