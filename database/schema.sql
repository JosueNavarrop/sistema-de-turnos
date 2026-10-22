-- TurnoFácil · Script de base de datos (MySQL 8)
-- El backend crea estas tablas solo al iniciar; este script sirve para crearlas a mano o revisarlas.

SET NAMES utf8mb4;  -- sin esto, los acentos (Créditos) se guardan mal al cargar el script

CREATE DATABASE IF NOT EXISTS turnofacil
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE turnofacil;

CREATE TABLE ventanillas (
  id_ventanilla INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(30) NOT NULL,
  activo        BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE servicios (
  id_servicio INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(80) NOT NULL,
  prefijo     CHAR(1) NOT NULL UNIQUE,
  descripcion VARCHAR(200),
  activo      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE usuarios (
  id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(100) NOT NULL,
  usuario         VARCHAR(50)  NOT NULL UNIQUE,
  contrasena_hash VARCHAR(255) NOT NULL,
  rol             ENUM('ADMIN','RECEPCIONISTA') NOT NULL,
  id_ventanilla   INT NULL,
  activo          BOOLEAN NOT NULL DEFAULT TRUE,
  ultimo_acceso   DATETIME NULL,
  FOREIGN KEY (id_ventanilla) REFERENCES ventanillas(id_ventanilla)
);

CREATE TABLE ventanilla_servicio (
  id_ventanilla INT NOT NULL,
  id_servicio   INT NOT NULL,
  PRIMARY KEY (id_ventanilla, id_servicio),
  FOREIGN KEY (id_ventanilla) REFERENCES ventanillas(id_ventanilla),
  FOREIGN KEY (id_servicio)   REFERENCES servicios(id_servicio)
);

CREATE TABLE turnos (
  id_turno      INT AUTO_INCREMENT PRIMARY KEY,
  id_servicio   INT NOT NULL,
  numero        INT NOT NULL,
  codigo        VARCHAR(10) NOT NULL,
  fecha         DATE NOT NULL,
  estado        ENUM('EN_ESPERA','LLAMADO','ATENDIDO','NO_PRESENTADO','CANCELADO')
                NOT NULL DEFAULT 'EN_ESPERA',
  hora_creacion DATETIME NOT NULL,
  hora_llamado  DATETIME NULL,
  hora_anuncio  DATETIME(6) NULL,   -- último anuncio en la pantalla pública (llamado o volver a llamar)
  hora_fin      DATETIME NULL,
  id_ventanilla INT NULL,
  id_usuario    INT NULL,
  UNIQUE KEY uq_turno_dia (id_servicio, fecha, numero),      -- RN-01
  INDEX idx_cola (estado, id_servicio, hora_creacion),        -- RN-02
  FOREIGN KEY (id_servicio)   REFERENCES servicios(id_servicio),
  FOREIGN KEY (id_ventanilla) REFERENCES ventanillas(id_ventanilla),
  FOREIGN KEY (id_usuario)    REFERENCES usuarios(id_usuario)
);

-- Datos de ejemplo (los usuarios los crea el backend con contraseñas cifradas: python -m app.seed)
INSERT INTO servicios (nombre, prefijo, descripcion, activo) VALUES
 ('Caja', 'C', 'Pagos y depósitos', TRUE),
 ('Servicio al cliente', 'S', 'Consultas y reclamaciones', TRUE),
 ('Créditos', 'R', 'Solicitudes de préstamo', TRUE),
 ('Reclamos', 'Q', 'Quejas formales', FALSE);

INSERT INTO ventanillas (nombre, activo) VALUES
 ('Ventanilla 1', TRUE), ('Ventanilla 2', TRUE), ('Ventanilla 3', FALSE);

INSERT INTO ventanilla_servicio VALUES (1, 1), (2, 2), (2, 3), (3, 1), (3, 3);
