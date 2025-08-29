import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

class AuthenticationSystem:
    def __init__(self, config_path: str = "auth_config.json"):
        self.config_path = config_path
        self.failed_attempts = {}
        self.active_sessions = {}
        self.audit_log = []
        self.load_config()
    
    def load_config(self):
        """Load authentication configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            print("🔐 Authentication system loaded successfully")
        except FileNotFoundError:
            print("❌ Auth config file not found, using default settings")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default authentication configuration"""
        return {
            "access_keys": {
                "master_key": "DEFAULT_MASTER_KEY",
                "admin_key": "DEFAULT_ADMIN_KEY"
            },
            "permissions": {
                "DEFAULT_MASTER_KEY": ["create_blog", "update_blog", "delete_blog", "search_blogs", "admin_access"],
                "DEFAULT_ADMIN_KEY": ["create_blog", "update_blog", "search_blogs"]
            },
            "security_settings": {
                "require_auth_for_operations": ["create", "update", "delete"],
                "max_attempts": 3,
                "lockout_duration_minutes": 15,
                "session_timeout_minutes": 60
            }
        }
    
    def validate_access_key(self, access_key: str, operation: str) -> Dict[str, Any]:
        """Validate access key and check permissions"""
        try:
            # Check if key is locked out
            if self._is_locked_out(access_key):
                return {
                    "valid": False,
                    "reason": "account_locked",
                    "message": "🔒 Access key is temporarily locked due to too many failed attempts",
                    "lockout_remaining": self._get_lockout_remaining(access_key)
                }
            
            # Check if key exists and has permission
            permissions = self.config.get("permissions", {})
            if access_key not in permissions:
                self._record_failed_attempt(access_key)
                return {
                    "valid": False,
                    "reason": "invalid_key",
                    "message": "❌ Invalid access key provided"
                }
            
            # Check operation permission
            allowed_operations = permissions[access_key]
            if operation not in allowed_operations:
                self._record_failed_attempt(access_key)
                return {
                    "valid": False,
                    "reason": "insufficient_permission",
                    "message": f"🚫 Access key does not have permission for '{operation}' operation",
                    "allowed_operations": allowed_operations
                }
            
            # Validation successful
            self._clear_failed_attempts(access_key)
            self._create_session(access_key)
            self._log_access(access_key, operation, "success")
            
            return {
                "valid": True,
                "message": "✅ Access granted",
                "permissions": allowed_operations,
                "session_id": self._get_session_id(access_key)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": "system_error",
                "message": f"❌ Authentication system error: {str(e)}"
            }
    
    def _is_locked_out(self, access_key: str) -> bool:
        """Check if access key is locked out"""
        if access_key not in self.failed_attempts:
            return False
        
        attempts_data = self.failed_attempts[access_key]
        max_attempts = self.config["security_settings"]["max_attempts"]
        lockout_duration = self.config["security_settings"]["lockout_duration_minutes"]
        
        if attempts_data["count"] >= max_attempts:
            # Check if lockout period has expired
            lockout_time = attempts_data["last_attempt"] + timedelta(minutes=lockout_duration)
            if datetime.now() < lockout_time:
                return True
            else:
                # Lockout expired, reset attempts
                del self.failed_attempts[access_key]
                return False
        
        return False
    
    def _get_lockout_remaining(self, access_key: str) -> str:
        """Get remaining lockout time"""
        if access_key not in self.failed_attempts:
            return "0 minutes"
        
        attempts_data = self.failed_attempts[access_key]
        lockout_duration = self.config["security_settings"]["lockout_duration_minutes"]
        lockout_end = attempts_data["last_attempt"] + timedelta(minutes=lockout_duration)
        remaining = lockout_end - datetime.now()
        
        if remaining.total_seconds() > 0:
            minutes = int(remaining.total_seconds() / 60)
            return f"{minutes} minutes"
        return "0 minutes"
    
    def _record_failed_attempt(self, access_key: str):
        """Record failed authentication attempt"""
        now = datetime.now()
        
        if access_key in self.failed_attempts:
            self.failed_attempts[access_key]["count"] += 1
            self.failed_attempts[access_key]["last_attempt"] = now
        else:
            self.failed_attempts[access_key] = {
                "count": 1,
                "first_attempt": now,
                "last_attempt": now
            }
        
        self._log_access(access_key, "authentication", "failed")
    
    def _clear_failed_attempts(self, access_key: str):
        """Clear failed attempts for successful authentication"""
        if access_key in self.failed_attempts:
            del self.failed_attempts[access_key]
    
    def _create_session(self, access_key: str):
        """Create active session"""
        session_id = self._generate_session_id(access_key)
        timeout_minutes = self.config["security_settings"]["session_timeout_minutes"]
        
        self.active_sessions[session_id] = {
            "access_key": access_key,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=timeout_minutes),
            "last_activity": datetime.now()
        }
        
        return session_id
    
    def _generate_session_id(self, access_key: str) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time() * 1000))
        combined = f"{access_key}_{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _get_session_id(self, access_key: str) -> str:
        """Get current session ID for access key"""
        for session_id, session_data in self.active_sessions.items():
            if session_data["access_key"] == access_key:
                return session_id
        return ""
    
    def _log_access(self, access_key: str, operation: str, status: str):
        """Log access attempts"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "access_key_hash": hashlib.sha256(access_key.encode()).hexdigest()[:8],  # Partial hash for privacy
            "operation": operation,
            "status": status,
            "ip_address": "localhost"  # Would be actual IP in production
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_access_key_info(self, access_key: str) -> Dict[str, Any]:
        """Get information about access key permissions"""
        permissions = self.config.get("permissions", {})
        
        if access_key not in permissions:
            return {
                "valid": False,
                "message": "❌ Invalid access key"
            }
        
        return {
            "valid": True,
            "permissions": permissions[access_key],
            "key_type": self._get_key_type(access_key),
            "last_used": self._get_last_used(access_key)
        }
    
    def _get_key_type(self, access_key: str) -> str:
        """Determine key type based on permissions"""
        permissions = self.config.get("permissions", {}).get(access_key, [])
        
        if "admin_access" in permissions:
            return "Master Key"
        elif "delete_blog" in permissions:
            return "Admin Key"
        elif "update_blog" in permissions:
            return "Update Key"
        else:
            return "Read-Only Key"
    
    def _get_last_used(self, access_key: str) -> Optional[str]:
        """Get last usage time for access key"""
        for log_entry in reversed(self.audit_log):
            if log_entry["status"] == "success":
                access_key_hash = hashlib.sha256(access_key.encode()).hexdigest()[:8]
                if log_entry["access_key_hash"] == access_key_hash:
                    return log_entry["timestamp"]
        return None
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if now > session_data["expires_at"]:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        return {
            "active_sessions": len(self.active_sessions),
            "failed_attempts": len(self.failed_attempts),
            "locked_accounts": sum(1 for k in self.failed_attempts.keys() if self._is_locked_out(k)),
            "total_access_logs": len(self.audit_log),
            "successful_auths_today": self._count_successful_auths_today(),
            "failed_auths_today": self._count_failed_auths_today()
        }
    
    def _count_successful_auths_today(self) -> int:
        """Count successful authentications today"""
        today = datetime.now().date()
        count = 0
        
        for log_entry in self.audit_log:
            log_date = datetime.fromisoformat(log_entry["timestamp"]).date()
            if log_date == today and log_entry["status"] == "success":
                count += 1
        
        return count
    
    def _count_failed_auths_today(self) -> int:
        """Count failed authentications today"""
        today = datetime.now().date()
        count = 0
        
        for log_entry in self.audit_log:
            log_date = datetime.fromisoformat(log_entry["timestamp"]).date()
            if log_date == today and log_entry["status"] == "failed":
                count += 1
        
        return count

# Global authentication instance
auth_system = AuthenticationSystem()