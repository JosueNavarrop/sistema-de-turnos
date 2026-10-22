from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import JWT_HORAS, JWT_SECRET
from .database import get_db
from .models import Usuario

bearer = HTTPBearer(auto_error=False)


def hash_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


def verificar_contrasena(contrasena: str, hash_: str) -> bool:
    try:
        return bcrypt.checkpw(contrasena.encode(), hash_.encode())
    except ValueError:
        return False


def crear_token(usuario: Usuario) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_HORAS)
    return jwt.encode({"sub": str(usuario.id_usuario), "rol": usuario.rol, "exp": exp}, JWT_SECRET, algorithm="HS256")


def get_usuario(cred: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Usuario:
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Debe iniciar sesión")
    try:
        datos = jwt.decode(cred.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión inválida o vencida")
    usuario = db.get(Usuario, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario deshabilitado")
    return usuario


def requiere_rol(*roles: str):
    def dependencia(usuario: Usuario = Depends(get_usuario)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tiene permiso para esta acción")
        return usuario

    return dependencia
