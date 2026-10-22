from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS
from .database import Base, SessionLocal, engine
from .routers import auth, servicios, turnos, usuarios, ventanillas
from .seed import cargar

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        cargar(db)
    yield


app = FastAPI(title="TurnoFácil API", version="1.0.0", lifespan=lifespan,
              description="Sistema de turnos · Grupo 2 · Ingeniería de Software II · UNICARIBE")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])

for r in (auth, servicios, ventanillas, usuarios, turnos):
    app.include_router(r.router)


@app.get("/api/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}


# En la versión liberable, FastAPI también sirve el frontend compilado (frontend/dist).
if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def spa(ruta: str):
        if ruta.startswith("api/"):
            raise HTTPException(404, "Ruta no encontrada")
        archivo = FRONTEND / ruta
        if ruta and archivo.is_file():
            return FileResponse(archivo)
        return FileResponse(FRONTEND / "index.html")
