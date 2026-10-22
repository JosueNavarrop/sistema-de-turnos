"""Reglas de negocio de los turnos (RN-01 a RN-05)."""
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import MINUTOS_POR_PERSONA
from .models import Servicio, Turno, Usuario, Ventanilla, ventanilla_servicio


def ahora() -> datetime:
    return datetime.now().replace(microsecond=0)


def hoy() -> date:
    return ahora().date()


def en_espera(db: Session, id_servicio: int) -> int:
    return db.scalar(select(func.count()).select_from(Turno).where(
        Turno.id_servicio == id_servicio, Turno.fecha == hoy(), Turno.estado == "EN_ESPERA")) or 0


def generar_turno(db: Session, id_servicio: int) -> tuple[Turno, int]:
    """RF-03. Devuelve el turno creado y cuántas personas tiene delante."""
    servicio = db.get(Servicio, id_servicio)
    if servicio is None or not servicio.activo:  # RN-04
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El servicio no existe o no está activo")

    for _ in range(3):  # si dos kioscos generan a la vez, la restricción única obliga a reintentar
        delante = en_espera(db, id_servicio)
        ultimo = db.scalar(select(func.max(Turno.numero)).where(
            Turno.id_servicio == id_servicio, Turno.fecha == hoy()).with_for_update())
        numero = (ultimo or 0) + 1  # RN-01: reinicia cada día y por servicio
        turno = Turno(id_servicio=id_servicio, numero=numero, codigo=f"{servicio.prefijo}-{numero:03d}",
                      fecha=hoy(), estado="EN_ESPERA", hora_creacion=ahora())
        db.add(turno)
        try:
            db.commit()
            db.refresh(turno)
            return turno, delante
        except IntegrityError:
            db.rollback()
    raise HTTPException(status.HTTP_409_CONFLICT, "No se pudo generar el turno, intente de nuevo")


def espera_estimada(delante: int) -> int:
    return delante * MINUTOS_POR_PERSONA


def turno_abierto(db: Session, id_ventanilla: int) -> Turno | None:
    return db.scalar(select(Turno).where(
        Turno.id_ventanilla == id_ventanilla, Turno.estado == "LLAMADO", Turno.fecha == hoy()))


def ventanilla_de(usuario: Usuario) -> Ventanilla:
    v = usuario.ventanilla
    if v is None or not v.activo:
        raise HTTPException(status.HTTP_409_CONFLICT, "No tiene una ventanilla activa asignada")
    return v


def llamar_siguiente(db: Session, usuario: Usuario) -> Turno:
    """RF-05."""
    v = ventanilla_de(usuario)
    if turno_abierto(db, v.id_ventanilla):  # RN-03
        raise HTTPException(status.HTTP_409_CONFLICT, "Cierre el turno actual antes de llamar al siguiente")
    siguiente = db.scalar(
        select(Turno)
        .join(ventanilla_servicio, ventanilla_servicio.c.id_servicio == Turno.id_servicio)
        .where(ventanilla_servicio.c.id_ventanilla == v.id_ventanilla,
               Turno.estado == "EN_ESPERA", Turno.fecha == hoy())
        .order_by(Turno.hora_creacion, Turno.id_turno)  # RN-02: el más antiguo primero
        .limit(1)
        .with_for_update()
    )
    if siguiente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No hay clientes en espera")
    siguiente.estado = "LLAMADO"
    siguiente.hora_llamado = ahora()
    siguiente.hora_anuncio = datetime.now()
    siguiente.id_ventanilla = v.id_ventanilla
    siguiente.id_usuario = usuario.id_usuario
    db.commit()
    db.refresh(siguiente)
    return siguiente


def volver_a_llamar(db: Session, usuario: Usuario, id_turno: int) -> Turno:
    turno = _turno_propio_abierto(db, usuario, id_turno)
    turno.hora_anuncio = datetime.now()
    db.commit()
    return turno


def cerrar_turno(db: Session, usuario: Usuario, id_turno: int, estado: str) -> Turno:
    """RF-06 y cancelación por el administrador (RN-05)."""
    if estado == "CANCELADO":
        if usuario.rol != "ADMIN":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el administrador puede cancelar turnos")
        turno = db.get(Turno, id_turno)
        if turno is None or turno.estado != "EN_ESPERA":
            raise HTTPException(status.HTTP_409_CONFLICT, "Solo se pueden cancelar turnos en espera")
    else:
        turno = _turno_propio_abierto(db, usuario, id_turno)
    turno.estado = estado
    turno.hora_fin = ahora()
    db.commit()
    db.refresh(turno)
    return turno


def _turno_propio_abierto(db: Session, usuario: Usuario, id_turno: int) -> Turno:
    turno = db.get(Turno, id_turno)
    if turno is None or turno.estado != "LLAMADO" or turno.id_ventanilla != usuario.id_ventanilla:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese turno no está abierto en su ventanilla")
    return turno
