from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, time
from enum import Enum

class NivelDificultad(str, Enum):
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"

class TipoYoga(str, Enum):
    HATHA = "hatha"
    VINYASA = "vinyasa"
    ASHTANGA = "ashtanga"
    KUNDALINI = "kundalini"
    RESTAURATIVO = "restaurativo"

class ClaseYogaBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    instructor_id: int
    tipo: TipoYoga
    nivel: NivelDificultad
    duracion_minutos: int = Field(..., ge=30, le=120)
    capacidad_maxima: int = Field(..., ge=1, le=50)
    precio: float = Field(..., ge=0)

class ClaseYogaCreate(ClaseYogaBase):
    horario: time
    dias_semana: List[int] = Field(..., min_items=1, max_items=7)

class ClaseYogaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    duracion_minutos: Optional[int] = Field(None, ge=30, le=120)
    capacidad_maxima: Optional[int] = Field(None, ge=1, le=50)
    precio: Optional[float] = Field(None, ge=0)
    activa: Optional[bool] = None

class ClaseYogaResponse(ClaseYogaBase):
    id: int
    horario: time
    dias_semana: List[int]
    activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

class ReservaClase(BaseModel):
    usuario_id: int
    clase_id: int
    fecha: datetime
    estado: str = "confirmada"

class Instructor(BaseModel):
    id: int
    nombre: str
    especialidades: List[TipoYoga]
    experiencia_anios: int
    calificacion: float

class ClaseConDisponibilidad(ClaseYogaResponse):
    cupos_disponibles: int
    instructor: Instructor