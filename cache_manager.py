import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Any, Dict
import httpx

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, cache_dir: str = "resources"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, sub_dir: str, filename: str) -> Path:
        cache_path = self.cache_dir / sub_dir
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path / filename
    
    def _get_meta_path(self, sub_dir: str, filename: str) -> Path:
        meta_filename = f"{filename}.meta"
        return self._get_cache_path(sub_dir, meta_filename)
    
    def _load_meta(self, sub_dir: str, filename: str) -> Dict:
        meta_path = self._get_meta_path(sub_dir, filename)
        if meta_path.exists():
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_meta(self, sub_dir: str, filename: str, meta: Dict):
        meta_path = self._get_meta_path(sub_dir, filename)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    
    def _get_cached_date(self, sub_dir: str, filename: str) -> Optional[date]:
        meta = self._load_meta(sub_dir, filename)
        cached_date_str = meta.get("cached_date")
        if cached_date_str:
            try:
                return datetime.strptime(cached_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        return None
    
    def _is_cache_valid(self, sub_dir: str, filename: str) -> bool:
        cached_date = self._get_cached_date(sub_dir, filename)
        if cached_date is None:
            return False
        today = date.today()
        return cached_date >= today
    
    def _cleanup_old_files(self, sub_dir: str, keep_filename: str):
        cache_path = self.cache_dir / sub_dir
        if not cache_path.exists():
            return
        
        keep_file = cache_path / keep_filename
        keep_meta = cache_path / f"{keep_filename}.meta"
        
        for file in cache_path.iterdir():
            if file.is_file() and file != keep_file and file != keep_meta:
                try:
                    file.unlink()
                    logger.info(f"Cleaned up old cache file: {file}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup file {file}: {e}")
    
    def load_cache(self, sub_dir: str, filename: str) -> Optional[Any]:
        if not self._is_cache_valid(sub_dir, filename):
            return None
        
        cache_path = self._get_cache_path(sub_dir, filename)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load cache {cache_path}: {e}")
        return None
    
    def save_cache(self, sub_dir: str, filename: str, data: Any):
        cache_path = self._get_cache_path(sub_dir, filename)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        meta = {
            "cached_date": date.today().isoformat(),
            "cached_at": datetime.now().isoformat()
        }
        self._save_meta(sub_dir, filename, meta)
        
        self._cleanup_old_files(sub_dir, filename)
        logger.info(f"Cache saved to {cache_path}")
    
    async def fetch_and_cache(
        self, 
        url: str, 
        sub_dir: str, 
        filename: str
    ) -> Optional[Any]:
        cached_data = self.load_cache(sub_dir, filename)
        if cached_data is not None:
            logger.info(f"Using cached data for {sub_dir}/{filename}")
            return cached_data
        
        logger.info(f"Fetching data from {url}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if isinstance(data, str):
                logger.warning(f"API returned string instead of JSON, attempting to parse")
                try:
                    import json
                    data = json.loads(data)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse string as JSON")
                    return None
            
            self.save_cache(sub_dir, filename, data)
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
        
        return None


cache_manager = CacheManager()
