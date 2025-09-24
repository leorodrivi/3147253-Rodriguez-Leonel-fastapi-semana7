"""
Modelos de datos para el Centro de Yoga Paz Interior
Modelos Pydantic optimizados para la gestión de clases de yoga
"""

from .optimized import (
    ClaseYogaBase,
    ClaseYogaCreate,
    ClaseYogaUpdate,
    ClaseYogaResponse,
    ClaseConDisponibilidad,
    ReservaClase,
    Instructor,
    NivelDificultad,
    TipoYoga
)

__all__ = [
    'ClaseYogaBase',
    'ClaseYogaCreate',
    'ClaseYogaUpdate',
    'ClaseYogaResponse',
    'ClaseConDisponibilidad',
    'ReservaClase',
    'Instructor',
    'NivelDificultad',
    'TipoYoga'
]