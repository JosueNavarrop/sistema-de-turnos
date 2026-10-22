import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import cargar


@pytest.fixture
def client():
    """API con una base SQLite en memoria y los datos iniciales cargados."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Sesion = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with Sesion() as db:
        cargar(db)

    def db_de_prueba():
        db = Sesion()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_de_prueba
    yield TestClient(app)  # sin "with": no ejecuta el lifespan que usa la base real
    app.dependency_overrides.clear()


def token(client, usuario, contrasena):
    r = client.post("/api/auth/login", json={"usuario": usuario, "contrasena": contrasena})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin(client):
    return token(client, "admin", "admin123")


@pytest.fixture
def ana(client):
    """Recepcionista de la Ventanilla 1 (atiende Caja)."""
    return token(client, "aperez", "recep123")


@pytest.fixture
def luis(client):
    """Recepcionista de la Ventanilla 2 (atiende Servicio al cliente y Créditos)."""
    return token(client, "lgomez", "recep123")


def id_servicio(client, prefijo):
    return next(s["id_servicio"] for s in client.get("/api/servicios").json() if s["prefijo"] == prefijo)


def generar(client, prefijo):
    r = client.post("/api/turnos", json={"id_servicio": id_servicio(client, prefijo)})
    assert r.status_code == 201, r.text
    return r.json()
