from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from models.optimized import (
    ClaseYogaCreate, 
    ClaseYogaResponse, 
    ClaseYogaUpdate,
    ClaseConDisponibilidad,
    ReservaClase,
    TipoYoga,
    NivelDificultad
)
from cache.cache_manager import cache_manager
from monitoring.metrics_collector import metrics_collector
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

clases_db = {}
reservas_db = {}
instructores_db = {
    1: {"id": 1, "nombre": "Ana García", "especialidades": ["hatha", "restaurativo"], "experiencia_anios": 5, "calificacion": 4.8},
    2: {"id": 2, "nombre": "Carlos López", "especialidades": ["vinyasa", "ashtanga"], "experiencia_anios": 7, "calificacion": 4.9}
}

class_id_counter = 1

@router.post("/clases", response_model=ClaseYogaResponse)
@cache_manager.cached(expire=300)
async def crear_clase(clase: ClaseYogaCreate):
    """Crear nueva clase de yoga"""
    global class_id_counter
    
    try:
        clase_id = class_id_counter
        clase_data = {
            **clase.dict(),
            "id": clase_id,
            "activa": True,
            "fecha_creacion": "2024-01-01T00:00:00",
            "fecha_actualizacion": "2024-01-01T00:00:00"
        }
        
        clases_db[clase_id] = clase_data
        class_id_counter += 1

        await cache_manager.invalidate_pattern("listar_clases")
        
        await metrics_collector.record_event("clase_creada", {"clase_id": clase_id})
        return clase_data

    except Exception as e:
        logger.error(f"Error creando clase: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/clases", response_model=List[ClaseConDisponibilidad])
@cache_manager.cached(expire=180)
async def listar_clases(
    tipo: Optional[TipoYoga] = Query(None),
    nivel: Optional[NivelDificultad] = Query(None),
    instructor_id: Optional[int] = Query(None),
    activa: bool = Query(True)
):
    """Listar clases con filtros y disponibilidad"""
    try:
        clases_filtradas = []
        for clase in clases_db.values():
            if tipo and clase["tipo"] != tipo:
                continue
            if nivel and clase["nivel"] != nivel:
                continue
            if instructor_id and clase["instructor_id"] != instructor_id:
                continue
            if clase["activa"] != activa:
                continue

            reservas_count = sum(1 for r in reservas_db.values() if r["clase_id"] == clase["id"])
            cupos_disponibles = clase["capacidad_maxima"] - reservas_count

            instructor = instructores_db.get(clase["instructor_id"])

            clases_filtradas.append({
                **clase,
                "cupos_disponibles": cupos_disponibles,
                "instructor": instructor
            })

        await metrics_collector.record_event("clases_listadas", {"count": len(clases_filtradas)})
        return clases_filtradas

    except Exception as e:
        logger.error(f"Error listando clases: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/clases/{clase_id}", response_model=ClaseConDisponibilidad)
@cache_manager.cached(expire=240, key_prefix="clase_detalle")
async def obtener_clase(clase_id: int):
    """Obtener detalle de una clase específica"""
    try:
        if clase_id not in clases_db:
            raise HTTPException(status_code=404, detail="Clase no encontrada")

        clase = clases_db[clase_id]
        
        reservas_count = sum(1 for r in reservas_db.values() if r["clase_id"] == clase_id)
        cupos_disponibles = clase["capacidad_maxima"] - reservas_count
        
        instructor = instructores_db.get(clase["instructor_id"])

        return {**clase, "cupos_disponibles": cupos_disponibles, "instructor": instructor}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo clase: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/clases/{clase_id}", response_model=ClaseYogaResponse)
async def actualizar_clase(clase_id: int, clase_update: ClaseYogaUpdate):
    """Actualizar información de una clase"""
    try:
        if clase_id not in clases_db:
            raise HTTPException(status_code=404, detail="Clase no encontrada")

        update_data = clase_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            clases_db[clase_id][field] = value

        clases_db[clase_id]["fecha_actualizacion"] = "2024-01-01T00:00:00"

        await cache_manager.invalidate_pattern("clase_detalle")
        await cache_manager.invalidate_pattern("listar_clases")

        await metrics_collector.record_event("clase_actualizada", {"clase_id": clase_id})
        return clases_db[clase_id]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando clase: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/clases/{clase_id}/reservar", response_model=ReservaClase)
async def reservar_clase(clase_id: int, usuario_id: int):
    """Reservar una clase para un usuario"""
    try:
        if clase_id not in clases_db:
            raise HTTPException(status_code=404, detail="Clase no encontrada")

        clase = clases_db[clase_id]
        if not clase["activa"]:
            raise HTTPException(status_code=400, detail="Clase no disponible")

        reservas_count = sum(1 for r in reservas_db.values() if r["clase_id"] == clase_id)
        if reservas_count >= clase["capacidad_maxima"]:
            raise HTTPException(status_code=400, detail="Clase llena")

        reserva_id = len(reservas_db) + 1
        reserva = {
            "id": reserva_id,
            "usuario_id": usuario_id,
            "clase_id": clase_id,
            "fecha": "2024-01-01T00:00:00",
            "estado": "confirmada"
        }
        reservas_db[reserva_id] = reserva

        await cache_manager.invalidate_pattern("clase_detalle")
        await cache_manager.invalidate_pattern("listar_clases")

        await metrics_collector.record_event("reserva_creada", {
            "clase_id": clase_id,
            "usuario_id": usuario_id
        })

        return reserva

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando reserva: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/metrics/cache")
async def get_cache_metrics():
    """Endpoint para métricas del cache"""
    return await cache_manager.get_stats()