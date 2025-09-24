import redis.asyncio as redis
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.connection: Optional[redis.Redis] = None

    async def connect(self):
        """Establecer conexión con Redis"""
        try:
            self.connection = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            await self.connection.ping()
            logger.info("Conexión Redis establecida exitosamente")
        except Exception as e:
            logger.error(f"Error conectando a Redis: {e}")
            raise

    async def disconnect(self):
        """Cerrar conexión con Redis"""
        if self.connection:
            await self.connection.close()
            logger.info("Conexión Redis cerrada")

    async def set(self, key: str, value: Any, expire: int = 3600):
        """Guardar valor en cache"""
        try:
            serialized_value = json.dumps(value)
            await self.connection.setex(key, expire, serialized_value)
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        try:
            value = await self.connection.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo del cache: {e}")
            return None

    async def delete(self, key: str):
        """Eliminar clave del cache"""
        try:
            await self.connection.delete(key)
        except Exception as e:
            logger.error(f"Error eliminando del cache: {e}")

    async def exists(self, key: str) -> bool:
        """Verificar si clave existe"""
        try:
            return await self.connection.exists(key) == 1
        except Exception as e:
            logger.error(f"Error verificando existencia: {e}")
            return False

redis_client = RedisClient()