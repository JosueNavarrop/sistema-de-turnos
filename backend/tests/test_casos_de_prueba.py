"""Casos de prueba CP-01 a CP-15 (ver docs/casos-de-prueba.md)."""
from datetime import timedelta

from app import turnos as reglas

from .conftest import generar, id_servicio, token


# ---------- CU-01 Iniciar sesión ----------

def test_cp01_login_correcto_devuelve_token_y_rol(client):
    r = client.post("/api/auth/login", json={"usuario": "admin", "contrasena": "admin123"})
    assert r.status_code == 200
    assert r.json()["access_token"]
    assert r.json()["usuario"]["rol"] == "ADMIN"


def test_cp02_login_con_contrasena_incorrecta(client):
    r = client.post("/api/auth/login", json={"usuario": "admin", "contrasena": "mala"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Usuario o contraseña inválidos"


def test_cp03_usuario_deshabilitado_no_entra(client, admin):
    luis = next(u for u in client.get("/api/usuarios", headers=admin).json() if u["usuario"] == "lgomez")
    datos = {k: luis[k] for k in ("nombre", "usuario", "rol", "id_ventanilla")} | {"activo": False}
    assert client.put(f"/api/usuarios/{luis['id_usuario']}", json=datos, headers=admin).status_code == 200
    r = client.post("/api/auth/login", json={"usuario": "lgomez", "contrasena": "recep123"})
    assert r.status_code == 403


# ---------- CU-03 Generar turno ----------

def test_cp04_kiosco_solo_muestra_servicios_activos(client):
    prefijos = [s["prefijo"] for s in client.get("/api/servicios?activos=true").json()]
    assert prefijos == ["C", "S", "R"]  # «Reclamos» (Q) está inactivo · RN-04


def test_cp05_turnos_consecutivos_por_servicio(client):
    t1, t2, s1 = generar(client, "C"), generar(client, "C"), generar(client, "S")
    assert (t1["codigo"], t2["codigo"], s1["codigo"]) == ("C-001", "C-002", "S-001")
    assert t2["delante"] == 1 and t2["estado"] == "EN_ESPERA"
    assert t2["espera_estimada_min"] == 3


def test_cp06_numeracion_reinicia_al_dia_siguiente(client, monkeypatch):
    generar(client, "C")
    generar(client, "C")
    manana = reglas.hoy() + timedelta(days=1)
    monkeypatch.setattr(reglas, "hoy", lambda: manana)
    assert generar(client, "C")["codigo"] == "C-001"  # RN-01


def test_cp07_no_se_genera_turno_de_servicio_inactivo(client):
    r = client.post("/api/turnos", json={"id_servicio": id_servicio(client, "Q")})
    assert r.status_code == 404


# ---------- CU-05 Llamar siguiente ----------

def test_cp08_llama_al_mas_antiguo_de_los_servicios_de_su_ventanilla(client, luis):
    generar(client, "C")                     # Caja no la atiende la Ventanilla 2
    primero = generar(client, "R")
    generar(client, "S")
    r = client.post("/api/turnos/siguiente", headers=luis)
    assert r.status_code == 200
    assert r.json()["codigo"] == primero["codigo"]  # RN-02
    assert r.json()["estado"] == "LLAMADO" and r.json()["ventanilla"] == "Ventanilla 2"


def test_cp09_no_puede_llamar_con_un_turno_abierto(client, ana):
    generar(client, "C")
    generar(client, "C")
    assert client.post("/api/turnos/siguiente", headers=ana).status_code == 200
    r = client.post("/api/turnos/siguiente", headers=ana)
    assert r.status_code == 409  # RN-03


def test_cp10_sin_clientes_en_espera(client, ana):
    r = client.post("/api/turnos/siguiente", headers=ana)
    assert r.status_code == 404
    assert r.json()["detail"] == "No hay clientes en espera"


# ---------- CU-06 Marcar atendido ----------

def test_cp11_marcar_atendido_libera_la_ventanilla(client, ana):
    generar(client, "C")
    generar(client, "C")
    t = client.post("/api/turnos/siguiente", headers=ana).json()
    r = client.put(f"/api/turnos/{t['id_turno']}/estado", json={"estado": "ATENDIDO"}, headers=ana)
    assert r.status_code == 200 and r.json()["estado"] == "ATENDIDO" and r.json()["hora_fin"]
    assert client.post("/api/turnos/siguiente", headers=ana).json()["codigo"] == "C-002"
    panel = client.get("/api/turnos/mi-ventanilla", headers=ana).json()
    assert panel["atendidos"] == 1 and panel["abierto"]["codigo"] == "C-002"


def test_cp12_no_se_presento_y_volver_a_llamar(client, ana, luis):
    generar(client, "C")
    generar(client, "S")
    c = client.post("/api/turnos/siguiente", headers=ana).json()
    client.post("/api/turnos/siguiente", headers=luis)                       # S-001 queda como actual
    assert client.post(f"/api/turnos/{c['id_turno']}/rellamar", headers=ana).status_code == 200
    assert client.get("/api/turnos/actual").json()["actual"]["codigo"] == "C-001"
    r = client.put(f"/api/turnos/{c['id_turno']}/estado", json={"estado": "NO_PRESENTADO"}, headers=ana)
    assert r.json()["estado"] == "NO_PRESENTADO"
    # un recepcionista no puede cerrar el turno de otra ventanilla
    otro = client.get("/api/turnos/mi-ventanilla", headers=luis).json()["abierto"]
    assert client.put(f"/api/turnos/{otro['id_turno']}/estado", json={"estado": "ATENDIDO"},
                      headers=ana).status_code == 409


# ---------- CU-04 Ver turno actual ----------

def test_cp13_pantalla_publica_muestra_actual_y_anteriores(client, ana, luis):
    vacia = client.get("/api/turnos/actual").json()
    assert vacia["actual"] is None and vacia["ultimos"] == []
    generar(client, "C")
    generar(client, "S")
    client.post("/api/turnos/siguiente", headers=ana)
    client.post("/api/turnos/siguiente", headers=luis)
    pantalla = client.get("/api/turnos/actual").json()
    assert pantalla["actual"]["codigo"] == "S-001" and pantalla["actual"]["ventanilla"] == "Ventanilla 2"
    assert [t["codigo"] for t in pantalla["ultimos"]] == ["C-001"]


# ---------- CU-02 y CU-08 Administración ----------

def test_cp14_administracion_valida_permisos_y_duplicados(client, admin, ana):
    nuevo = {"nombre": "Reclamos 2", "prefijo": "C", "descripcion": "", "activo": True}
    assert client.post("/api/servicios", json=nuevo).status_code == 401           # sin sesión
    assert client.post("/api/servicios", json=nuevo, headers=ana).status_code == 403  # recepcionista
    r = client.post("/api/servicios", json=nuevo, headers=admin)
    assert r.status_code == 409 and "Caja" in r.json()["detail"]                   # prefijo duplicado
    assert client.post("/api/servicios", json=nuevo | {"prefijo": "x"}, headers=admin).json()["prefijo"] == "X"
    usuario = {"nombre": "Carlos Méndez", "usuario": "aperez", "contrasena": "clave123", "rol": "RECEPCIONISTA"}
    assert client.post("/api/usuarios", json=usuario, headers=admin).status_code == 409
    v = client.post("/api/ventanillas", json={"nombre": "Ventanilla 4", "servicios": [id_servicio(client, "C")]},
                    headers=admin).json()
    creado = client.post("/api/usuarios", json=usuario | {"usuario": "cmendez", "id_ventanilla": v["id_ventanilla"]},
                         headers=admin)
    assert creado.status_code == 201
    cm = token(client, "cmendez", "clave123")
    generar(client, "C")
    assert client.post("/api/turnos/siguiente", headers=cm).json()["ventanilla"] == "Ventanilla 4"


# ---------- CU-07 Consultar turnos ----------

def test_cp15_consulta_con_filtros_y_totales(client, admin, ana):
    generar(client, "C")
    generar(client, "C")
    generar(client, "S")
    t = client.post("/api/turnos/siguiente", headers=ana).json()
    client.put(f"/api/turnos/{t['id_turno']}/estado", json={"estado": "ATENDIDO"}, headers=ana)
    s = client.get("/api/turnos?estado=EN_ESPERA", headers=admin).json()
    assert {x["codigo"] for x in s["turnos"]} == {"C-002", "S-001"}
    assert s["totales"]["total"] == 3 and s["totales"]["atendido"] == 1 and s["totales"]["en_espera"] == 2
    caja = client.get(f"/api/turnos?servicio={id_servicio(client, 'C')}", headers=admin).json()
    assert caja["totales"]["total"] == 2
    # el administrador puede cancelar un turno en espera; el recepcionista no
    s001 = next(x for x in s["turnos"] if x["codigo"] == "S-001")
    assert client.put(f"/api/turnos/{s001['id_turno']}/estado", json={"estado": "CANCELADO"},
                      headers=ana).status_code == 403
    assert client.put(f"/api/turnos/{s001['id_turno']}/estado", json={"estado": "CANCELADO"},
                      headers=admin).json()["estado"] == "CANCELADO"
    assert client.get("/api/turnos", headers=admin).json()["totales"]["cancelado"] == 1
