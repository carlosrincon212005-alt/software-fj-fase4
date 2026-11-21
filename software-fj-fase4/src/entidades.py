"""Módulo de entidades base y clase Cliente con encapsulación y validaciones para Software FJ."""

from abc import ABC, abstractmethod
import re

from src.excepciones import ErrorValidacionCliente


class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema de Software FJ."""

    def __init__(self, identificador: str) -> None:
        # Valida que toda entidad tenga un identificador no vacío
        if not isinstance(identificador, str) or not identificador.strip():
            raise ValueError("El identificador de la entidad es obligatorio.")
        self._identificador = identificador.strip()

    @property
    def identificador(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._identificador

    @abstractmethod
    def resumen(self) -> str:
        """Método abstracto que obliga a las subclases a definir su representación resumida."""


class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con encapsulación de datos y validaciones estrictas."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str) -> None:
        # Inicializa el identificador heredado de EntidadSistema encadenando errores si aplica
        try:
            super().__init__(identificador)
        except ValueError as exc:
            raise ErrorValidacionCliente(
                "Identificador de cliente inválido.", detalles={"identificador": identificador}
            ) from exc

        # Usa propiedades/setters para aplicar validaciones estrictas desde la creación
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        """Obtiene el nombre completo encapsulado del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Valida y asigna el nombre del cliente."""
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorValidacionCliente(
                "El nombre del cliente debe tener al menos 3 caracteres.",
                detalles={"nombre": valor},
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        """Obtiene el correo electrónico encapsulado del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Valida formato básico de correo electrónico y asigna el valor."""
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise ErrorValidacionCliente(
                "El correo electrónico del cliente no tiene un formato válido.",
                detalles={"correo": valor},
            )
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        """Obtiene el teléfono encapsulado del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Valida que el teléfono contenga entre 7 y 15 dígitos."""
        limpio = valor.strip() if isinstance(valor, str) else ""
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            raise ErrorValidacionCliente(
                "El teléfono del cliente debe contener entre 7 y 15 dígitos numéricos.",
                detalles={"telefono": valor},
            )
        self._telefono = limpio

    def resumen(self) -> str:
        """Implementa el método abstracto devolviendo un resumen seguro del cliente."""
        return f"Cliente [{self._identificador}] - {self._nombre} ({self._correo})"
