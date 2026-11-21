"""Punto de entrada y simulación de al menos 10 operaciones para Software FJ (sin base de datos)."""

import sys
from pathlib import Path

# Asegura que la carpeta raíz del proyecto esté en sys.path al ejecutar `python main.py`
RAIZ_PROYECTO = Path(__file__).resolve().parent
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from src.excepciones import ErrorCalculoCosto, ErrorReservaInvalida, ErrorServicioNoDisponible
from src.registrador_logs import RegistradorLogs
from src.reservas import GestorSoftwareFJ
from src.servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def ejecutar_simulacion() -> None:
    """Ejecuta 12 operaciones completas (válidas e inválidas) manteniendo el sistema activo."""
    # Inicializa el registrador de logs (único archivo persistente permitido; sin base de datos)
    registrador = RegistradorLogs(ruta_archivo=str(RAIZ_PROYECTO / "logs" / "sistema_software_fj.log"))
    gestor = GestorSoftwareFJ(registrador=registrador)
    registrador.registrar_evento("INFO", "=== Inicio de simulación Software FJ (Fase 4) ===")

    # --- BLOQUE 1: REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS) ---
    # Operación 1: Cliente válido
    gestor.registrar_cliente("CLI-01", "Laura Gómez", "laura.gomez@correo.com", "3001234567")
    # Operación 2: Cliente válido
    gestor.registrar_cliente("CLI-02", "Carlos Rincón", "carlos.rincon@correo.com", "3109876543")
    # Operación 3: Cliente inválido (correo sin formato válido y teléfono corto)
    gestor.registrar_cliente("CLI-03", "Ana", "correo_invalido", "123")

    # --- BLOQUE 2: CREACIÓN DE SERVICIOS (CORRECTA E INCORRECTA) ---
    # Operación 4: Servicio válido - Reserva de sala
    gestor.registrar_servicio(
        ReservaSala("SAL-101", "Sala Ejecutiva Norte", tarifa_base=80000.0, capacidad=12, disponible=True)
    )
    # Operación 5: Servicio válido - Alquiler de equipo
    gestor.registrar_servicio(
        AlquilerEquipo("EQP-202", "Laptop Workstation i7", tarifa_base=45000.0, categoria_equipo="Cómputo", disponible=True)
    )
    # Operación 6: Servicio válido - Asesoría especializada
    gestor.registrar_servicio(
        AsesoriaEspecializada(
            "ASE-303", "Arquitectura de Software", tarifa_base=120000.0, especialidad="POO y Excepciones", disponible=True
        )
    )
    # Operación 7: Servicio inválido (tarifa base negativa -> capturado sin detener el sistema)
    try:
        sala_invalida = ReservaSala("SAL-ERR", "Sala Inválida", tarifa_base=-15000.0, capacidad=5, disponible=True)
        gestor.registrar_servicio(sala_invalida)
    except ErrorServicioNoDisponible as exc:
        registrador.registrar_excepcion(exc, contexto="simulacion_servicio_invalido")

    # --- BLOQUE 3: RESERVAS (EXITOSAS, CANCELADA Y FALLIDAS) ---
    # Operación 8: Reserva exitosa de sala con descuento e impuesto opcionales (sobrecarga)
    gestor.crear_y_procesar_reserva(
        codigo_reserva="RES-001",
        id_cliente="CLI-01",
        codigo_servicio="SAL-101",
        duracion=3,
        descuento_pct=10.0,
        impuesto_pct=19.0,
    )
    # Operación 9: Reserva exitosa de alquiler de equipo
    gestor.crear_y_procesar_reserva(
        codigo_reserva="RES-002",
        id_cliente="CLI-02",
        codigo_servicio="EQP-202",
        duracion=2,
        descuento_pct=5.0,
        impuesto_pct=19.0,
    )
    # Operación 10: Reserva válida cancelada antes de procesarse
    gestor.crear_y_procesar_reserva(
        codigo_reserva="RES-003",
        id_cliente="CLI-01",
        codigo_servicio="ASE-303",
        duracion=1,
        cancelar_en_vez_de_procesar=True,
    )
    # Operación 11: Reserva fallida por cliente inexistente (encadena excepciones y sigue el sistema)
    gestor.crear_y_procesar_reserva(
        codigo_reserva="RES-004",
        id_cliente="CLI-999",
        codigo_servicio="SAL-101",
        duracion=2,
    )
    # Operación 12: Reserva fallida por duración inválida (0 horas -> ErrorReservaInvalida)
    gestor.crear_y_procesar_reserva(
        codigo_reserva="RES-005",
        id_cliente="CLI-02",
        codigo_servicio="EQP-202",
        duracion=0,
    )

    # Demostración adicional de encadenamiento explícito en cálculo de costo inválido
    try:
        servicio_asesoria = next((s for s in gestor.servicios if s.codigo == "ASE-303"), None)
        if servicio_asesoria is not None:
            servicio_asesoria.calcular_costo(unidades=2, descuento_pct=150.0)
    except ErrorCalculoCosto as exc:
        error_enc = ErrorReservaInvalida("Fallo de cotización en prueba final.")
        error_enc.__cause__ = exc
        registrador.registrar_excepcion(error_enc, contexto="prueba_sobrecarga_costo")

    registrador.registrar_evento(
        "INFO",
        f"Resumen en memoria -> Clientes: {len(gestor.clientes)} | Servicios: {len(gestor.servicios)} | Reservas: {len(gestor.reservas)}",
    )
    print("Simulación finalizada sin interrupciones.")
    print(f"Clientes registrados en memoria: {len(gestor.clientes)}")
    print(f"Servicios registrados en memoria: {len(gestor.servicios)}")
    print(f"Reservas almacenadas en memoria: {len(gestor.reservas)}")


if __name__ == "__main__":
    ejecutar_simulacion()