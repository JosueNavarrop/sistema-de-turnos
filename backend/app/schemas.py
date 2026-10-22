"""Esquemas de entrada de la API (Pydantic) y funciones que dan forma a las respuestas."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .models import Servicio, Turno, Usuario, Ventanilla


class LoginIn(BaseModel):
    usuario: str = Field(min_length=1, max_length=50)
    contrasena: str = Field(min_length=1)


class ServicioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    prefijo: str = Field(min_length=1, max_length=1)
    descripcion: str | None = Field(default=None, max_length=200)
    activo: bool = True

    @field_validator("prefijo")
    @classmethod
    def prefijo_letra(cls, v: str) -> str:
        v = v.strip().upper()
        if not v.isalpha():
            raise ValueError("El prefijo debe ser una letra")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre es obligatorio")
        return v


class VentanillaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=30)
    activo: bool = True
    servicios: list[int] = []


class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    usuario: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9._-]+$")
    contrasena: str | None = Field(default=None, min_length=6)
    rol: Literal["ADMIN", "RECEPCIONISTA"]
    id_ventanilla: int | None = None
    activo: bool = True


class TurnoIn(BaseModel):
    id_servicio: int


class EstadoIn(BaseModel):
    estado: Literal["ATENDIDO", "NO_PRESENTADO", "CANCELADO"]


# ---------- Respuestas ----------

def servicio_out(s: Servicio) -> dict:
    return {"id_servicio": s.id_servicio, "nombre": s.nombre, "prefijo": s.prefijo,
            "descripcion": s.descripcion, "activo": s.activo}


def usuario_out(u: Usuario) -> dict:
    return {"id_usuario": u.id_usuario, "nombre": u.nombre, "usuario": u.usuario, "rol": u.rol,
            "id_ventanilla": u.id_ventanilla, "ventanilla": u.ventanilla.nombre if u.ventanilla else None,
            "activo": u.activo, "ultimo_acceso": u.ultimo_acceso}


def ventanilla_out(v: Ventanilla, turno_actual: str | None = None) -> dict:
    recep = [u.nombre for u in v.usuarios if u.activo and u.rol == "RECEPCIONISTA"]
    return {"id_ventanilla": v.id_ventanilla, "nombre": v.nombre, "activo": v.activo,
            "servicios": [servicio_out(s) for s in v.servicios],
            "recepcionistas": recep, "turno_actual": turno_actual}


def turno_out(t: Turno) -> dict:
    return {"id_turno": t.id_turno, "codigo": t.codigo, "numero": t.numero, "fecha": t.fecha,
            "estado": t.estado, "id_servicio": t.id_servicio, "servicio": t.servicio.nombre,
            "prefijo": t.servicio.prefijo, "hora_creacion": t.hora_creacion, "hora_llamado": t.hora_llamado,
            "hora_fin": t.hora_fin, "id_ventanilla": t.id_ventanilla,
            "ventanilla": t.ventanilla.nombre if t.ventanilla else None,
            "atendio": t.usuario.nombre if t.usuario else None,
            "espera_min": round((t.hora_llamado - t.hora_creacion).total_seconds() / 60) if t.hora_llamado else None}
