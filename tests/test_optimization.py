import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from app.routes.optimized_api import router
from app.models.optimized import ClaseYogaCreate, ClaseYogaUpdate
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Client de testing para FastAPI"""
    return TestClient(app)

@pytest.mark.asyncio
class TestAPIOptimization:
    """Tests de optimización de la API"""
    
    async def test_response_time_optimization(self, client, setup_database):
        """Test de tiempo de respuesta de endpoints"""
        start_time = time.time()
        response = client.get("/api/v1/clases")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0
    
    async def test_cache_optimization(self, client, setup_database):
        """Test de optimización por cache"""
        response1 = client.get("/api/v1/clases")
        assert response1.status_code == 200
        data1 = response1.json()
        
        start_time = time.time()
        response2 = client.get("/api/v1/clases")
        response_time = time.time() - start_time
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data1 == data2
        assert response_time < 0.5
    
    async def test_concurrent_requests(self, client, setup_database):
        """Test de manejo de requests concurrentes"""
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/api/v1/clases")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0
        assert all(status == 200 for status in results)

@pytest.mark.asyncio
class TestBusinessLogicOptimization:
    """Tests de optimización de lógica de negocio"""
    
    async def test_reservation_optimization(self, client, setup_database):
        """Test de optimización en el sistema de reservas"""
        response = client.post("/api/v1/clases/1/reservar?usuario_id=100")
        assert response.status_code == 200
        
        for i in range(25):
            response = client.post(f"/api/v1/clases/1/reservar?usuario_id={100 + i}")
        
        assert response.status_code == 400
        assert "Clase llena" in response.json()["detail"]

class TestMonitoringOptimization:
    """Tests de optimización del sistema de monitoreo"""
    
    def test_metrics_efficiency(self):
        """Test de eficiencia en colección de métricas"""
        from monitoring.metrics_collector import metrics_collector
        
        start_time = time.time()
        
        for i in range(100):
            metrics_collector.record_request(
                path=f"/api/v1/clases/{i}",
                method="GET", 
                status_code=200,
                response_time=0.1
            )
        
        collection_time = time.time() - start_time
        assert collection_time < 0.1
    
    def test_alert_system_performance(self):
        """Test de performance del sistema de alertas"""
        from monitoring.alerts import alert_manager
        
        start_time = time.time()
        
        for i in range(100):
            alert_manager.add_alert(
                f"Test Alert {i}",
                f"Message {i}",
                "high" if i % 10 == 0 else "medium",
                "test"
            )
        
        generation_time = time.time() - start_time
        assert generation_time < 0.05

def test_enum_optimization():
    """Test de optimización usando Enums"""
    from app.models.optimized import TipoYoga, NivelDificultad
    
    assert TipoYoga.HATHA == "hatha"
    assert NivelDificultad.PRINCIPIANTE == "principiante"
    
    import time
    
    start = time.time()
    for _ in range(10000):
        if TipoYoga.HATHA == TipoYoga.HATHA:
            pass
    enum_time = time.time() - start
    
    start = time.time()
    for _ in range(10000):
        if "hatha" == "hatha":
            pass
    string_time = time.time() - start
    
    assert enum_time < string_time * 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])