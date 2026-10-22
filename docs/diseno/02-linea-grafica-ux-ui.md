# 02 · Línea gráfica UX/UI — "TurnoFácil"

**Grupo 2 · Ingeniería de Software II · UNICARIBE · Entrega 1 (08/10/2026)**

## 1. Principios de experiencia

| Principio | Qué significa en el sistema |
|---|---|
| **Claridad a distancia** | El número de turno es el elemento más grande de cada pantalla pública; se lee a 5 m. |
| **Mínimos toques** | El cliente saca su turno en 1 toque (+ confirmación automática). |
| **Una acción principal por pantalla** | En el panel del recepcionista domina el botón *Llamar siguiente*. |
| **Estado siempre visible** | Cada turno muestra su estado con color + texto (nunca solo color). |
| **Prevención de errores** | Botones deshabilitados cuando la acción no aplica (ej. RN-03: no llamar si hay turno abierto). |

## 2. Identidad

- **Nombre:** TurnoFácil
- **Tono:** cercano, directo, en segunda persona de cortesía ("Seleccione su servicio", "Su turno es…").
- **Logo (propuesta):** ícono de ticket con el texto "TurnoFácil" en Poppins SemiBold.

## 3. Paleta de colores

| Rol | Nombre | HEX | Uso |
|---|---|---|---|
| Primario | Azul confianza | `#1E5EFF` | Botones principales, encabezados, enlaces |
| Primario oscuro | Azul noche | `#0B2A6F` | Fondo de la pantalla pública, barra superior |
| Acento | Turquesa | `#14B8A6` | Turno actual resaltado, confirmaciones |
| Fondo | Gris nube | `#F5F7FB` | Fondo de pantallas internas |
| Superficie | Blanco | `#FFFFFF` | Tarjetas, tablas, formularios |
| Texto | Grafito | `#1F2937` | Texto principal |
| Texto secundario | Gris | `#6B7280` | Etiquetas, ayudas |
| Borde | Gris claro | `#E5E7EB` | Bordes de tarjetas y tablas |

**Colores de estado del turno**

| Estado | Color | HEX | Etiqueta |
|---|---|---|---|
| EN_ESPERA | Ámbar | `#F59E0B` | En espera |
| LLAMADO | Azul | `#1E5EFF` | Llamado |
| ATENDIDO | Verde | `#16A34A` | Atendido |
| NO_PRESENTADO | Rojo | `#DC2626` | No se presentó |
| CANCELADO | Gris | `#6B7280` | Cancelado |

> Todas las combinaciones texto/fondo cumplen contraste ≥ 4.5:1 (WCAG AA).

## 4. Tipografía

| Uso | Fuente | Peso | Tamaño |
|---|---|---|---|
| Número de turno (pantalla pública) | Poppins | 700 | 160 px |
| Número de turno (kiosco/panel) | Poppins | 700 | 64 px |
| Títulos (H1) | Poppins | 600 | 28 px |
| Subtítulos (H2) | Poppins | 600 | 20 px |
| Texto / tablas | Inter | 400 | 16 px |
| Etiquetas / ayudas | Inter | 500 | 13 px |

Fuentes gratuitas de Google Fonts.

## 5. Espaciado, forma e íconos

- **Grilla:** múltiplos de 8 px (8, 16, 24, 32).
- **Bordes redondeados:** 12 px en tarjetas y botones; 999 px en etiquetas de estado.
- **Sombras:** una sola, suave: `0 2px 8px rgba(0,0,0,.08)`.
- **Íconos:** Material Symbols (Outlined) — `confirmation_number`, `campaign`, `check_circle`, `person_off`, `settings`, `search`.

## 6. Componentes

| Componente | Especificación |
|---|---|
| **Botón primario** | Fondo `#1E5EFF`, texto blanco, alto 48 px (64 px en kiosco), radio 12 px. Hover: 10 % más oscuro. Deshabilitado: 40 % opacidad. |
| **Botón secundario** | Borde 1.5 px `#1E5EFF`, fondo blanco, texto azul. |
| **Botón de servicio (kiosco)** | Tarjeta 240×160 px, letra del prefijo en 48 px, nombre debajo en 20 px. |
| **Etiqueta de estado** | Píldora con fondo del color de estado al 12 % y texto del color pleno. |
| **Tarjeta** | Fondo blanco, radio 12 px, padding 24 px, sombra suave. |
| **Tabla** | Encabezado gris nube, filas de 48 px, separador `#E5E7EB`. |
| **Campo de texto** | Alto 44 px, borde `#E5E7EB`, foco con borde `#1E5EFF` de 2 px. |
| **Mensaje** | Éxito turquesa, error rojo; ícono + texto, se cierra a los 4 s. |

