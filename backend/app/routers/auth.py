from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginIn, usuario_out
from ..security import crear_token, get_usuario, verificar_contrasena
from ..turnos import ahora

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login")
def login(datos: LoginIn, db: Session = Depends(get_db)):
    """RF-01 · CU-01."""
    usuario = db.scalar(select(Usuario).where(Usuario.usuario == datos.usuario.strip()))
    if usuario is None or not verificar_contrasena(datos.contrasena, usuario.contrasena_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña inválidos")
    if not usuario.activo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario deshabilitado, contacte al administrador")
    usuario.ultimo_acceso = ahora()
    db.commit()
    return {"access_token": crear_token(usuario), "token_type": "bearer", "usuario": usuario_out(usuario)}


@router.get("/me")
def yo(usuario: Usuario = Depends(get_usuario)):
    return usuario_out(usuario)
