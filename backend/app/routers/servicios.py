from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Servicio, Turno
from ..schemas import ServicioIn, servicio_out
from ..security import requiere_rol
from ..turnos import hoy

router = APIRouter(prefix="/api/servicios", tags=["Servicios"])


@router.get("")
def listar(activos: bool = False, db: Session = Depends(get_db)):
    """Lista de servicios. El kiosco pide solo los activos (RN-04)."""
    q = select(Servicio).order_by(Servicio.id_servicio)
    if activos:
        q = q.where(Servicio.activo.is_(True))
    hoy_por_servicio = dict(db.execute(
        select(Turno.id_servicio, func.count()).where(Turno.fecha == hoy()).group_by(Turno.id_servicio)).all())
    return [servicio_out(s) | {"turnos_hoy": hoy_por_servicio.get(s.id_servicio, 0)} for s in db.scalars(q)]


def _validar_prefijo(db: Session, prefijo: str, id_actual: int | None = None):
    otro = db.scalar(select(Servicio).where(Servicio.prefijo == prefijo))
    if otro and otro.id_servicio != id_actual:
        raise HTTPException(status.HTTP_409_CONFLICT, f"El prefijo «{prefijo}» ya lo usa «{otro.nombre}»")


@router.post("", status_code=201, dependencies=[Depends(requiere_rol("ADMIN"))])
def crear(datos: ServicioIn, db: Session = Depends(get_db)):
    """RF-02 · CU-02."""
    _validar_prefijo(db, datos.prefijo)
    servicio = Servicio(**datos.model_dump())
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio_out(servicio)


@router.put("/{id_servicio}", dependencies=[Depends(requiere_rol("ADMIN"))])
def editar(id_servicio: int, datos: ServicioIn, db: Session = Depends(get_db)):
    servicio = db.get(Servicio, id_servicio)
    if servicio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Servicio no encontrado")
    _validar_prefijo(db, datos.prefijo, id_servicio)
    for campo, valor in datos.model_dump().items():
        setattr(servicio, campo, valor)
    db.commit()
    return servicio_out(servicio)
