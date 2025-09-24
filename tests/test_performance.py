import asyncio
import time
import pytest
from httpx import AsyncClient
from app.main import app
import logging

logger = logging.getLogger(__name__)

class TestPerformance:
    @pytest.mark.asyncio
    async def test_response_time_clases_endpoint(self):
        """Test de tiempo de respuesta para endpoint de clases"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = time.time()
            response = await client.get("/api/v1/clases")
            end_time = time.time()
            
            response_time = end_time - start_time
            logger.info(f"Tiempo de respuesta: {response_time:.3f}s")
            
            assert response.status_code == 200
            assert response_time < 1.0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test de requests concurrentes"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            tasks = [client.get("/api/v1/clases") for _ in range(10)]
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            logger.info(f"10 requests concurrentes en {total_time:.3f}s")
            
            assert all(r.status_code == 200 for r in responses)
            assert total_time < 3.0

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test de performance del cache"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time_1 = time.time()
            await client.get("/api/v1/clases")
            end_time_1 = time.time()
            first_request_time = end_time_1 - start_time_1

            start_time_2 = time.time()
            await client.get("/api/v1/clases")
            end_time_2 = time.time()
            second_request_time = end_time_2 - start_time_2

            logger.info(f"Primera request: {first_request_time:.3f}s")
            logger.info(f"Segunda request: {second_request_time:.3f}s")
            
            assert second_request_time < first_request_time * 0.5