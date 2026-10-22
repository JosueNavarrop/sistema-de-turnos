import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./turnofacil.db")
JWT_SECRET = os.getenv("JWT_SECRET", "turnofacil-clave-de-desarrollo-cambiar-en-produccion")
JWT_HORAS = int(os.getenv("JWT_HORAS", "10"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
MINUTOS_POR_PERSONA = int(os.getenv("MINUTOS_POR_PERSONA", "3"))
