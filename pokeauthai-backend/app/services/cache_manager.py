import json
import os
import time
from pathlib import Path
from typing import Any

from app.config import get_settings


class CacheManager:
    def __init__(self, cache_dir: Path | None = None):
        if cache_dir is None:
            settings = get_settings()
            # Default to pokeauthai-backend/cache
            self.cache_dir = Path(__file__).resolve().parents[2] / "cache"
        else:
            self.cache_dir = cache_dir

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, cache_name: str) -> Path:
        if not cache_name.endswith(".json"):
            cache_name += ".json"
        return self.cache_dir / cache_name

    def get(self, cache_name: str, key: str, ttl_seconds: int = 86400) -> Any | None:
        """Get an item from the cache if it exists and is not expired."""
        path = self._get_cache_path(cache_name)
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            if key not in cache_data:
                return None

            entry = cache_data[key]
            timestamp = entry.get("_timestamp", 0)

            # Check TTL
            if time.time() - timestamp > ttl_seconds:
                return None

            return entry.get("data")
        except (json.JSONDecodeError, IOError):
            return None

    def set(self, cache_name: str, key: str, data: Any) -> None:
        """Set an item in the cache."""
        path = self._get_cache_path(cache_name)
        
        # Load existing
        cache_data = {}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                cache_data = {}

        # Update
        cache_data[key] = {
            "_timestamp": time.time(),
            "data": data
        }

        # Save
        try:
            # Write to temp file then rename for atomic update
            temp_path = path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path)
        except IOError:
            pass

cache_manager = CacheManager()
