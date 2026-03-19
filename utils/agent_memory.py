"""
Agent Memory — Lightweight JSON-file-based memory system for cross-cycle learning.

Each agent can have its own namespace. Memory persists between trading cycles
so agents can recall past decisions, debate outcomes, and trade results.
"""

import json
import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    Simple persistent memory for a single agent.

    Stores entries as a JSON array on disk, keyed by namespace.
    Each entry has a timestamp, a user-defined key, and arbitrary data.
    """

    def __init__(self, namespace: str, memory_dir: str = "data/agent_memory",
                 max_entries: int = 50):
        self.namespace = namespace
        self.memory_dir = memory_dir
        self.max_entries = max_entries
        self._filepath = os.path.join(memory_dir, f"{namespace}.json")
        self._cache: List[Dict[str, Any]] = []
        self._load()

    # ── Public API ──────────────────────────────────────────────────

    def store(self, key: str, data: Any) -> None:
        """Store a memory entry under the given key."""
        entry = {
            "key": key,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self._cache.append(entry)

        # Trim to max entries (keep most recent)
        if len(self._cache) > self.max_entries:
            self._cache = self._cache[-self.max_entries:]

        self._save()
        logger.debug(f"[{self.namespace}] Stored memory: {key}")

    def recall(self, key: str) -> Optional[Any]:
        """Recall the most recent entry for the given key, or None."""
        for entry in reversed(self._cache):
            if entry["key"] == key:
                return entry["data"]
        return None

    def recall_all(self, key: str) -> List[Any]:
        """Recall all entries for the given key, oldest first."""
        return [e["data"] for e in self._cache if e["key"] == key]

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the N most recent entries regardless of key."""
        return self._cache[-n:]

    def get_context_summary(self, n: int = 3) -> str:
        """
        Build a short text summary of recent memories for LLM prompt injection.
        Returns an empty string if no memories exist.
        """
        recent = self.get_recent(n)
        if not recent:
            return ""

        lines = [f"=== Recent Memory ({self.namespace}) ==="]
        for entry in recent:
            ts = entry.get("timestamp", "?")[:19]
            key = entry.get("key", "?")
            data = entry.get("data", {})
            # Truncate data repr to avoid prompt bloat
            data_str = str(data)[:200]
            lines.append(f"[{ts}] {key}: {data_str}")
        lines.append("=== End Memory ===")
        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all memories for this namespace."""
        self._cache = []
        self._save()

    # ── Internal ────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load memories from disk."""
        try:
            if os.path.exists(self._filepath):
                with open(self._filepath, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
                logger.debug(f"[{self.namespace}] Loaded {len(self._cache)} memories")
        except Exception as e:
            logger.warning(f"[{self.namespace}] Failed to load memory: {e}")
            self._cache = []

    def _save(self) -> None:
        """Persist memories to disk."""
        try:
            os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"[{self.namespace}] Failed to save memory: {e}")
