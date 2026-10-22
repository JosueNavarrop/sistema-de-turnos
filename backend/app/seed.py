"""Crea las tablas y carga los datos iniciales si la base está vacía.

Uso:  python -m app.seed            (desde la carpeta backend)
      python -m app.seed --reiniciar  (borra todo y vuelve a cargar)
"""
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Servicio, Usuario, Ventanilla
from .security import hash_contrasena

# Credenciales de prueba. Cambiarlas en producción desde Administración → Usuarios.
USUARIOS_INICIALES = [
    ("Administrador", "admin", "admin123", "ADMIN", None),
    ("Ana Pérez", "aperez", "recep123", "RECEPCIONISTA", "Ventanilla 1"),
    ("Luis Gómez", "lgomez", "recep123", "RECEPCIONISTA", "Ventanilla 2"),
]


def cargar(db: Session) -> bool:
    """Carga solo lo que falte: servicios y ventanillas si no hay ninguno, y usuarios si no hay ninguno."""
    if db.scalar(select(Usuario).limit(1)):
        return False
    if not db.scalar(select(Servicio).limit(1)):
        caja = Servicio(nombre="Caja", prefijo="C", descripcion="Pagos y depósitos")
        cliente = Servicio(nombre="Servicio al cliente", prefijo="S", descripcion="Consultas y reclamaciones")
        creditos = Servicio(nombre="Créditos", prefijo="R", descripcion="Solicitudes de préstamo")
        reclamos = Servicio(nombre="Reclamos", prefijo="Q", descripcion="Quejas formales", activo=False)
        db.add_all([caja, cliente, creditos, reclamos])
        if not db.scalar(select(Ventanilla).limit(1)):
            db.add_all([Ventanilla(nombre="Ventanilla 1", servicios=[caja]),
                        Ventanilla(nombre="Ventanilla 2", servicios=[cliente, creditos]),
                        Ventanilla(nombre="Ventanilla 3", servicios=[caja, creditos], activo=False)])
        db.flush()
    por_nombre = {v.nombre: v for v in db.scalars(select(Ventanilla))}
    for nombre, usuario, clave, rol, ventanilla in USUARIOS_INICIALES:
        db.add(Usuario(nombre=nombre, usuario=usuario, contrasena_hash=hash_contrasena(clave), rol=rol,
                       ventanilla=por_nombre.get(ventanilla)))
    db.commit()
    return True


def main():
    if "--reiniciar" in sys.argv:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        print("Datos iniciales cargados." if cargar(db) else "La base ya tenía datos; no se cargó nada.")


if __name__ == "__main__":
    main()
