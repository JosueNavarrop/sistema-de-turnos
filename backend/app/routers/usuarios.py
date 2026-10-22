from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario, Ventanilla
from ..schemas import UsuarioIn, usuario_out
from ..security import hash_contrasena, requiere_rol

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"], dependencies=[Depends(requiere_rol("ADMIN"))])


@router.get("")
def listar(db: Session = Depends(get_db)):
    return [usuario_out(u) for u in db.scalars(select(Usuario).order_by(Usuario.id_usuario))]


def _validar(db: Session, datos: UsuarioIn, id_actual: int | None = None):
    otro = db.scalar(select(Usuario).where(Usuario.usuario == datos.usuario))
    if otro and otro.id_usuario != id_actual:
        raise HTTPException(status.HTTP_409_CONFLICT, f"El usuario «{datos.usuario}» ya existe")
    if datos.id_ventanilla is not None and db.get(Ventanilla, datos.id_ventanilla) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La ventanilla no existe")


@router.post("", status_code=201)
def crear(datos: UsuarioIn, db: Session = Depends(get_db)):
    """RF-08 · CU-08."""
    if not datos.contrasena:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La contraseña es obligatoria (mínimo 6 caracteres)")
    _validar(db, datos)
    usuario = Usuario(nombre=datos.nombre.strip(), usuario=datos.usuario, rol=datos.rol, activo=datos.activo,
                      contrasena_hash=hash_contrasena(datos.contrasena),
                      id_ventanilla=datos.id_ventanilla if datos.rol == "RECEPCIONISTA" else None)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario_out(usuario)


@router.put("/{id_usuario}")
def editar(id_usuario: int, datos: UsuarioIn, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    _validar(db, datos, id_usuario)
    usuario.nombre = datos.nombre.strip()
    usuario.usuario = datos.usuario
    usuario.rol = datos.rol
    usuario.activo = datos.activo
    usuario.id_ventanilla = datos.id_ventanilla if datos.rol == "RECEPCIONISTA" else None
    if datos.contrasena:
        usuario.contrasena_hash = hash_contrasena(datos.contrasena)
    db.commit()
    db.refresh(usuario)
    return usuario_out(usuario)
