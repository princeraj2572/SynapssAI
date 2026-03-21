"""
Caching layer for analytics and frequently accessed data.
Provides in-memory cache with TTL and optional Redis support.

Usage:
    cache = Cache()
    
    # Get with automatic caching
    result = cache.get_or_compute("daily_summary_2024-01-15", 
                                   compute_fn=lambda: expensive_query(...),
                                   ttl=3600)
    
    # Manual cache
    cache.set("key", value, ttl=1800)
    value = cache.get("key")
    
    # Invalidate
    cache.delete("key")
    cache.invalidate_pattern("daily_summary*")
"""
import time
import json
import hashlib
from typing import Any, Callable, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheEntry:
    """Single cache entry with TTL support."""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # None = no expiration
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        elapsed = time.time() - self.created_at
        return elapsed > self.ttl
    
    def __repr__(self):
        age = time.time() - self.created_at
        return f"CacheEntry(age={age:.1f}s, ttl={self.ttl}s)"


class InMemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 10000):
        self.store: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key not in self.store:
            self.misses += 1
            return None
        
        entry = self.store[key]
        if entry.is_expired():
            del self.store[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in cache with optional TTL (in seconds)."""
        if len(self.store) >= self.max_size:
            # Simple eviction: remove oldest entry
            oldest_key = min(self.store.keys(), 
                            key=lambda k: self.store[k].created_at)
            del self.store[oldest_key]
            logger.debug(f"Cache evicted {oldest_key} (size: {self.max_size})")
        
        self.store[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str):
        """Remove entry from cache."""
        if key in self.store:
            del self.store[key]
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (simple prefix match)."""
        keys_to_delete = [k for k in self.store.keys() if k.startswith(pattern)]
        for key in keys_to_delete:
            del self.store[key]
        if keys_to_delete:
            logger.debug(f"Invalidated {len(keys_to_delete)} cache entries matching '{pattern}'")
    
    def clear(self):
        """Clear entire cache."""
        self.store.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "size": len(self.store),
            "max_size": self.max_size,
        }
    
    def __repr__(self):
        stats = self.get_stats()
        return f"InMemoryCache({stats})"


class Cache:
    """
    Unified cache interface supporting both in-memory and Redis backends.
    Falls back to in-memory if Redis unavailable.
    """
    
    def __init__(self, redis_url: Optional[str] = None, use_redis: bool = False):
        self.redis_client = None
        self.in_memory = InMemoryCache()
        
        if use_redis and REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        return self.in_memory.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        if self.redis_client:
            try:
                serialized = json.dumps(value, default=str)
                self.redis_client.setex(key, ttl or 3600, serialized)
                return
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        self.in_memory.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete value from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        self.in_memory.delete(key)
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis pattern invalidation error: {e}")
        
        self.in_memory.invalidate_pattern(pattern)
    
    def get_or_compute(self, key: str, compute_fn: Callable[[], Any], 
                       ttl: Optional[int] = 3600) -> Any:
        """
        Get value from cache, or compute and cache if missing.
        
        Args:
            key: Cache key
            compute_fn: Function to call if cache miss
            ttl: Time-to-live in seconds (default 1 hour)
        
        Returns:
            Cached or computed value
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        
        try:
            value = compute_fn()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Error computing cache value for {key}: {e}")
            raise
    
    def clear(self):
        """Clear entire cache."""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"Redis flush error: {e}")
        
        self.in_memory.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "backend": "redis" if self.redis_client else "memory",
            "memory": self.in_memory.get_stats(),
        }
    
    def __repr__(self):
        return f"Cache({self.get_stats()})"


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(ttl=1800, key_prefix="daily_summary")
        def get_daily_summary(db, date):
            return expensive_query(db, date)
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix or func.__name__}:"
            
            # Include relevant args (skip 'db' sessions)
            for arg in args:
                if not isinstance(arg, object) or not hasattr(arg, '__tablename__'):
                    cache_key += str(arg) + ":"
            
            for k, v in sorted(kwargs.items()):
                if k != 'db':
                    cache_key += f"{k}={v}:"
            
            # Hash long keys
            if len(cache_key) > 100:
                cache_key = hashlib.sha256(cache_key.encode()).hexdigest()
            
            # Get from cache or compute
            result = _global_cache.get_or_compute(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl
            )
            return result
        
        return wrapper
    return decorator


# Global cache instance
_global_cache = Cache()


def get_cache() -> Cache:
    """Get the global cache instance."""
    return _global_cache


def initialize_cache(redis_url: Optional[str] = None):
    """Initialize cache with optional Redis backend."""
    global _global_cache
    _global_cache = Cache(redis_url=redis_url, use_redis=bool(redis_url))
    logger.info(f"Cache initialized: {_global_cache}")
