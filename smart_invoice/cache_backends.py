"""
Smart Invoice - Intelligent Caching Layer
Provides Redis caching with automatic fallback to LocMemCache
"""
import logging
from django.core.cache.backends.locmem import LocMemCache as DjangoLocMemCache
from django.core.cache.backends.redis import RedisCache as DjangoRedisCache
from django.core.cache import InvalidCacheBackendError

logger = logging.getLogger(__name__)


class ResilientCacheBackend:
    """
    Intelligent cache backend that attempts Redis first, falls back to LocMemCache.
    Provides transparent caching with automatic fallback on Redis failures.
    """
    
    def __init__(self, server, params):
        self.server = server
        self.params = params
        self.using_redis = False
        self._primary_cache = None
        self._fallback_cache = None
        
        # Try to initialize Redis first
        try:
            self._primary_cache = DjangoRedisCache(server, params)
            self.using_redis = True
            logger.info("✓ Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"⚠ Redis unavailable, falling back to LocMemCache: {e}")
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """Initialize LocMemCache as fallback."""
        try:
            self._fallback_cache = DjangoLocMemCache(
                'fallback', 
                {'MAX_ENTRIES': 1000, 'CULL_FREQUENCY': 3}
            )
            logger.info("✓ LocMemCache fallback initialized")
        except Exception as e:
            logger.error(f"✗ Critical: Both caches failed to initialize: {e}")
            raise
    
    @property
    def _cache(self):
        """Get active cache backend."""
        if self.using_redis and self._primary_cache:
            return self._primary_cache
        return self._fallback_cache
    
    def add(self, key, value, timeout=None, version=None):
        """Add a value to the cache if the key does not already exist."""
        try:
            return self._cache.add(key, value, timeout, version)
        except Exception as e:
            logger.error(f"Cache add failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.add(key, value, timeout, version)
            return False
    
    def get(self, key, default=None, version=None):
        """Fetch a value from the cache."""
        try:
            return self._cache.get(key, default, version)
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.get(key, default, version)
            return default
    
    def set(self, key, value, timeout=None, version=None):
        """Set a value in the cache."""
        try:
            return self._cache.set(key, value, timeout, version)
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.set(key, value, timeout, version)
            return False
    
    def delete(self, key, version=None):
        """Delete a value from the cache."""
        try:
            return self._cache.delete(key, version)
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.delete(key, version)
            return False
    
    def clear(self):
        """Clear the entire cache."""
        try:
            return self._cache.clear()
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.clear()
            return False
    
    def _handle_redis_failure(self):
        """Handle Redis connection failure by switching to fallback."""
        if self.using_redis:
            logger.warning("⚠ Switching from Redis to LocMemCache fallback due to errors")
            self.using_redis = False
            if not self._fallback_cache:
                self._initialize_fallback()
    
    def get_many(self, keys, version=None):
        """Fetch multiple values from the cache."""
        try:
            return self._cache.get_many(keys, version)
        except Exception as e:
            logger.error(f"Cache get_many failed: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.get_many(keys, version)
            return {}
    
    def set_many(self, data, timeout=None, version=None):
        """Set multiple values in the cache."""
        try:
            return self._cache.set_many(data, timeout, version)
        except Exception as e:
            logger.error(f"Cache set_many failed: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.set_many(data, timeout, version)
            return []
    
    def delete_many(self, keys, version=None):
        """Delete multiple values from the cache."""
        try:
            return self._cache.delete_many(keys, version)
        except Exception as e:
            logger.error(f"Cache delete_many failed: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.delete_many(keys, version)
    
    def has_key(self, key, version=None):
        """Check if a key exists in the cache."""
        try:
            return self._cache.has_key(key, version)
        except Exception as e:
            logger.error(f"Cache has_key failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.has_key(key, version)
            return False
    
    def incr(self, key, delta=1, version=None):
        """Increment a value in the cache."""
        try:
            return self._cache.incr(key, delta, version)
        except Exception as e:
            logger.error(f"Cache incr failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.incr(key, delta, version)
            raise ValueError("Key does not exist")
    
    def decr(self, key, delta=1, version=None):
        """Decrement a value in the cache."""
        try:
            return self._cache.decr(key, delta, version)
        except Exception as e:
            logger.error(f"Cache decr failed for key {key}: {e}")
            if self.using_redis:
                self._handle_redis_failure()
                return self._fallback_cache.decr(key, delta, version)
            raise ValueError("Key does not exist")
