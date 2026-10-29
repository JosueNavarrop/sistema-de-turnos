# Casos de prueba · TurnoFácil

**Grupo 2 · Ingeniería de Software II · UNICARIBE**

Los 15 casos están automatizados en [`backend/tests/test_casos_de_prueba.py`](../backend/tests/test_casos_de_prueba.py) y se ejecutan con `pytest` sobre una base SQLite en memoria con los datos iniciales. Cada prueba se llama igual que su caso (`test_cp01_…`).

**Resultado de la última ejecución (22/10/2026): 15 de 15 aprobados.**

```
cd backend && pytest -v
```

| ID | Caso de uso | Caso de prueba | Datos de entrada | Resultado esperado | Estado |
|---|---|---|---|---|---|
| CP-01 | CU-01 | Inicio de sesión correcto | `admin` / `admin123` | 200, devuelve token y rol `ADMIN` | ✅ Aprobado |
| CP-02 | CU-01 | Contraseña incorrecta | `admin` / `mala` | 401, «Usuario o contraseña inválidos» | ✅ Aprobado |
| CP-03 | CU-01, CU-08 | Usuario deshabilitado no entra | Desactivar a `lgomez` e iniciar sesión | 403 | ✅ Aprobado |
| CP-04 | CU-03 | El kiosco solo muestra servicios activos | `GET /api/servicios?activos=true` | Solo C, S, R; «Reclamos» (inactivo) no aparece (RN-04) | ✅ Aprobado |
| CP-05 | CU-03 | Turnos consecutivos por servicio | Generar C, C, S | C-001, C-002, S-001; C-002 con 1 persona delante y 3 min estimados | ✅ Aprobado |
| CP-06 | CU-03 | La numeración reinicia al día siguiente | Generar 2 turnos de Caja, cambiar la fecha al día siguiente y generar otro | El nuevo turno es C-001 (RN-01) | ✅ Aprobado |
| CP-07 | CU-03 | No se genera turno de un servicio inactivo | Turno de «Reclamos» | 404 | ✅ Aprobado |
| CP-08 | CU-05 | Llama al turno más antiguo de los servicios de su ventanilla | Turnos C, R, S; Ventanilla 2 llama | Llama R-001 (Caja no es de su ventanilla) (RN-02) | ✅ Aprobado |
| CP-09 | CU-05 | No puede llamar con un turno abierto | Llamar dos veces seguidas | El segundo llamado da 409 (RN-03) | ✅ Aprobado |
| CP-10 | CU-05 | Sin clientes en espera | Llamar con la cola vacía | 404, «No hay clientes en espera» | ✅ Aprobado |
| CP-11 | CU-06 | Marcar atendido libera la ventanilla | Llamar C-001, marcar atendido y llamar otra vez | C-001 `ATENDIDO` con hora de fin; se llama C-002; contador de atendidos = 1 | ✅ Aprobado |
| CP-12 | CU-06 | No se presentó y volver a llamar | Volver a llamar C-001, luego «No se presentó» | C-001 vuelve a ser el turno actual en pantalla; queda `NO_PRESENTADO`; no puede cerrar turnos de otra ventanilla (409) | ✅ Aprobado |
| CP-13 | CU-04 | Pantalla pública: actual y anteriores | Sin llamados; luego llamar C-001 y S-001 | Vacía al inicio; después S-001 actual en Ventanilla 2 y C-001 en anteriores | ✅ Aprobado |
| CP-14 | CU-02, CU-08 | Administración valida permisos y duplicados | Crear servicio sin sesión, como recepcionista y con prefijo «C»; crear usuario repetido; crear ventanilla y usuario nuevos | 401, 403, 409 («ya lo usa Caja»), 409; el usuario nuevo llama turnos en su ventanilla | ✅ Aprobado |
| CP-15 | CU-07 | Consulta con filtros y totales; cancelación | Filtrar por estado y servicio; cancelar como recepcionista y como admin | Filtros y totales correctos; el recepcionista recibe 403; el admin cancela (RN-05) | ✅ Aprobado |

## Pruebas manuales de interfaz

Complementan las automáticas y se ejecutaron en Chrome contra el sistema levantado con Docker.

| ID | Pantalla | Pasos | Resultado esperado | Estado |
|---|---|---|---|---|
| PM-01 | Kiosco | Tocar «Caja» | Ticket con código, personas delante y espera; vuelve a la lista a los 5 s | ✅ |
| PM-02 | Login | Contraseña incorrecta | Mensaje rojo «Usuario o contraseña inválidos» | ✅ |
| PM-03 | Recepción | Llamar siguiente con un turno abierto | El botón está desactivado y explica por qué | ✅ |
| PM-04 | Pantalla pública | Llamar un turno y «Volver a llamar» desde recepción, con la pantalla abierta | Aparece en 3 s o menos y parpadea; suena si se pulsó «Activar sonido» | ✅ Aparición y parpadeo · sonido: verificar en la TV |
| PM-05 | Administración | Nuevo servicio con prefijo «C» | Error «El prefijo «C» ya lo usa «Caja»» dentro del formulario | ✅ |
| PM-06 | Rutas | Entrar a `/admin` como recepcionista | Redirige a `/recepcion` | ✅ |
| PM-07 | Kiosco | Sacar un turno y esperar 7 s | El ticket desaparece y vuelve la lista de servicios | ✅ |
| PM-08 | Administración | Activar «Reclamos» con ⏻ y abrir el kiosco; luego desactivarlo | Aparece en el kiosco y desaparece al desactivarlo | ✅ |
| PM-09 | Administración | Editar la Ventanilla 3 y marcarla activa | Queda «Activo» en la tabla | ✅ |
| PM-10 | Administración | Nuevo usuario con usuario repetido «aperez»; luego con uno nuevo | Error «El usuario «aperez» ya existe»; después se crea y aparece en la tabla | ✅ |
| PM-11 | Recepción | Entrar con el usuario recién creado y llamar siguiente | Llama un turno de los servicios de su ventanilla | ✅ |
| PM-12 | Recepción | «No se presentó» | El turno se cierra y suma a «No presentados» | ✅ |
| PM-13 | Sesión | Cerrar sesión y abrir `/admin` | Lleva a `/login?volver=/admin`; al entrar como admin vuelve a `/admin` | ✅ |
| PM-14 | Consultar turnos | Cancelar un turno en espera con ✕; filtrar por estado, servicio y una fecha sin turnos | Pide confirmación y lo marca «Cancelado»; filtros correctos; «Sin turnos para ese filtro» | ✅ |
| PM-15 | Todas | Ver en tablet (768 px) y celular (375 px) | Sin desbordes horizontales ni textos cortados | ✅ Tras corregir la pantalla pública y los filtros |
