import logging
from datetime import datetime
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Alert:
    def __init__(self, title: str, message: str, level: AlertLevel, source: str):
        self.title = title
        self.message = message
        self.level = level
        self.source = source
        self.timestamp = datetime.now()
        self.resolved = False

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved
        }

class AlertManager:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_triggers = {}

    def check_performance_alerts(self, metrics: Dict):
        """Revisar y generar alertas de performance"""
        avg_response = metrics.get('avg_response_time', 0)
        error_rate = metrics.get('error_rate', 0)
        
        if avg_response > 1.0:
            self.add_alert(
                "Tiempo de respuesta elevado",
                f"El API está respondiendo en {avg_response:.2f}s (límite: 1.0s)",
                AlertLevel.HIGH,
                "performance"
            )
        
        if error_rate > 0.05:
            self.add_alert(
                "Tasa de error alta",
                f"Tasa de error del {error_rate:.1%} detectada",
                AlertLevel.HIGH,
                "errors"
            )

    def check_business_alerts(self):
        """Alertas específicas del negocio de yoga"""
        ocupacion_promedio = 0.78
        
        if ocupacion_promedio < 0.3:
            self.add_alert(
                "Baja ocupación de clases",
                f"Ocupación promedio: {ocupacion_promedio:.0%} - Recomendado >30%",
                AlertLevel.MEDIUM,
                "business"
            )

    def add_alert(self, title: str, message: str, level: AlertLevel, source: str):
        """Agregar una nueva alerta"""
        for alert in self.alerts:
            if (alert.title == title and 
                not alert.resolved and 
                (datetime.now() - alert.timestamp).seconds < 300):
                return
        
        new_alert = Alert(title, message, level, source)
        self.alerts.append(new_alert)
        logger.warning(f"ALERTA {level.value}: {title} - {message}")

    def resolve_alert(self, title: str) -> bool:
        """Marcar alerta como resuelta"""
        for alert in self.alerts:
            if alert.title == title and not alert.resolved:
                alert.resolved = True
                logger.info(f"Alerta resuelta: {title}")
                return True
        return False

    def get_active_alerts(self) -> List[Dict]:
        """Obtener alertas activas (no resueltas)"""
        return [alert.to_dict() for alert in self.alerts if not alert.resolved]

    def get_alert_stats(self) -> Dict:
        """Estadísticas simples de alertas"""
        active = self.get_active_alerts()
        return {
            "total_active": len(active),
            "by_level": {
                "high": len([a for a in active if a["level"] == "high"]),
                "medium": len([a for a in active if a["level"] == "medium"]),
                "low": len([a for a in active if a["level"] == "low"])
            }
        }

alert_manager = AlertManager()

from fastapi import APIRouter

router = APIRouter()

@router.get("/alerts")
async def get_alerts():
    """Obtener alertas activas"""
    return {
        "status": "success",
        "alerts": alert_manager.get_active_alerts(),
        "stats": alert_manager.get_alert_stats()
    }

@router.post("/alerts/resolve")
async def resolve_alert(alert_title: str):
    """Resolver una alerta por título"""
    success = alert_manager.resolve_alert(alert_title)
    return {
        "status": "success" if success else "error",
        "message": f"Alerta '{alert_title}' resuelta" if success else "Alerta no encontrada"
    }

@router.delete("/alerts")
async def clear_resolved_alerts():
    """Limpiar alertas resueltas (mantenimiento)"""
    initial_count = len(alert_manager.alerts)
    alert_manager.alerts = [alert for alert in alert_manager.alerts if not alert.resolved]
    cleared_count = initial_count - len(alert_manager.alerts)
    
    return {
        "status": "success",
        "message": f"Se limpiaron {cleared_count} alertas resueltas"
    }