from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ESTADOS, Turno, Usuario
from ..schemas import EstadoIn, TurnoIn, turno_out
from ..security import get_usuario, requiere_rol
from .. import turnos as reglas

router = APIRouter(prefix="/api/turnos", tags=["Turnos"])


@router.post("", status_code=201)
def generar(datos: TurnoIn, db: Session = Depends(get_db)):
    """RF-03 · CU-03. Público: lo usa el kiosco."""
    turno, delante = reglas.generar_turno(db, datos.id_servicio)
    return turno_out(turno) | {"delante": delante, "espera_estimada_min": reglas.espera_estimada(delante)}


@router.get("/actual")
def actual(db: Session = Depends(get_db)):
    """RF-04 · CU-04. Turno actual y los 5 anteriores para la pantalla pública."""
    anunciados = list(db.scalars(
        select(Turno).where(Turno.fecha == reglas.hoy(), Turno.hora_anuncio.is_not(None))
        .order_by(Turno.hora_anuncio.desc(), Turno.id_turno.desc()).limit(6)))
    ultimo = anunciados[0] if anunciados else None
    return {
        "actual": turno_out(ultimo) if ultimo else None,
        "ultimos": [turno_out(t) for t in anunciados[1:]],
        # cambia cada vez que se anuncia un turno; la pantalla lo usa para parpadear y sonar
        "anuncio": f"{ultimo.id_turno}@{ultimo.hora_anuncio.isoformat()}" if ultimo else None,
    }


@router.get("/mi-ventanilla")
def mi_ventanilla(usuario: Usuario = Depends(requiere_rol("RECEPCIONISTA")), db: Session = Depends(get_db)):
    """Estado del panel del recepcionista (P4 / P4b)."""
    v = reglas.ventanilla_de(usuario)
    ids = [s.id_servicio for s in v.servicios]
    abierto = reglas.turno_abierto(db, v.id_ventanilla)
    mios = list(db.scalars(select(Turno).where(Turno.fecha == reglas.hoy(), Turno.id_ventanilla == v.id_ventanilla)))
    llamados = [t for t in mios if t.hora_llamado]
    cerrados = sorted((t for t in mios if t.hora_fin and t.estado in ("ATENDIDO", "NO_PRESENTADO")),
                      key=lambda t: t.hora_fin)
    return {
        "ventanilla": {"id_ventanilla": v.id_ventanilla, "nombre": v.nombre},
        "abierto": turno_out(abierto) if abierto else None,
        "cola": [{"prefijo": s.prefijo, "servicio": s.nombre, "en_espera": reglas.en_espera(db, s.id_servicio)}
                 for s in v.servicios],
        "en_espera": sum(reglas.en_espera(db, i) for i in ids),
        "atendidos": sum(t.estado == "ATENDIDO" for t in mios),
        "no_presentados": sum(t.estado == "NO_PRESENTADO" for t in mios),
        "espera_promedio_min": round(sum((t.hora_llamado - t.hora_creacion).total_seconds() for t in llamados)
                                     / len(llamados) / 60) if llamados else None,
        "ultimo": {"codigo": cerrados[-1].codigo, "hora_fin": cerrados[-1].hora_fin} if cerrados else None,
    }


@router.post("/siguiente")
def siguiente(usuario: Usuario = Depends(requiere_rol("RECEPCIONISTA")), db: Session = Depends(get_db)):
    """RF-05 · CU-05."""
    return turno_out(reglas.llamar_siguiente(db, usuario))


@router.post("/{id_turno}/rellamar")
def rellamar(id_turno: int, usuario: Usuario = Depends(requiere_rol("RECEPCIONISTA")), db: Session = Depends(get_db)):
    """CU-06, flujo alterno 2b."""
    return turno_out(reglas.volver_a_llamar(db, usuario, id_turno))


@router.put("/{id_turno}/estado")
def cambiar_estado(id_turno: int, datos: EstadoIn, usuario: Usuario = Depends(get_usuario),
                   db: Session = Depends(get_db)):
    """RF-06 · CU-06. ATENDIDO o NO_PRESENTADO (recepcionista); CANCELADO (administrador)."""
    return turno_out(reglas.cerrar_turno(db, usuario, id_turno, datos.estado))


@router.get("")
def consultar(fecha: date | None = None, servicio: int | None = None, estado: str | None = None,
              _: Usuario = Depends(get_usuario), db: Session = Depends(get_db)):
    """RF-07 · CU-07."""
    fecha = fecha or reglas.hoy()
    del_dia = list(db.scalars(select(Turno).where(Turno.fecha == fecha)
                              .order_by(Turno.hora_creacion.desc(), Turno.id_turno.desc())))
    filtrados = [t for t in del_dia
                 if (servicio is None or t.id_servicio == servicio) and (not estado or t.estado == estado)]
    base = [t for t in del_dia if servicio is None or t.id_servicio == servicio]
    llamados = [t for t in base if t.hora_llamado]
    return {
        "turnos": [turno_out(t) for t in filtrados],
        "totales": {
            "total": len(base),
            **{e.lower(): sum(t.estado == e for t in base) for e in ESTADOS},
            "espera_promedio_min": round(sum((t.hora_llamado - t.hora_creacion).total_seconds() for t in llamados)
                                         / len(llamados) / 60) if llamados else None,
        },
    }
