"""
Immutable audit logging for compliance.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class AuditEntry:
    """Single audit log entry."""

    timestamp: str  # ISO format
    agent: str
    action: str  # "suggest", "validate", "refuse", "log"
    target: str  # File or resource
    status: str  # "approved", "denied", "pending", "executed"
    reason: Optional[str] = None
    metadata: Dict[str, Any] = None
    hash_prev: str = ""  # Hash of previous entry (chain)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def compute_hash(self) -> str:
        """Compute SHA256 hash of this entry (excluding its own hash)."""
        entry_dict = asdict(self)
        entry_dict["hash_prev"] = self.hash_prev
        entry_dict["hash"] = ""  # Exclude hash field itself

        json_str = json.dumps(entry_dict, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]


class AuditLog:
    """
    Immutable, append-only audit log.

    Maintains chain of hashes to detect tampering.
    """

    def __init__(self, log_dir: str = ".pmind/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.jsonl"
        self.entries: List[AuditEntry] = []
        self._load_existing()

    def _load_existing(self):
        """Load existing entries from disk."""
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = AuditEntry(**data)
                        self.entries.append(entry)

    def log_action(
        self,
        agent: str,
        action: str,
        target: str,
        status: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        Log an action (append-only).

        Returns the created AuditEntry.
        """
        # Compute hash chain
        hash_prev = ""
        if self.entries:
            hash_prev = self.entries[-1].compute_hash()

        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            agent=agent,
            action=action,
            target=target,
            status=status,
            reason=reason,
            metadata=metadata or {},
            hash_prev=hash_prev,
        )

        # Append to file (immutable)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

        self.entries.append(entry)
        return entry

    def get_entries(
        self, agent: Optional[str] = None, status: Optional[str] = None
    ) -> List[AuditEntry]:
        """Get filtered entries."""
        result = self.entries

        if agent:
            result = [e for e in result if e.agent == agent]

        if status:
            result = [e for e in result if e.status == status]

        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get audit summary."""
        actions_by_agent = {}
        actions_by_status = {}

        for entry in self.entries:
            actions_by_agent[entry.agent] = actions_by_agent.get(entry.agent, 0) + 1
            actions_by_status[entry.status] = actions_by_status.get(entry.status, 0) + 1

        return {
            "total_entries": len(self.entries),
            "by_agent": actions_by_agent,
            "by_status": actions_by_status,
            "first_entry": self.entries[0].timestamp if self.entries else None,
            "last_entry": self.entries[-1].timestamp if self.entries else None,
        }

    def export_report(self, output_file: str, format: str = "json") -> str:
        """Export audit trail as report."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(path, "w") as f:
                json.dump(
                    {
                        "summary": self.get_summary(),
                        "entries": [asdict(e) for e in self.entries],
                    },
                    f,
                    indent=2,
                    default=str,
                )

        elif format == "markdown":
            with open(path, "w") as f:
                f.write("# ProjectMind Audit Report\n\n")
                f.write(f"Generated: {datetime.utcnow().isoformat()}Z\n\n")

                summary = self.get_summary()
                f.write("## Summary\n\n")
                f.write(f"- Total Actions: {summary['total_entries']}\n")
                f.write(f"- By Agent:\n")
                for agent, count in summary["by_agent"].items():
                    f.write(f"  - {agent}: {count}\n")
                f.write(f"- By Status:\n")
                for status, count in summary["by_status"].items():
                    f.write(f"  - {status}: {count}\n")

                f.write("\n## Actions\n\n")
                for entry in self.entries:
                    f.write(f"### {entry.timestamp}\n")
                    f.write(f"- **Agent**: {entry.agent}\n")
                    f.write(f"- **Action**: {entry.action}\n")
                    f.write(f"- **Target**: {entry.target}\n")
                    f.write(f"- **Status**: {entry.status}\n")
                    if entry.reason:
                        f.write(f"- **Reason**: {entry.reason}\n")
                    f.write("\n")

        return str(path)

    def verify_chain_integrity(self) -> bool:
        """Verify hash chain hasn't been tampered with."""
        if not self.entries:
            return True

        for i, entry in enumerate(self.entries):
            computed_hash = entry.compute_hash()
            if i > 0 and entry.hash_prev != self.entries[i - 1].compute_hash():
                return False

        return True
