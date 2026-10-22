from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Servicio, Turno, Ventanilla
from ..schemas import VentanillaIn, ventanilla_out
from ..security import get_usuario, requiere_rol
from ..turnos import hoy

router = APIRouter(prefix="/api/ventanillas", tags=["Ventanillas"])


@router.get("", dependencies=[Depends(get_usuario)])
def listar(db: Session = Depends(get_db)):
    abiertos = dict(db.execute(select(Turno.id_ventanilla, Turno.codigo).where(
        Turno.estado == "LLAMADO", Turno.fecha == hoy())).all())
    return [ventanilla_out(v, abiertos.get(v.id_ventanilla))
            for v in db.scalars(select(Ventanilla).order_by(Ventanilla.id_ventanilla))]


def _aplicar(db: Session, v: Ventanilla, datos: VentanillaIn):
    servicios = list(db.scalars(select(Servicio).where(Servicio.id_servicio.in_(datos.servicios)))) if datos.servicios else []
    if len(servicios) != len(set(datos.servicios)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Algún servicio no existe")
    v.nombre = datos.nombre.strip()
    v.activo = datos.activo
    v.servicios = servicios


@router.post("", status_code=201, dependencies=[Depends(requiere_rol("ADMIN"))])
def crear(datos: VentanillaIn, db: Session = Depends(get_db)):
    """RF-08 · CU-08."""
    v = Ventanilla()
    _aplicar(db, v, datos)
    db.add(v)
    db.commit()
    db.refresh(v)
    return ventanilla_out(v)


@router.put("/{id_ventanilla}", dependencies=[Depends(requiere_rol("ADMIN"))])
def editar(id_ventanilla: int, datos: VentanillaIn, db: Session = Depends(get_db)):
    v = db.get(Ventanilla, id_ventanilla)
    if v is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ventanilla no encontrada")
    _aplicar(db, v, datos)
    db.commit()
    return ventanilla_out(v)
