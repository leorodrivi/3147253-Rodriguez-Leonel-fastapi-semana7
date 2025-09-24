import time
from typing import Dict, List
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "requests": [],
            "errors": [],
            "events": [],
            "response_times": []
        }
        self.is_running = False
        self.task = None

    async def start(self):
        """Iniciar recolector de métricas"""
        self.is_running = True
        self.task = asyncio.create_task(self._cleanup_loop())
        logger.info("Metrics collector started")

    async def stop(self):
        """Detener recolector de métricas"""
        self.is_running = False
        if self.task:
            self.task.cancel()
        logger.info("Metrics collector stopped")

    async def _cleanup_loop(self):
        """Loop de limpieza de métricas antiguas"""
        while self.is_running:
            await asyncio.sleep(300)  # Cada 5 minutos
            self._cleanup_old_metrics()

    def _cleanup_old_metrics(self):
        """Limpiar métricas más antiguas de 1 hora"""
        one_hour_ago = time.time() - 3600
        for metric_type in self.metrics:
            self.metrics[metric_type] = [
                m for m in self.metrics[metric_type] 
                if m.get("timestamp", 0) > one_hour_ago
            ]

    async def record_request(self, path: str, method: str, status_code: int, response_time: float):
        """Registrar métrica de request"""
        metric = {
            "timestamp": time.time(),
            "path": path,
            "method": method,
            "status_code": status_code,
            "response_time": response_time
        }
        self.metrics["requests"].append(metric)
        self.metrics["response_times"].append(response_time)

    async def record_error(self, path: str, status_code: int, method: str):
        """Registrar error"""
        error_metric = {
            "timestamp": time.time(),
            "path": path,
            "status_code": status_code,
            "method": method
        }
        self.metrics["errors"].append(error_metric)

    async def record_exception(self, path: str, exception_type: str):
        """Registrar excepción"""
        exception_metric = {
            "timestamp": time.time(),
            "path": path,
            "exception_type": exception_type
        }
        self.metrics["errors"].append(exception_metric)

    async def record_event(self, event_type: str, metadata: Dict):
        """Registrar evento personalizado"""
        event_metric = {
            "timestamp": time.time(),
            "event_type": event_type,
            "metadata": metadata
        }
        self.metrics["events"].append(event_metric)

    def get_metrics_summary(self) -> Dict:
        """Obtener resumen de métricas"""
        now = time.time()
        one_hour_ago = now - 3600

        recent_requests = [r for r in self.metrics["requests"] if r["timestamp"] > one_hour_ago]
        recent_errors = [e for e in self.metrics["errors"] if e["timestamp"] > one_hour_ago]

        if recent_requests:
            response_times = [r["response_time"] for r in recent_requests]
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = max_response_time = 0

        return {
            "requests_last_hour": len(recent_requests),
            "errors_last_hour": len(recent_errors),
            "avg_response_time": round(avg_response_time, 3),
            "max_response_time": round(max_response_time, 3),
            "error_rate": len(recent_errors) / max(len(recent_requests), 1),
            "timestamp": datetime.now().isoformat()
        }

metrics_collector = MetricsCollector()