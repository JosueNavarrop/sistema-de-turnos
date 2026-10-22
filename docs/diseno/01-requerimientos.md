# 01 · Requerimientos — Sistema de Turnos "TurnoFácil"

**Grupo 2 · Ingeniería de Software II · UNICARIBE · Entrega 1 (08/10/2026)**

## 1. Descripción general

TurnoFácil organiza la atención por orden de llegada en un **centro de atención al cliente** (adaptable a clínica, banco u oficina pública cambiando solo los servicios). El cliente elige un servicio y recibe un turno (ej. **C-015**); una pantalla pública muestra el turno que se está atendiendo; el recepcionista llama al siguiente y lo marca como atendido; el administrador configura servicios y consulta el historial.

**Objetivo:** eliminar filas físicas y desorden en la atención, y registrar cuántos turnos se atienden y cuánto esperan los clientes.

**Alcance:** una sucursal con varias ventanillas. **Fuera de alcance:** citas por adelantado, pagos, notificaciones por SMS/WhatsApp, múltiples sucursales.

## 2. Usuarios del sistema

| Usuario | Descripción | Requiere login |
|---|---|---|
| **Cliente** | Persona que llega a ser atendida. Saca su turno en el kiosco y mira la pantalla pública. | No |
| **Recepcionista** | Atiende en una ventanilla. Llama turnos y los marca como atendidos. | Sí |
| **Administrador** | Gestiona servicios, ventanillas y usuarios; consulta turnos y reportes. | Sí |

## 3. Requerimientos funcionales

| ID | Requerimiento | Usuario | Prioridad |
|---|---|---|---|
| RF-01 | **Iniciar sesión** con usuario y contraseña; el menú se adapta al rol. | Recepcionista, Admin | Alta |
| RF-02 | **Registrar servicios**: crear, editar y activar/desactivar servicios con nombre y prefijo (ej. Caja → "C"). | Admin | Alta |
| RF-03 | **Generar turno**: el cliente elige un servicio y el sistema asigna el siguiente consecutivo del día (C-001, C-002…). | Cliente | Alta |
| RF-04 | **Mostrar turno actual**: la pantalla pública muestra el turno llamado, su ventanilla y los últimos llamados; se actualiza sola. | Cliente | Alta |
| RF-05 | **Llamar siguiente turno**: llama el turno en espera más antiguo de los servicios de su ventanilla. | Recepcionista | Alta |
| RF-06 | **Marcar atendido**: cierra el turno como *Atendido* o *No se presentó*, guardando la hora. | Recepcionista | Alta |
| RF-07 | **Consultar turnos**: listado filtrable por fecha, servicio y estado, con totales y tiempo promedio de espera. | Admin, Recepcionista | Media |
| RF-08 | **Gestionar usuarios y ventanillas**: crear recepcionistas y asignarlos a una ventanilla con sus servicios. | Admin | Media |

## 4. Requerimientos no funcionales

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-01 | Usabilidad | Sacar un turno en el kiosco toma máximo 2 toques. |
| RNF-02 | Rendimiento | La pantalla pública refleja un llamado en ≤ 3 segundos. |
| RNF-03 | Seguridad | Contraseñas cifradas (bcrypt); cada rol solo accede a sus opciones. |
| RNF-04 | Compatibilidad | Chrome, Edge y Firefox actuales; pantallas desde 10" (tablet/kiosco) hasta TV. |
| RNF-05 | Disponibilidad | Opera en la red local de la sucursal durante el horario de atención. |
| RNF-06 | Mantenibilidad | Código separado en capas (presentación, lógica, datos). |
| RNF-07 | Accesibilidad | Contraste mínimo 4.5:1 y textos del turno legibles a 5 m en la pantalla pública. |

## 5. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | La numeración de turnos reinicia en 001 cada día y por servicio. |
| RN-02 | Los turnos se atienden en orden de llegada (FIFO) dentro de cada servicio. |
| RN-03 | Una ventanilla no puede llamar otro turno mientras tenga uno *Llamado* sin cerrar. |
| RN-04 | Un servicio desactivado no aparece en el kiosco, pero conserva su historial. |
| RN-05 | Estados del turno: `EN_ESPERA → LLAMADO → ATENDIDO \| NO_PRESENTADO`. `CANCELADO` solo lo asigna el Admin. |

## 6. Trazabilidad

| Requerimiento | Caso de uso | Pantalla |
|---|---|---|
| RF-01 | CU-01 | P3 Login |
| RF-02 | CU-02 | P5 Administración |
| RF-03 | CU-03 | P1 Kiosco |
| RF-04 | CU-04 | P2 Pantalla pública |
| RF-05 | CU-05 | P4 Panel de atención |
| RF-06 | CU-06 | P4 Panel de atención |
| RF-07 | CU-07 | P6 Consultar turnos |
| RF-08 | CU-08 | P5 Administración |

## 7. Cumplimiento de mínimos del proyecto

| Mínimo solicitado | TurnoFácil |
|---|---|
| 5–7 funcionalidades principales | 7 (+ login) |
| 4–6 pantallas | 6 |
| 3–5 tablas principales | 5 |
| 2–3 tipos de usuario | 3 |
