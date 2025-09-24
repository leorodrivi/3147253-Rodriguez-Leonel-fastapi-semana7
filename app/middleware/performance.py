import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from monitoring.metrics_collector import metrics_collector

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        await metrics_collector.record_request(
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time=process_time
        )

        if process_time > 1.0:
            logger.warning(
                f"Lentitud detectada en {request.url.path}: "
                f"{process_time:.3f}s"
            )

        return response