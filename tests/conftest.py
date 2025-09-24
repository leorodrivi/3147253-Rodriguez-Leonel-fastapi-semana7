import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from app.main import app

os.environ["TESTING"] = "true"

@pytest.fixture(scope="session")
def event_loop():
    """Crear instancia del event loop para async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_client():
    """Client de testing para FastAPI"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
async def setup_cache():
    """Setup para tests de cache"""
    from app.cache.redis_client import redis_client
    from app.cache.cache_manager import cache_manager
    
    import redis.asyncio as redis
    from unittest.mock import AsyncMock, MagicMock
    
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = 1
    mock_redis.keys.return_value = []
    
    redis_client.connection = mock_redis
    redis_client.connection.keys = AsyncMock(return_value=[])
    redis_client.connection.delete = AsyncMock(return_value=1)
    
    yield redis_client, cache_manager
    
    redis_client.connection = None

@pytest.fixture(scope="function")
async def setup_database():
    """Setup de base de datos simulada para tests"""
    from app.routes.optimized_api import clases_db, reservas_db, instructores_db
    
    test_clases = {
        1: {
            "id": 1,
            "nombre": "Yoga Principiantes",
            "descripcion": "Clase para iniciantes",
            "instructor_id": 1,
            "tipo": "hatha",
            "nivel": "principiante", 
            "duracion_minutos": 60,
            "capacidad_maxima": 20,
            "precio": 25.0,
            "horario": "09:00:00",
            "dias_semana": [1, 3, 5],
            "activa": True,
            "fecha_creacion": "2024-01-01T00:00:00",
            "fecha_actualizacion": "2024-01-01T00:00:00"
        }
    }
    
    test_instructores = {
        1: {
            "id": 1, 
            "nombre": "Ana García",
            "especialidades": ["hatha", "restaurativo"],
            "experiencia_anios": 5,
            "calificacion": 4.8
        }
    }
    
    clases_db.clear()
    clases_db.update(test_clases)
    
    reservas_db.clear()
    
    instructores_db.clear()
    instructores_db.update(test_instructores)
    
    yield clases_db, reservas_db, instructores_db
    
    clases_db.clear()
    reservas_db.clear()
    instructores_db.clear()

@pytest.fixture(scope="function")
def sample_clase_data():
    """Datos de ejemplo para una clase de yoga"""
    return {
        "nombre": "Yoga Intermedio",
        "descripcion": "Clase para nivel intermedio",
        "instructor_id": 1,
        "tipo": "vinyasa",
        "nivel": "intermedio",
        "duracion_minutos": 75,
        "capacidad_maxima": 15,
        "precio": 30.0,
        "horario": "18:00:00",
        "dias_semana": [2, 4]
    }