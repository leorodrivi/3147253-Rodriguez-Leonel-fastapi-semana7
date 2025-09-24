from typing import Optional, Any, Callable
import hashlib
import json
from cache.redis_client import redis_client
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.prefix = "yoga_"

    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generar clave única para cache basada en parámetros"""
        key_data = f"{func_name}:{args}:{kwargs}"
        return f"{self.prefix}{hashlib.md5(key_data.encode()).hexdigest()}"

    async def cached(
        self, 
        expire: int = 300, 
        key_prefix: str = None
    ) -> Callable:
        """
        Decorador para cachear resultados de funciones
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_args = args[1:] if args and hasattr(args[0], '__class__') else args
                
                prefix = key_prefix or func.__name__
                cache_key = self._generate_key(prefix, *cache_args, **kwargs)
                
                cached_result = await redis_client.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit para {cache_key}")
                    return cached_result

                result = await func(*args, **kwargs)
                await redis_client.set(cache_key, result, expire)
                logger.debug(f"Cache miss, guardado para {cache_key}")
                
                return result
            return wrapper
        return decorator

    async def invalidate_pattern(self, pattern: str):
        """Invalidar cache por patrón"""
        try:
            keys = await redis_client.connection.keys(f"{self.prefix}{pattern}*")
            if keys:
                await redis_client.connection.delete(*keys)
                logger.info(f"Invalidadas {len(keys)} claves con patrón {pattern}")
        except Exception as e:
            logger.error(f"Error invalidando cache: {e}")

    async def get_stats(self) -> dict:
        """Obtener estadísticas del cache"""
        try:
            keys = await redis_client.connection.keys(f"{self.prefix}*")
            return {
                "total_keys": len(keys),
                "prefix": self.prefix,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error obteniendo stats del cache: {e}")
            return {"error": str(e)}

cache_manager = CacheManager()