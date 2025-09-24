from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from cache.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/"]:
            return await call_next(request)

        client_ip = request.client.host
        endpoint = request.url.path
        key = f"rate_limit:{client_ip}:{endpoint}"

        try:
            current = await redis_client.connection.get(key)
            if current is None:
                await redis_client.connection.setex(key, self.window, 1)
            else:
                current_count = int(current)
                if current_count >= self.max_requests:
                    logger.warning(f"Rate limit excedido para {client_ip} en {endpoint}")
                    raise HTTPException(
                        status_code=429, 
                        detail="Demasiadas solicitudes. Intente más tarde."
                    )
                await redis_client.connection.incr(key)

            response = await call_next(request)
            return response

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Error en rate limiting: {e}")
            return await call_next(request)