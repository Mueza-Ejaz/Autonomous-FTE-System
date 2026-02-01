"""
Permission Manager for Gold Tier
Manages role-based access control, permissions, and authorization for the system.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import logging
from enum import Enum


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    DELETE = "delete"
    MODIFY_PERMISSIONS = "modify_permissions"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_USERS = "manage_users"
    ACCESS_SENSITIVE_DATA = "access_sensitive_data"
    BYPASS_APPROVAL = "bypass_approval"


class Role(Enum):
    GUEST = "guest"
    USER = "user"
    POWER_USER = "power_user"
    ADMIN = "admin"
    SYSTEM = "system"
    AUDITOR = "auditor"


class ResourceType(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"
    CONFIG = "config"
    LOG = "log"
    SYSTEM = "system"


class PermissionManager:
    """System for managing permissions and access control"""

    def __init__(self, storage_path: str = "AI_Employee_Vault/Gold_Tier/Security/Compliance"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Initialize permission data
        self.users = self._load_users()
        self.roles = self._load_roles()
        self.permissions = self._load_permissions()
        self.role_assignments = self._load_role_assignments()
        self.resource_permissions = self._load_resource_permissions()

    def _setup_logging(self) -> logging.Logger:
        """Set up permission manager logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = self.storage_path / "permission_manager.log"
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load user information"""
        users_file = self.storage_path / "users.json"

        default_users = {
            "system": {
                "name": "System Account",
                "role": "system",
                "permissions": ["admin", "access_sensitive_data"],
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "active": True
            },
            "admin": {
                "name": "Administrator",
                "role": "admin",
                "permissions": ["admin", "manage_users", "view_audit_logs"],
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "active": True
            }
        }

        if users_file.exists():
            with open(users_file, 'r') as f:
                return json.load(f)
        else:
            # Create default users file
            with open(users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
            return default_users

    def _load_roles(self) -> Dict[str, Dict[str, Any]]:
        """Load role definitions"""
        roles_file = self.storage_path / "roles.json"

        default_roles = {
            "guest": {
                "permissions": ["read"],
                "description": "Basic read-only access"
            },
            "user": {
                "permissions": ["read", "write"],
                "description": "Standard user with read/write access"
            },
            "power_user": {
                "permissions": ["read", "write", "execute"],
                "description": "Power user with execution privileges"
            },
            "admin": {
                "permissions": ["read", "write", "execute", "delete", "admin", "modify_permissions", "manage_users", "view_audit_logs"],
                "description": "Administrator with full access"
            },
            "system": {
                "permissions": ["admin", "access_sensitive_data", "bypass_approval"],
                "description": "System account with maximum privileges"
            },
            "auditor": {
                "permissions": ["read", "view_audit_logs"],
                "description": "Audit access only"
            }
        }

        if roles_file.exists():
            with open(roles_file, 'r') as f:
                return json.load(f)
        else:
            # Create default roles file
            with open(roles_file, 'w') as f:
                json.dump(default_roles, f, indent=2)
            return default_roles

    def _load_permissions(self) -> Dict[str, Dict[str, Any]]:
        """Load permission definitions"""
        permissions_file = self.storage_path / "permissions.json"

        default_permissions = {
            "read": {
                "description": "Read access to resources",
                "inherits": []
            },
            "write": {
                "description": "Write access to resources",
                "inherits": ["read"]
            },
            "execute": {
                "description": "Execute/run capabilities",
                "inherits": ["read"]
            },
            "delete": {
                "description": "Delete resources",
                "inherits": ["read", "write"]
            },
            "admin": {
                "description": "Administrative privileges",
                "inherits": ["read", "write", "execute", "delete"]
            },
            "modify_permissions": {
                "description": "Modify permissions and roles",
                "inherits": ["admin"]
            },
            "view_audit_logs": {
                "description": "Access to audit logs",
                "inherits": ["admin"]
            },
            "manage_users": {
                "description": "User management capabilities",
                "inherits": ["admin"]
            },
            "access_sensitive_data": {
                "description": "Access to sensitive information",
                "inherits": ["admin"]
            },
            "bypass_approval": {
                "description": "Bypass approval processes",
                "inherits": ["admin"]
            }
        }

        if permissions_file.exists():
            with open(permissions_file, 'r') as f:
                return json.load(f)
        else:
            # Create default permissions file
            with open(permissions_file, 'w') as f:
                json.dump(default_permissions, f, indent=2)
            return default_permissions

    def _load_role_assignments(self) -> Dict[str, List[str]]:
        """Load user-to-role assignments"""
        assignments_file = self.storage_path / "role_assignments.json"

        default_assignments = {
            "admin": ["admin"],
            "system": ["system"]
        }

        if assignments_file.exists():
            with open(assignments_file, 'r') as f:
                return json.load(f)
        else:
            # Create default assignments file
            with open(assignments_file, 'w') as f:
                json.dump(default_assignments, f, indent=2)
            return default_assignments

    def _load_resource_permissions(self) -> Dict[str, Dict[str, List[str]]]:
        """Load resource-specific permissions"""
        resource_perms_file = self.storage_path / "resource_permissions.json"

        default_resource_perms = {
            "Vault/Config/": {
                "admin": ["read", "write", "delete"],
                "auditor": ["read"]
            },
            "Vault/Logs/": {
                "admin": ["read", "write"],
                "auditor": ["read"]
            },
            "AI_Employee_Vault/Gold_Tier/": {
                "admin": ["read", "write", "execute"],
                "power_user": ["read", "write"],
                "user": ["read"]
            }
        }

        if resource_perms_file.exists():
            with open(resource_perms_file, 'r') as f:
                return json.load(f)
        else:
            # Create default resource permissions file
            with open(resource_perms_file, 'w') as f:
                json.dump(default_resource_perms, f, indent=2)
            return default_resource_perms

    def add_user(self, user_id: str, name: str, role: str = "user", active: bool = True) -> bool:
        """Add a new user to the system"""
        if user_id in self.users:
            self.logger.warning(f"User {user_id} already exists")
            return False

        # Verify role exists
        if role not in self.roles:
            self.logger.error(f"Invalid role: {role}")
            return False

        self.users[user_id] = {
            "name": name,
            "role": role,
            "permissions": self._get_permissions_for_role(role),
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "active": active
        }

        # Save to file
        self._save_users()
        self.logger.info(f"Added user {user_id} with role {role}")
        return True

    def assign_role(self, user_id: str, role: str) -> bool:
        """Assign a role to a user"""
        if user_id not in self.users:
            self.logger.error(f"User {user_id} does not exist")
            return False

        if role not in self.roles:
            self.logger.error(f"Invalid role: {role}")
            return False

        old_role = self.users[user_id]["role"]
        self.users[user_id]["role"] = role
        self.users[user_id]["permissions"] = self._get_permissions_for_role(role)

        # Save changes
        self._save_users()
        self.logger.info(f"Assigned role {role} to user {user_id} (was {old_role})")
        return True

    def grant_permission(self, user_id: str, permission: str) -> bool:
        """Grant a specific permission to a user"""
        if user_id not in self.users:
            self.logger.error(f"User {user_id} does not exist")
            return False

        if permission not in self.permissions:
            self.logger.error(f"Invalid permission: {permission}")
            return False

        if permission not in self.users[user_id]["permissions"]:
            self.users[user_id]["permissions"].append(permission)

            # Save changes
            self._save_users()
            self.logger.info(f"Granted permission {permission} to user {user_id}")

        return True

    def revoke_permission(self, user_id: str, permission: str) -> bool:
        """Revoke a specific permission from a user"""
        if user_id not in self.users:
            self.logger.error(f"User {user_id} does not exist")
            return False

        if permission in self.users[user_id]["permissions"]:
            self.users[user_id]["permissions"].remove(permission)

            # Save changes
            self._save_users()
            self.logger.info(f"Revoked permission {permission} from user {user_id}")

        return True

    def check_permission(self, user_id: str, permission: str, resource: str = None) -> bool:
        """Check if a user has a specific permission"""
        if user_id not in self.users:
            self.logger.warning(f"User {user_id} does not exist")
            return False

        if not self.users[user_id]["active"]:
            self.logger.warning(f"User {user_id} is inactive")
            return False

        # Check if user has the direct permission
        if permission in self.users[user_id]["permissions"]:
            # If resource-specific permissions exist, check those too
            if resource and not self._check_resource_permission(user_id, permission, resource):
                return False
            return True

        # Check inherited permissions
        return self._check_permission_inheritance(permission, self.users[user_id]["permissions"])

    def _check_resource_permission(self, user_id: str, permission: str, resource: str) -> bool:
        """Check if user has permission for a specific resource"""
        # Find the most specific resource match
        user_role = self.users[user_id]["role"]

        # Check exact resource match first
        if resource in self.resource_permissions:
            resource_perms = self.resource_permissions[resource]
            if user_role in resource_perms:
                return permission in resource_perms[user_role]

        # Check parent directory matches
        resource_path = Path(resource)
        while resource_path.parent != resource_path:
            resource_path = resource_path.parent
            parent_resource = str(resource_path) + "/"

            if parent_resource in self.resource_permissions:
                resource_perms = self.resource_permissions[parent_resource]
                if user_role in resource_perms:
                    return permission in resource_perms[user_role]

        # If no specific resource permissions, allow based on general permissions
        return True

    def _check_permission_inheritance(self, permission: str, user_permissions: List[str]) -> bool:
        """Check if a permission is inherited through other permissions"""
        # Get inheritance chain for the requested permission
        inherited_perms = self._get_inherited_permissions(permission)

        # Check if user has any of the required permissions
        for perm in user_permissions:
            if perm in inherited_perms or perm == permission:
                return True

        return False

    def _get_inherited_permissions(self, permission: str) -> Set[str]:
        """Get all permissions that inherit from the given permission"""
        inherited = {permission}

        # Find all permissions that inherit from this one
        for perm_name, perm_data in self.permissions.items():
            if permission in perm_data.get("inherits", []):
                inherited.update(self._get_inherited_permissions(perm_name))

        return inherited

    def _get_permissions_for_role(self, role: str) -> List[str]:
        """Get all permissions for a role, including inherited ones"""
        if role not in self.roles:
            return []

        role_permissions = set(self.roles[role]["permissions"])

        # Add inherited permissions
        for perm in list(role_permissions):
            inherited = self._get_inherited_permissions(perm)
            role_permissions.update(inherited)

        return list(role_permissions)

    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user"""
        if user_id not in self.users:
            return []

        return self.users[user_id]["permissions"]

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles for a user"""
        if user_id not in self.users:
            return []

        return [self.users[user_id]["role"]]

    def create_resource_permission(self, resource: str, role: str, permissions: List[str]) -> bool:
        """Create or update resource-specific permissions"""
        if role not in self.roles:
            self.logger.error(f"Invalid role: {role}")
            return False

        for perm in permissions:
            if perm not in self.permissions:
                self.logger.error(f"Invalid permission: {perm}")
                return False

        if resource not in self.resource_permissions:
            self.resource_permissions[resource] = {}

        self.resource_permissions[resource][role] = permissions

        # Save to file
        self._save_resource_permissions()
        self.logger.info(f"Set resource permissions for {resource} and role {role}")
        return True

    def remove_resource_permission(self, resource: str, role: str = None) -> bool:
        """Remove resource-specific permissions"""
        if resource not in self.resource_permissions:
            self.logger.warning(f"No permissions found for resource: {resource}")
            return False

        if role:
            if role in self.resource_permissions[resource]:
                del self.resource_permissions[resource][role]
                if not self.resource_permissions[resource]:  # Remove resource if no roles left
                    del self.resource_permissions[resource]
        else:
            del self.resource_permissions[resource]

        # Save to file
        self._save_resource_permissions()
        self.logger.info(f"Removed resource permissions for {resource}")
        return True

    def _save_users(self):
        """Save users to file"""
        users_file = self.storage_path / "users.json"
        with open(users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def _save_resource_permissions(self):
        """Save resource permissions to file"""
        resource_perms_file = self.storage_path / "resource_permissions.json"
        with open(resource_perms_file, 'w') as f:
            json.dump(self.resource_permissions, f, indent=2)

    def get_access_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """Get access matrix showing permissions by user and resource"""
        access_matrix = {}

        for user_id, user_data in self.users.items():
            if user_data["active"]:
                user_perms = user_data["permissions"]

                # For each resource with specific permissions
                for resource, role_perms in self.resource_permissions.items():
                    if user_data["role"] in role_perms:
                        if user_id not in access_matrix:
                            access_matrix[user_id] = {}

                        allowed_perms = []
                        for perm in role_perms[user_data["role"]]:
                            if perm in user_perms:
                                allowed_perms.append(perm)

                        if allowed_perms:
                            access_matrix[user_id][resource] = allowed_perms

        return access_matrix

    def validate_user_session(self, user_id: str, session_token: str = None) -> bool:
        """Validate user session and permissions"""
        if user_id not in self.users:
            self.logger.warning(f"Invalid user session for {user_id}")
            return False

        if not self.users[user_id]["active"]:
            self.logger.warning(f"Session for inactive user {user_id}")
            return False

        # In a real implementation, you'd validate the session token
        # For now, just return True if user is valid and active
        return True

    def enforce_temporal_restrictions(self, user_id: str, action_time: datetime = None) -> bool:
        """Enforce time-based access restrictions"""
        if action_time is None:
            action_time = datetime.now()

        # Example: Check if user has weekend access
        if action_time.weekday() >= 5:  # Saturday or Sunday
            user_role = self.users[user_id]["role"]
            if user_role in ["guest", "user"]:
                # Basic users may not have weekend access
                return False

        # Example: Check business hours
        if 9 <= action_time.hour <= 17:  # Business hours
            return True
        else:
            # Outside business hours - check if user has extended access
            user_role = self.users[user_id]["role"]
            return user_role in ["admin", "power_user", "system"]

    def generate_permission_report(self) -> Dict[str, Any]:
        """Generate a comprehensive permission report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_users": len(self.users),
            "active_users": len([u for u in self.users.values() if u["active"]]),
            "inactive_users": len([u for u in self.users.values() if not u["active"]]),
            "users_by_role": {},
            "resource_restrictions": len(self.resource_permissions),
            "permissions_summary": {perm: 0 for perm in self.permissions.keys()},
            "access_matrix_preview": self.get_access_matrix()
        }

        # Count users by role
        for user_data in self.users.values():
            role = user_data["role"]
            report["users_by_role"][role] = report["users_by_role"].get(role, 0) + 1

        # Count permission usage
        for user_data in self.users.values():
            for perm in user_data["permissions"]:
                if perm in report["permissions_summary"]:
                    report["permissions_summary"][perm] += 1

        # Save report
        report_file = self.storage_path / f"permission_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Generated permission report: {report_file}")
        return report

    def cleanup_inactive_users(self, days_inactive: int = 90) -> int:
        """Clean up users who haven't logged in for specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        cleaned_count = 0

        for user_id, user_data in list(self.users.items()):
            last_login = user_data["last_login"]
            if last_login:
                login_date = datetime.fromisoformat(last_login)
                if login_date < cutoff_date:
                    # Mark as inactive instead of deleting
                    user_data["active"] = False
                    cleaned_count += 1
                    self.logger.info(f"Marked user {user_id} as inactive due to inactivity")

        # Save changes
        self._save_users()
        return cleaned_count


async def test_permission_manager():
    """Test the permission manager"""
    print("Testing Permission Manager...")

    pm = PermissionManager()

    # Add a test user
    print("\n1. Adding test users...")
    pm.add_user("alice", "Alice Johnson", "user")
    pm.add_user("bob", "Bob Smith", "power_user")
    pm.add_user("charlie", "Charlie Brown", "admin")
    print("Test users added")

    # Check user permissions
    print("\n2. Checking user permissions...")
    alice_perms = pm.get_user_permissions("alice")
    bob_perms = pm.get_user_permissions("bob")
    charlie_perms = pm.get_user_permissions("charlie")

    print(f"Alice's permissions: {alice_perms}")
    print(f"Bob's permissions: {bob_perms}")
    print(f"Charlie's permissions: {charlie_perms}")

    # Test permission checks
    print("\n3. Testing permission checks...")
    print(f"Alice can read: {pm.check_permission('alice', 'read')}")
    print(f"Alice can write: {pm.check_permission('alice', 'write')}")
    print(f"Alice can admin: {pm.check_permission('alice', 'admin')}")
    print(f"Bob can execute: {pm.check_permission('bob', 'execute')}")
    print(f"Charlie can admin: {pm.check_permission('charlie', 'admin')}")

    # Grant and revoke permissions
    print("\n4. Granting and revoking permissions...")
    pm.grant_permission("alice", "execute")
    print(f"Alice can now execute: {pm.check_permission('alice', 'execute')}")

    pm.revoke_permission("alice", "execute")
    print(f"Alice can execute after revocation: {pm.check_permission('alice', 'execute')}")

    # Test role assignment
    print("\n5. Testing role assignment...")
    pm.assign_role("alice", "power_user")
    alice_new_perms = pm.get_user_permissions("alice")
    print(f"Alice's new permissions after role change: {alice_new_perms}")

    # Test resource-specific permissions
    print("\n6. Testing resource-specific permissions...")
    pm.create_resource_permission("Vault/Secret/", "user", ["read"])
    pm.create_resource_permission("Vault/Secret/", "admin", ["read", "write", "delete"])

    print(f"Alice can read secret: {pm.check_permission('alice', 'read', 'Vault/Secret/')}")
    print(f"Charlie can delete secret: {pm.check_permission('charlie', 'delete', 'Vault/Secret/')}")

    # Test temporal restrictions
    print("\n7. Testing temporal restrictions...")
    test_time = datetime(2026, 1, 1, 8, 0)  # Early morning
    print(f"Alice allowed at 8 AM: {pm.enforce_temporal_restrictions('alice', test_time)}")

    test_time = datetime(2026, 1, 1, 12, 0)  # Midday
    print(f"Alice allowed at 12 PM: {pm.enforce_temporal_restrictions('alice', test_time)}")

    # Generate permission report
    print("\n8. Generating permission report...")
    report = pm.generate_permission_report()
    print(f"Report generated with {report['total_users']} total users")
    print(f"Active users: {report['active_users']}")
    print(f"Users by role: {report['users_by_role']}")

    # Show access matrix
    print("\n9. Access matrix preview:")
    matrix = pm.get_access_matrix()
    for user, resources in list(matrix.items())[:3]:  # Show first 3 users
        print(f"  {user}: {resources}")

    return True


if __name__ == "__main__":
    asyncio.run(test_permission_manager())