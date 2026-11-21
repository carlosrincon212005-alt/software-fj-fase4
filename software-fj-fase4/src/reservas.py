"""Módulo de gestión de reservas y gestor en memoria para Software FJ."""

from src.entidades import Cliente
from src.excepciones import (
    ErrorCalculoCosto,
    ErrorReservaInvalida,
    ErrorServicioNoDisponible,
    ErrorValidacionCliente,
)
from src.registrador_logs import RegistradorLogs
from src.servicios import Servicio


class Reserva:
    """Integra cliente, servicio, duración y estado con confirmación, cancelación y procesamiento."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA")

    def __init__(
        self,
        codigo_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        # Valida que el código de reserva no esté vacío
        if not isinstance(codigo_reserva, str) or not codigo_reserva.strip():
            raise ErrorReservaInvalida("El código de la reserva es obligatorio.")
        # Valida que se reciba una instancia válida de Cliente
        if not isinstance(cliente, Cliente):
            raise ErrorReservaInvalida("La reserva requiere un objeto Cliente válido.")
        # Valida que se reciba una instancia válida de Servicio
        if not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida("La reserva requiere un objeto Servicio válido.")
        # Valida que el servicio esté disponible al crear la reserva
        if not servicio.disponible:
            raise ErrorServicioNoDisponible(
                f"No se puede reservar el servicio '{servicio.nombre}' porque no está disponible.",
                detalles={"codigo_reserva": codigo_reserva, "servicio": servicio.codigo},
            )
        # Valida que la duración sea un entero positivo
        if not isinstance(duracion, int) or duracion <= 0:
            raise ErrorReservaInvalida(
                "La duración de la reserva debe ser un número entero positivo.",
                detalles={"duracion": duracion, "codigo_reserva": codigo_reserva},
            )

        self.codigo_reserva = codigo_reserva.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.descuento_pct = descuento_pct
        self.impuesto_pct = impuesto_pct
        self.estado = "PENDIENTE"

        # Calcula el costo inicial usando el método con parámetros opcionales (sobrecarga)
        self.costo_total = self.servicio.calcular_costo(
            self.duracion,
            descuento_pct=self.descuento_pct,
            impuesto_pct=self.impuesto_pct,
        )

    def confirmar(self) -> None:
        """Confirma la reserva si su estado actual lo permite."""
        if self.estado == "CANCELADA":
            raise ErrorReservaInvalida(
                f"No se puede confirmar la reserva '{self.codigo_reserva}' porque está cancelada."
            )
        if self.estado == "PROCESADA":
            raise ErrorReservaInvalida(
                f"La reserva '{self.codigo_reserva}' ya fue procesada."
            )
        self.estado = "CONFIRMADA"

    def cancelar(self) -> None:
        """Cancela la reserva si aún no ha sido procesada."""
        if self.estado == "PROCESADA":
            raise ErrorReservaInvalida(
                f"No se puede cancelar la reserva '{self.codigo_reserva}' porque ya está procesada."
            )
        self.estado = "CANCELADA"

    def procesar(self) -> float:
        """Procesa la reserva confirmada, recalcula y retorna el costo final."""
        if self.estado != "CONFIRMADA":
            raise ErrorReservaInvalida(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual de '{self.codigo_reserva}': {self.estado}."
            )
        try:
            # Recalcula el costo aplicando descuento e impuesto opcionales
            costo_final = self.servicio.calcular_costo(
                self.duracion,
                descuento_pct=self.descuento_pct,
                impuesto_pct=self.impuesto_pct,
            )
        except ErrorCalculoCosto as exc:
            # Encadena la excepción de cálculo dentro de una excepción de reserva
            raise ErrorReservaInvalida(
                f"Error al procesar el costo de la reserva '{self.codigo_reserva}'.",
                detalles={"codigo_reserva": self.codigo_reserva},
            ) from exc

        self.costo_total = costo_final
        self.estado = "PROCESADA"
        return self.costo_total


class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas en memoria mediante listas (sin base de datos)."""

    def __init__(self, registrador: RegistradorLogs) -> None:
        self.registrador = registrador
        # Listas en memoria para gestionar entidades sin usar ningún motor de base de datos
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, identificador: str, nombre: str, correo: str, telefono: str) -> Cliente | None:
        """Intenta crear y registrar un cliente con try/except/else/finally y registro en log."""
        cliente_creado: Cliente | None = None
        try:
            cliente_creado = Cliente(identificador, nombre, correo, telefono)
            if any(c.identificador == cliente_creado.identificador for c in self.clientes):
                raise ErrorValidacionCliente(
                    f"Ya existe un cliente registrado con ID '{cliente_creado.identificador}'."
                )
        except ErrorValidacionCliente as exc:
            self.registrador.registrar_excepcion(exc, contexto="registrar_cliente")
            return None
        else:
            # Se ejecuta solo si no hubo excepción
            self.clientes.append(cliente_creado)
            self.registrador.registrar_evento(
                "INFO", f"Cliente registrado correctamente: {cliente_creado.resumen()}"
            )
            return cliente_creado
        finally:
            # Bloque finally de control de operación
            self.registrador.registrar_evento(
                "DEBUG", f"Intento de registro de cliente finalizado (ID={identificador})."
            )

    def registrar_servicio(self, servicio: Servicio) -> Servicio | None:
        """Registra un objeto Servicio en la lista en memoria con manejo de excepciones."""
        try:
            if not isinstance(servicio, Servicio):
                raise ErrorServicioNoDisponible("El objeto proporcionado no es un Servicio válido.")
            servicio.validar_parametros()
            if any(s.codigo == servicio.codigo for s in self.servicios):
                raise ErrorServicioNoDisponible(
                    f"Ya existe un servicio registrado con el código '{servicio.codigo}'."
                )
        except ErrorServicioNoDisponible as exc:
            self.registrador.registrar_excepcion(exc, contexto="registrar_servicio")
            return None
        else:
            self.servicios.append(servicio)
            self.registrador.registrar_evento(
                "INFO", f"Servicio registrado correctamente: {servicio.describir()}"
            )
            return servicio
        finally:
            self.registrador.registrar_evento("DEBUG", "Operación registrar_servicio evaluada.")

    def crear_y_procesar_reserva(
        self,
        codigo_reserva: str,
        id_cliente: str,
        codigo_servicio: str,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        cancelar_en_vez_de_procesar: bool = False,
    ) -> Reserva | None:
        """Crea, confirma y procesa (o cancela) una reserva encadenando excepciones si fallan búsquedas."""
        try:
            cliente = next((c for c in self.clientes if c.identificador == id_cliente), None)
            if cliente is None:
                raise ErrorValidacionCliente(f"No se encontró el cliente con ID '{id_cliente}'.")

            servicio = next((s for s in self.servicios if s.codigo == codigo_servicio), None)
            if servicio is None:
                raise ErrorServicioNoDisponible(f"No se encontró el servicio con código '{codigo_servicio}'.")

            reserva = Reserva(
                codigo_reserva=codigo_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )

            if cancelar_en_vez_de_procesar:
                reserva.cancelar()
                self.reservas.append(reserva)
                self.registrador.registrar_evento(
                    "INFO", f"Reserva '{reserva.codigo_reserva}' cancelada correctamente."
                )
                return reserva

            reserva.confirmar()
            total = reserva.procesar()
            self.reservas.append(reserva)
            self.registrador.registrar_evento(
                "INFO",
                f"Reserva '{reserva.codigo_reserva}' procesada exitosamente por ${total:.2f} para {cliente.nombre}.",
            )
            return reserva

        except (ErrorValidacionCliente, ErrorServicioNoDisponible, ErrorCalculoCosto) as exc:
            # Encadena excepciones de dominio dentro de ErrorReservaInvalida
            error_encadenado = ErrorReservaInvalida(
                f"Fallo en la operación de reserva '{codigo_reserva}': {exc}",
                detalles={"codigo_reserva": codigo_reserva, "id_cliente": id_cliente, "codigo_servicio": codigo_servicio},
            )
            error_encadenado.__cause__ = exc
            self.registrador.registrar_excepcion(error_encadenado, contexto="crear_y_procesar_reserva")
            return None
        except ErrorReservaInvalida as exc:
            self.registrador.registrar_excepcion(exc, contexto="crear_y_procesar_reserva")
            return None
        finally:
            self.registrador.registrar_evento(
                "DEBUG", f"Ciclo de reserva '{codigo_reserva}' concluido sin detener el sistema."
            )