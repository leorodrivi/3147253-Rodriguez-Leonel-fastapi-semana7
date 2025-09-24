from fastapi import FastAPI
from contextlib import asynccontextmanager
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.performance import PerformanceMiddleware
from middleware.monitoring import MonitoringMiddleware
from monitoring.metrics_collector import metrics_collector
from monitoring.alerts import alert_manager, router as alerts_router
from routes.optimized_api import router as api_router
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación Centro de Yoga Paz Interior")
    
    if os.getenv("TESTING") != "true":
        await metrics_collector.start()
    
    yield
    
    if os.getenv("TESTING") != "true":
        await metrics_collector.stop()
    logger.info("Apagando aplicación")

app = FastAPI(
    title="Centro de Yoga Paz Interior - API",
    description="Sistema optimizado de gestión de clases de yoga",
    version="1.0.0",
    lifespan=lifespan
)

if os.getenv("TESTING") != "true":
    app.add_middleware(RateLimiterMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(MonitoringMiddleware)

app.include_router(api_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1/alerts")

@app.get("/")
async def root():
    return {
        "message": "Bienvenido al Centro de Yoga Paz Interior",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/status")
async def system_status():
    """Estado completo del sistema con métricas y alertas"""
    if os.getenv("TESTING") == "true":
        return {"status": "healthy", "mode": "testing"}
    
    metrics = metrics_collector.get_metrics_summary()
    
    alert_manager.check_performance_alerts(metrics)
    alert_manager.check_business_alerts()
    
    return {
        "status": "healthy",
        "metrics": metrics,
        "alerts": {
            "active": alert_manager.get_active_alerts(),
            "stats": alert_manager.get_alert_stats()
        }
    }

if __name__ == "__main__" and os.getenv("TESTING") != "true":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=False
    )