from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Table, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

ROLES = ("ADMIN", "RECEPCIONISTA")
ESTADOS = ("EN_ESPERA", "LLAMADO", "ATENDIDO", "NO_PRESENTADO", "CANCELADO")

ventanilla_servicio = Table(
    "ventanilla_servicio",
    Base.metadata,
    Column("id_ventanilla", ForeignKey("ventanillas.id_ventanilla"), primary_key=True),
    Column("id_servicio", ForeignKey("servicios.id_servicio"), primary_key=True),
)


class Ventanilla(Base):
    __tablename__ = "ventanillas"

    id_ventanilla: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    servicios: Mapped[list["Servicio"]] = relationship(secondary=ventanilla_servicio, order_by="Servicio.prefijo")
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="ventanilla")


class Servicio(Base):
    __tablename__ = "servicios"

    id_servicio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(80))
    prefijo: Mapped[str] = mapped_column(String(1), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    usuario: Mapped[str] = mapped_column(String(50), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(Enum(*ROLES, name="rol"))
    id_ventanilla: Mapped[int | None] = mapped_column(ForeignKey("ventanillas.id_ventanilla"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    ventanilla: Mapped[Ventanilla | None] = relationship(back_populates="usuarios")


class Turno(Base):
    __tablename__ = "turnos"
    __table_args__ = (
        UniqueConstraint("id_servicio", "fecha", "numero", name="uq_turno_dia"),  # RN-01
        Index("idx_cola", "estado", "id_servicio", "hora_creacion"),                # RN-02
    )

    id_turno: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_servicio: Mapped[int] = mapped_column(ForeignKey("servicios.id_servicio"))
    numero: Mapped[int] = mapped_column(Integer)
    codigo: Mapped[str] = mapped_column(String(10))
    fecha: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="estado"), default="EN_ESPERA")
    hora_creacion: Mapped[datetime] = mapped_column(DateTime)
    hora_llamado: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # último anuncio en pantalla; con microsegundos para ordenar anuncios del mismo segundo
    hora_anuncio: Mapped[datetime | None] = mapped_column(
        DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True)
    hora_fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    id_ventanilla: Mapped[int | None] = mapped_column(ForeignKey("ventanillas.id_ventanilla"), nullable=True)
    id_usuario: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=True)

    servicio: Mapped[Servicio] = relationship()
    ventanilla: Mapped[Ventanilla | None] = relationship()
    usuario: Mapped[Usuario | None] = relationship()
