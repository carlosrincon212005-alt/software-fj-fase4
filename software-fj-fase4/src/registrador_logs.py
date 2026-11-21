"""Módulo de registro de eventos y errores en archivo de logs para Software FJ."""

from datetime import datetime
from pathlib import Path


class RegistradorLogs:
    """Gestiona la escritura de eventos y excepciones en un archivo de texto (sin base de datos)."""

    def __init__(self, ruta_archivo: str = "logs/sistema_software_fj.log") -> None:
        # Define la ruta del archivo de logs relativa a la carpeta raíz del proyecto
        self.ruta_archivo = Path(ruta_archivo)
        # Garantiza que la carpeta contenedora exista antes de escribir
        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

    def registrar_evento(self, nivel: str, mensaje: str, contexto: str = "") -> None:
        """Registra un evento o error con marca de tiempo en el archivo de logs."""
        # Obtiene la fecha y hora actual del sistema
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Construye la línea estructurada para facilitar la trazabilidad
        extra = f" | Contexto: {contexto}" if contexto else ""
        linea = f"[{marca_tiempo}] [{nivel.upper()}] {mensaje}{extra}\n"
        # Abre el archivo en modo anexar ('a') con codificación UTF-8 sin usar base de datos
        with self.ruta_archivo.open(mode="a", encoding="utf-8") as archivo_log:
            archivo_log.write(linea)

    def registrar_excepcion(self, exc: BaseException, contexto: str = "") -> None:
        """Registra una excepción y, si existe, su excepción encadenada (__cause__ o __context__)."""
        # Obtiene información de la excepción principal
        detalle = f"{type(exc).__name__}: {exc}"
        # Verifica si hay encadenamiento explícito (__cause__) o implícito (__context__)
        causa = exc.__cause__ or exc.__context__
        if causa is not None:
            detalle += f" <- Causado por {type(causa).__name__}: {causa}"
        # Registra el error con nivel ERROR
        self.registrar_evento(nivel="ERROR", mensaje=detalle, contexto=contexto)