## 7. Pantallas (wireframes)

### Mapa de navegación

```
 KIOSCO (público)        PANTALLA PÚBLICA (TV)
   [P1 Generar turno]      [P2 Turno actual]

 PERSONAL
   [P3 Login]
      ├── Recepcionista ──► [P4 Panel de atención] ──► [P6 Consultar turnos]
      └── Administrador ──► Menú admin
                              ├── [P5 Servicios / Ventanillas / Usuarios]
                              └── [P6 Consultar turnos]
```

### P1 · Kiosco "Generar turno" (tablet vertical/horizontal)

```
┌──────────────────────────────────────────┐
│            Bienvenido · TurnoFácil       │
│        Seleccione el servicio:           │
│  ┌────────────┐ ┌────────────┐           │
│  │     C      │ │     S      │           │
│  │   Caja     │ │ Servicio al│           │
│  │            │ │  cliente   │           │
│  └────────────┘ └────────────┘           │
│  ┌────────────┐                          │
│  │     R      │                          │
│  │  Créditos  │                          │
│  └────────────┘                          │
└──────────────────────────────────────────┘
   → Confirmación (5 s):  "Su turno es  C-015
                           Personas delante: 4"
```

### P2 · Pantalla pública "Turno actual" (TV 16:9, fondo azul noche)

```
┌──────────────────────────────────────────┐
│   TURNO ACTUAL            │  ÚLTIMOS     │
│                           │  S-008  V2   │
│      C - 015              │  C-014  V1   │
│    ► VENTANILLA 1         │  R-003  V3   │
│                           │  C-013  V1   │
└──────────────────────────────────────────┘
```
Al llamar un turno: el número parpadea 3 veces en turquesa y suena un tono corto.

### P3 · Login

```
┌─────────────────────────────┐
│       TurnoFácil · Acceso   │
│  Usuario:    [___________]  │
│  Contraseña: [___________]  │
│          [ Entrar ]         │
└─────────────────────────────┘
```

### P4 · Panel del recepcionista

```
┌──────────────────────────────────────────┐
│ Ventanilla 1 · Ana Pérez       [Salir]   │
├──────────────────────────────────────────┤
│  Atendiendo:   C-015   (Caja)            │
│  Llamado a las 10:42                     │
│  [ ATENDIDO ] [ NO SE PRESENTÓ ]         │
│  [ VOLVER A LLAMAR ]                     │
│                                          │
│  En espera: Caja 6 · Créditos 2          │
│  [  ► LLAMAR SIGUIENTE  ]  (deshabilitado│
│                       si hay turno abierto)
└──────────────────────────────────────────┘
```

### P5 · Administración (pestañas Servicios / Ventanillas / Usuarios)

```
┌──────────────────────────────────────────┐
│ Servicios | Ventanillas | Usuarios       │
├──────────────────────────────────────────┤
│ [+ Nuevo servicio]                       │
│ Prefijo │ Nombre             │ Estado │  │
│   C     │ Caja               │ Activo │✎ │
│   S     │ Servicio al cliente│ Activo │✎ │
│   R     │ Créditos           │Inactivo│✎ │
└──────────────────────────────────────────┘
```

### P6 · Consultar turnos

```
┌──────────────────────────────────────────┐
│ Fecha [08/10/2026] Servicio [Todos ▼]    │
│ Estado [Todos ▼]            [Buscar]     │
├──────────────────────────────────────────┤
│ Turno│Servicio│Llegada│Llamado│Estado│Vent│
│ C-015│ Caja   │10:30  │10:42  │Atend.│ V1 │
│ C-016│ Caja   │10:33  │  —    │Espera│ —  │
├──────────────────────────────────────────┤
│ Total 48 · Atendidos 41 · No pres. 3     │
│ Espera promedio: 9 min                   │
└──────────────────────────────────────────┘
```

## 8. Responsive

| Dispositivo | Pantallas | Ajuste |
|---|---|---|
| TV / monitor ≥ 1280 px | P2 | Pantalla completa, sin interacción |
| Tablet 768–1279 px | P1, P4 | Botones grandes (≥ 64 px de alto) |
| Escritorio ≥ 1024 px | P3, P5, P6 | Contenido centrado, máx. 1200 px de ancho |
