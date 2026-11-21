"""Módulo de servicios abstractos y especializados para Software FJ."""

from abc import ABC, abstractmethod

from src.excepciones import ErrorCalculoCosto, ErrorServicioNoDisponible


class Servicio(ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        # Asigna el código y valida parámetros usando el método abstracto sobrescrito
        self.codigo = codigo
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible
        self.validar_parametros()

    @abstractmethod
    def validar_parametros(self) -> None:
        """Valida los parámetros específicos del servicio; lanza ErrorServicioNoDisponible si fallan."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción detallada del servicio (polimorfismo)."""

    @abstractmethod
    def calcular_costo_base(self, unidades: int) -> float:
        """Calcula el costo base del servicio según la cantidad de unidades/horas/días."""

    def calcular_costo(
        self,
        unidades: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Método sobrecargado (vía parámetros opcionales) para calcular el costo final.

        Permite invocar con 1 argumento (solo unidades) o con descuento e impuesto opcionales.
        """
        # Verifica que el servicio esté disponible antes de cotizar
        if not self.disponible:
            raise ErrorServicioNoDisponible(
                f"El servicio '{self.nombre}' no está disponible actualmente.",
                detalles={"codigo": self.codigo},
            )
        # Valida rangos de descuento e impuesto para evitar cálculos inconsistentes
        if not (0.0 <= descuento_pct < 100.0):
            raise ErrorCalculoCosto(
                "El porcentaje de descuento debe estar entre 0 y menor a 100.",
                detalles={"descuento_pct": descuento_pct, "servicio": self.codigo},
            )
        if impuesto_pct < 0.0:
            raise ErrorCalculoCosto(
                "El porcentaje de impuesto no puede ser negativo.",
                detalles={"impuesto_pct": impuesto_pct, "servicio": self.codigo},
            )

        try:
            # Calcula el subtotal aplicando polimórficamente el costo base de cada servicio
            subtotal = self.calcular_costo_base(unidades)
            con_descuento = subtotal * (1.0 - descuento_pct / 100.0)
            total = con_descuento * (1.0 + impuesto_pct / 100.0)
        except ErrorCalculoCosto:
            raise
        except Exception as exc:
            # Encadena cualquier error inesperado durante el cálculo
            raise ErrorCalculoCosto(
                f"Error al calcular el costo del servicio '{self.codigo}'.",
                detalles={"unidades": unidades, "descuento_pct": descuento_pct, "impuesto_pct": impuesto_pct},
            ) from exc

        if total < 0:
            raise ErrorCalculoCosto(
                "El costo final calculado no puede ser negativo.",
                detalles={"total": total, "servicio": self.codigo},
            )
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio especializado para la reserva de salas de reuniones o capacitación."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True) -> None:
        # Guarda la capacidad de personas antes de validar parámetros
        self.capacidad = capacidad
        super().__init__(codigo=codigo, nombre=nombre, tarifa_base=tarifa_base, disponible=disponible)

    def validar_parametros(self) -> None:
        """Valida tarifa base por hora y capacidad mínima de la sala."""
        if not self.codigo or not self.codigo.strip():
            raise ErrorServicioNoDisponible("El código de la sala es obligatorio.")
        if self.tarifa_base <= 0:
            raise ErrorServicioNoDisponible("La tarifa por hora de la sala debe ser mayor que cero.")
        if not isinstance(self.capacidad, int) or self.capacidad <= 0:
            raise ErrorServicioNoDisponible("La capacidad de la sala debe ser un entero positivo.")

    def describir(self) -> str:
        """Describe la sala y su capacidad."""
        estado = "Disponible" if self.disponible else "No disponible"
        return f"[Sala] {self.nombre} ({self.codigo}) - Capacidad: {self.capacidad} personas - {estado}"

    def calcular_costo_base(self, unidades: int) -> float:
        """Calcula el costo según cantidad de horas reservadas."""
        if not isinstance(unidades, int) or unidades <= 0:
            raise ErrorCalculoCosto("Las horas de reserva de sala deben ser un entero positivo.")
        return self.tarifa_base * unidades


class AlquilerEquipo(Servicio):
    """Servicio especializado para el alquiler de equipos tecnológicos."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, categoria_equipo: str, disponible: bool = True) -> None:
        # Guarda la categoría del equipo antes de validar parámetros
        self.categoria_equipo = categoria_equipo
        super().__init__(codigo=codigo, nombre=nombre, tarifa_base=tarifa_base, disponible=disponible)

    def validar_parametros(self) -> None:
        """Valida tarifa base por día y categoría del equipo."""
        if not self.codigo or not self.codigo.strip():
            raise ErrorServicioNoDisponible("El código del equipo es obligatorio.")
        if self.tarifa_base <= 0:
            raise ErrorServicioNoDisponible("La tarifa diaria del equipo debe ser mayor que cero.")
        if not self.categoria_equipo or not self.categoria_equipo.strip():
            raise ErrorServicioNoDisponible("La categoría del equipo es obligatoria.")

    def describir(self) -> str:
        """Describe el equipo, su categoría y disponibilidad."""
        estado = "Disponible" if self.disponible else "No disponible"
        return f"[Equipo] {self.nombre} ({self.codigo}) - Categoría: {self.categoria_equipo} - {estado}"

    def calcular_costo_base(self, unidades: int) -> float:
        """Calcula el costo según cantidad de días de alquiler."""
        if not isinstance(unidades, int) or unidades <= 0:
            raise ErrorCalculoCosto("Los días de alquiler de equipo deben ser un entero positivo.")
        return self.tarifa_base * unidades


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de consultoría o asesoría técnica de Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True) -> None:
        # Guarda el área de especialidad antes de validar parámetros
        self.especialidad = especialidad
        super().__init__(codigo=codigo, nombre=nombre, tarifa_base=tarifa_base, disponible=disponible)

    def validar_parametros(self) -> None:
        """Valida tarifa base por sesión y especialidad técnica."""
        if not self.codigo or not self.codigo.strip():
            raise ErrorServicioNoDisponible("El código de la asesoría es obligatorio.")
        if self.tarifa_base <= 0:
            raise ErrorServicioNoDisponible("La tarifa por sesión de asesoría debe ser mayor que cero.")
        if not self.especialidad or not self.especialidad.strip():
            raise ErrorServicioNoDisponible("La especialidad de la asesoría es obligatoria.")

    def describir(self) -> str:
        """Describe la asesoría especializada y su enfoque."""
        estado = "Disponible" if self.disponible else "No disponible"
        return f"[Asesoría] {self.nombre} ({self.codigo}) - Especialidad: {self.especialidad} - {estado}"

    def calcular_costo_base(self, unidades: int) -> float:
        """Calcula el costo según cantidad de sesiones de asesoría."""
        if not isinstance(unidades, int) or unidades <= 0:
            raise ErrorCalculoCosto("El número de sesiones de asesoría debe ser un entero positivo.")
        return self.tarifa_base * unidades
    