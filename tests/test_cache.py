import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.cache.redis_client import RedisClient, redis_client
from app.cache.cache_manager import CacheManager, cache_manager
import json

@pytest.mark.asyncio
class TestRedisClient:
    """Tests para el cliente Redis"""
    
    async def test_redis_connection(self, setup_cache):
        """Test de conexión a Redis"""
        redis_client, _ = setup_cache
        await redis_client.connect()
        assert redis_client.connection is not None
    
    async def test_set_and_get_value(self, setup_cache):
        """Test de guardar y obtener valores del cache"""
        redis_client, _ = setup_cache
        
        test_key = "test_key"
        test_value = {"clase_id": 1, "nombre": "Yoga Principiantes"}
        
        redis_client.connection.setex = AsyncMock(return_value=True)
        
        redis_client.connection.get = AsyncMock(return_value=json.dumps(test_value))
        
        await redis_client.set(test_key, test_value)
        redis_client.connection.setex.assert_called_once()
        
        result = await redis_client.get(test_key)
        assert result == test_value
        redis_client.connection.get.assert_called_once_with(test_key)
    
    async def test_get_nonexistent_key(self, setup_cache):
        """Test de obtener clave que no existe"""
        redis_client, _ = setup_cache
        
        redis_client.connection.get = AsyncMock(return_value=None)
        result = await redis_client.get("key_inexistente")
        assert result is None

@pytest.mark.asyncio 
class TestCacheManager:
    """Tests para el gestor de cache"""
    
    async def test_generate_key(self):
        """Test de generación de claves de cache"""
        cache_manager = CacheManager()
        key = cache_manager._generate_key("test_func", "arg1", kwarg1="value1")
        
        assert key.startswith("yoga_")
        assert len(key) > 10
    
    async def test_cached_decorator_hit(self, setup_cache):
        """Test de decorador cached - cache hit"""
        _, cache_manager = setup_cache
        
        mock_func = AsyncMock(return_value={"data": "test"})
        
        cache_manager.redis_client.get = AsyncMock(return_value={"data": "cached"})
        
        decorated_func = cache_manager.cached(expire=300)(mock_func)
        result = await decorated_func("test_arg")
        
        assert result == {"data": "cached"}
        mock_func.assert_not_called()
    
    async def test_cached_decorator_miss(self, setup_cache):
        """Test de decorador cached - cache miss"""
        _, cache_manager = setup_cache
        
        mock_func = AsyncMock(return_value={"data": "fresh"})
        
        cache_manager.redis_client.get = AsyncMock(return_value=None)
        cache_manager.redis_client.set = AsyncMock()
        
        decorated_func = cache_manager.cached(expire=300)(mock_func)
        result = await decorated_func("test_arg")
        
        assert result == {"data": "fresh"}
        mock_func.assert_called_once()

@pytest.mark.asyncio
class TestCacheIntegration:
    """Tests de integración del sistema de cache"""
    
    async def test_cache_performance(self, setup_cache):
        """Test de performance del cache"""
        import time
        
        _, cache_manager = setup_cache
        
        async def slow_function():
            await asyncio.sleep(0.01)
            return {"data": "resultado"}
        
        cache_manager.redis_client.get = AsyncMock(return_value=None)
        cache_manager.redis_client.set = AsyncMock()
        
        cached_function = cache_manager.cached(expire=60)(slow_function)
        
        start_time = time.time()
        result1 = await cached_function()
        first_call_time = time.time() - start_time
        
        cache_manager.redis_client.get = AsyncMock(return_value=result1)
        
        start_time = time.time()
        result2 = await cached_function()
        second_call_time = time.time() - start_time
        
        assert result1 == result2
        assert second_call_time < first_call_time

if __name__ == "__main__":
    pytest.main([__file__, "-v"])