"""
Audit Logging: Immutable, append-only action trail.

All system actions are logged for compliance audits.
"""

from .audit_log import AuditLog, AuditEntry

__all__ = ["AuditLog", "AuditEntry"]
