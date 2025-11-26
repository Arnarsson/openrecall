"""
Universal Memory integration for OpenRecall.

This module syncs OpenRecall's captured screen data with Universal Memory MCP,
enabling AI agents to query your digital history through natural conversation.

Usage:
    # Export all memories to Universal Memory
    openrecall --export-memories

    # Enable real-time sync (sends new captures to Universal Memory)
    openrecall --sync-memories

    # Programmatic usage
    from openrecall.universal_memory import MemorySync
    sync = MemorySync(mcp_url="http://localhost:3000")
    sync.export_all()
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from openrecall.database import get_all_entries, Entry
from openrecall.config import appdata_folder

logger = logging.getLogger(__name__)


@dataclass
class MemoryObservation:
    """Represents an observation to be sent to Universal Memory."""
    entity_name: str
    content: str
    source: str = "openrecall"
    timestamp: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class UniversalMemoryClient:
    """
    Client for interacting with Universal Memory MCP.

    The MCP exposes HTTP endpoints for memory operations:
    - POST /memory/observation - Add a new observation
    - POST /memory/entity - Create a new entity
    - GET /memory/search - Search memories
    - GET /memory/graph - Get entity context graph
    - GET /memory/stats - Get memory statistics
    """

    def __init__(self, base_url: str = "http://localhost:3000"):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required. Install with: pip install requests")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "OpenRecall/1.0",
        })

    def add_observation(
        self,
        entity_name: str,
        content: str,
        source: str = "openrecall",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a new observation to Universal Memory.

        Args:
            entity_name: The entity this observation is about (e.g., "user", "project-x")
            content: The observation content
            source: Source identifier (default: "openrecall")
            metadata: Optional additional metadata

        Returns:
            Response from the memory service
        """
        payload = {
            "entity_name": entity_name,
            "content": content,
            "source": source,
        }
        if metadata:
            payload["metadata"] = metadata

        response = self.session.post(
            f"{self.base_url}/memory/observation",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def create_entity(
        self,
        name: str,
        entity_type: str = "context",
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new entity in Universal Memory.

        Args:
            name: Entity name/identifier
            entity_type: Type of entity (person, project, context, etc.)
            description: Optional description

        Returns:
            Response from the memory service
        """
        payload = {
            "name": name,
            "type": entity_type,
        }
        if description:
            payload["description"] = description

        response = self.session.post(
            f"{self.base_url}/memory/entity",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search memories by keyword.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            Search results from the memory service
        """
        response = self.session.get(
            f"{self.base_url}/memory/search",
            params={"q": query, "limit": limit},
        )
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        response = self.session.get(f"{self.base_url}/memory/stats")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check if the Universal Memory MCP is reachable."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class MemorySync:
    """
    Syncs OpenRecall captures to Universal Memory.

    Converts screen captures into meaningful observations:
    - Groups by application (creates entities for each app)
    - Extracts key content from OCR text
    - Adds temporal context (time of day, duration)
    """

    def __init__(
        self,
        mcp_url: str = "http://localhost:3000",
        entity_prefix: str = "openrecall",
    ):
        self.client = UniversalMemoryClient(mcp_url)
        self.entity_prefix = entity_prefix
        self._synced_timestamps_file = os.path.join(appdata_folder, "synced_memories.json")
        self._synced_timestamps = self._load_synced_timestamps()

    def _load_synced_timestamps(self) -> set:
        """Load set of already-synced timestamps to avoid duplicates."""
        if os.path.exists(self._synced_timestamps_file):
            try:
                with open(self._synced_timestamps_file, "r") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _save_synced_timestamps(self):
        """Persist synced timestamps to disk."""
        try:
            with open(self._synced_timestamps_file, "w") as f:
                json.dump(list(self._synced_timestamps), f)
        except Exception as e:
            logger.warning(f"Failed to save synced timestamps: {e}")

    def _entry_to_observation(self, entry: Entry) -> MemoryObservation:
        """
        Convert an OpenRecall database entry to a Universal Memory observation.

        Structures the observation to be useful for AI agent queries like:
        - "What was I working on in VS Code?"
        - "What did I read today?"
        - "Show me my browser activity"
        """
        # Create human-readable timestamp
        dt = datetime.fromtimestamp(entry.timestamp)
        time_str = dt.strftime("%Y-%m-%d %H:%M")
        time_of_day = self._get_time_of_day(dt.hour)

        # Truncate text if too long (Universal Memory may have limits)
        text = entry.text[:2000] if entry.text else ""

        # Structure the content for good AI querying
        content = f"""[{time_str}] {time_of_day} activity in {entry.app}
Window: {entry.title}
Content: {text}"""

        # Use app name as entity for grouping
        entity_name = f"{self.entity_prefix}:{entry.app.lower().replace(' ', '-')}"

        return MemoryObservation(
            entity_name=entity_name,
            content=content,
            source="openrecall",
            timestamp=entry.timestamp,
            metadata={
                "app": entry.app,
                "window_title": entry.title,
                "timestamp": entry.timestamp,
                "time_of_day": time_of_day,
            },
        )

    def _get_time_of_day(self, hour: int) -> str:
        """Convert hour to human-readable time of day."""
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"

    def export_entry(self, entry: Entry) -> bool:
        """
        Export a single entry to Universal Memory.

        Returns:
            True if exported successfully, False otherwise
        """
        if entry.timestamp in self._synced_timestamps:
            logger.debug(f"Skipping already synced entry: {entry.timestamp}")
            return True

        try:
            observation = self._entry_to_observation(entry)
            self.client.add_observation(
                entity_name=observation.entity_name,
                content=observation.content,
                source=observation.source,
                metadata=observation.metadata,
            )
            self._synced_timestamps.add(entry.timestamp)
            return True
        except Exception as e:
            logger.error(f"Failed to export entry {entry.timestamp}: {e}")
            return False

    def export_all(self, force: bool = False) -> Dict[str, int]:
        """
        Export all OpenRecall entries to Universal Memory.

        Args:
            force: If True, re-export already synced entries

        Returns:
            Dict with counts: {"exported": N, "skipped": N, "failed": N}
        """
        if force:
            self._synced_timestamps.clear()

        entries = get_all_entries()
        results = {"exported": 0, "skipped": 0, "failed": 0}

        print(f"Exporting {len(entries)} entries to Universal Memory...")

        for i, entry in enumerate(entries):
            if entry.timestamp in self._synced_timestamps and not force:
                results["skipped"] += 1
                continue

            if self.export_entry(entry):
                results["exported"] += 1
            else:
                results["failed"] += 1

            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(entries)}...")

        self._save_synced_timestamps()

        print(f"Export complete: {results['exported']} exported, "
              f"{results['skipped']} skipped, {results['failed']} failed")

        return results

    def export_recent(self, hours: int = 24) -> Dict[str, int]:
        """
        Export only recent entries (last N hours).

        Args:
            hours: How many hours back to export

        Returns:
            Dict with counts
        """
        import time
        cutoff = int(time.time()) - (hours * 3600)

        entries = get_all_entries()
        recent = [e for e in entries if e.timestamp >= cutoff]

        results = {"exported": 0, "skipped": 0, "failed": 0}

        print(f"Exporting {len(recent)} entries from last {hours} hours...")

        for entry in recent:
            if entry.timestamp in self._synced_timestamps:
                results["skipped"] += 1
                continue

            if self.export_entry(entry):
                results["exported"] += 1
            else:
                results["failed"] += 1

        self._save_synced_timestamps()
        return results

    def create_app_entities(self) -> List[str]:
        """
        Create entities for each unique app in OpenRecall data.

        This helps Universal Memory organize observations by application.
        """
        entries = get_all_entries()
        apps = set(e.app for e in entries if e.app)

        created = []
        for app in apps:
            entity_name = f"{self.entity_prefix}:{app.lower().replace(' ', '-')}"
            try:
                self.client.create_entity(
                    name=entity_name,
                    entity_type="application",
                    description=f"Screen activity from {app}",
                )
                created.append(entity_name)
                print(f"Created entity: {entity_name}")
            except Exception as e:
                logger.warning(f"Could not create entity {entity_name}: {e}")

        return created


def export_to_universal_memory(
    mcp_url: str = "http://localhost:3000",
    force: bool = False,
) -> Dict[str, int]:
    """
    Convenience function to export all OpenRecall data to Universal Memory.

    Args:
        mcp_url: URL of the Universal Memory MCP server
        force: Re-export already synced entries

    Returns:
        Export statistics
    """
    sync = MemorySync(mcp_url=mcp_url)

    # First, check if MCP is reachable
    if not sync.client.health_check():
        print(f"Warning: Universal Memory MCP not reachable at {mcp_url}")
        print("Make sure the MCP server is running.")
        return {"exported": 0, "skipped": 0, "failed": 0, "error": "MCP not reachable"}

    # Create app entities first
    sync.create_app_entities()

    # Export all observations
    return sync.export_all(force=force)
