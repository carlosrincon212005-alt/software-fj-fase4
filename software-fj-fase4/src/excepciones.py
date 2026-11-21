"""Módulo de excepciones personalizadas para el sistema de Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema de gestion de Software FJ."""

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL", detalles: dict | None = None) -> None:
        # Inicializa la excepcion base con un mensaje legible
        super().__init__(mensaje)
        # Almacena un código interno para identificar el tipo de error
        self.codigo = codigo
        # Guarda información adicional útil para diagnóstico y registro de logs
        self.detalles = detalles or {}


class ErrorValidacionCliente(ErrorSoftwareFJ):
    """Error lanzado cuando los datos de un cliente no cumplen las validaciones."""

    def __init__(self, mensaje: str, detalles: dict | None = None) -> None:
        # Delega en la clase base asignando un código específico de cliente
        super().__init__(mensaje, codigo="ERR_CLIENTE", detalles=detalles)


class ErrorServicioNoDisponible(ErrorSoftwareFJ):
    """Error lanzado cuando un servicio no existe, no está disponible o tiene parámetros inválidos."""

    def __init__(self, mensaje: str, detalles: dict | None = None) -> None:
        # Delega en la clase base asignando un código específico de servicio
        super().__init__(mensaje, codigo="ERR_SERVICIO", detalles=detalles)


class ErrorReservaInvalida(ErrorSoftwareFJ):
    """Error lanzado ante intentos de reserva incorrectos o transiciones de estado no permitidas."""

    def __init__(self, mensaje: str, detalles: dict | None = None) -> None:
        # Delega en la clase base asignando un código específico de reserva
        super().__init__(mensaje, codigo="ERR_RESERVA", detalles=detalles)


class ErrorCalculoCosto(ErrorSoftwareFJ):
    """Error lanzado cuando ocurre un cálculo inconsistente o inválido en tarifas o costos."""

    def __init__(self, mensaje: str, detalles: dict | None = None) -> None:
        # Delega en la clase base asignando un código específico de cálculo
        super().__init__(mensaje, codigo="ERR_CALCULO_COSTO", detalles=detalles)