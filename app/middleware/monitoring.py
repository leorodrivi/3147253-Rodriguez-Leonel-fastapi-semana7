from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from monitoring.metrics_collector import metrics_collector

logger = logging.getLogger(__name__)

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            if response.status_code >= 400:
                await metrics_collector.record_error(
                    path=request.url.path,
                    status_code=response.status_code,
                    method=request.method
                )

            return response

        except Exception as e:
            logger.error(f"Error no manejado en {request.url.path}: {e}")
            await metrics_collector.record_exception(
                path=request.url.path,
                exception_type=type(e).__name__
            )
            raise e