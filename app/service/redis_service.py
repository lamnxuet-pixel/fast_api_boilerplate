import json
import logging
from typing import Optional, Any

import aioredis
from aioredis import Redis

from app.conf.env.redis_config import redis_settings

_log = logging.getLogger(__name__)


class RedisService:
    """Redis service for session management"""
    
    def __init__(self):
        self._redis: Optional[Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            if redis_settings.REDIS_URL:
                self._redis = await aioredis.from_url(redis_settings.REDIS_URL)
            else:
                self._redis = await aioredis.Redis(
                    host=redis_settings.REDIS_HOST,
                    port=redis_settings.REDIS_PORT,
                    password=redis_settings.REDIS_PASSWORD if redis_settings.REDIS_PASSWORD else None,
                    db=redis_settings.REDIS_DB,
                    decode_responses=True
                )
            
            # Test connection
            await self._redis.ping()
            _log.info("Redis connection established successfully")
        except Exception as e:
            _log.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            _log.info("Redis connection closed")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis with optional TTL"""
        try:
            if not self._redis:
                raise Exception("Redis not connected")
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                await self._redis.setex(key, ttl, value)
            else:
                await self._redis.set(key, value)
            
            return True
        except Exception as e:
            _log.error(f"Failed to set Redis key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key from Redis"""
        try:
            if not self._redis:
                raise Exception("Redis not connected")
            
            return await self._redis.get(key)
        except Exception as e:
            _log.error(f"Failed to get Redis key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            if not self._redis:
                raise Exception("Redis not connected")
            
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            _log.error(f"Failed to delete Redis key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            if not self._redis:
                raise Exception("Redis not connected")
            
            result = await self._redis.exists(key)
            return result > 0
        except Exception as e:
            _log.error(f"Failed to check Redis key {key}: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._redis is not None


# Global Redis service instance
redis_service = RedisService()
