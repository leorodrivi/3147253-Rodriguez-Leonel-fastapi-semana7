from fastapi import APIRouter
from monitoring.metrics_collector import metrics_collector
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/metrics")
async def get_metrics_dashboard():
    """Endpoint del dashboard de métricas"""
    try:
        summary = metrics_collector.get_metrics_summary()
        
        yoga_metrics = {
            "performance": {
                "response_time": summary["avg_response_time"],
                "max_response_time": summary["max_response_time"],
                "requests_per_hour": summary["requests_last_hour"]
            },
            "reliability": {
                "error_rate": summary["error_rate"],
                "total_errors": summary["errors_last_hour"]
            },
            "business": {
                "clases_activas": 15,
                "reservas_hoy": 47,
                "ocupacion_promedio": 0.78
            }
        }
        
        return {
            "status": "success",
            "timestamp": summary["timestamp"],
            "metrics": yoga_metrics
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        return {
            "status": "error",
            "message": "Error obteniendo métricas"
        }