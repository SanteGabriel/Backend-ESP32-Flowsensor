from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class PumpStatus(Enum):
    """Estado de la bomba"""
    ON = "on"
    OFF = "off"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class Pump:
    """Entidad que representa la bomba de agua"""

    id: str
    device_id: str
    status: PumpStatus
    current_level: float  # nivel actual en litros o porcentaje
    max_level: float  # nivel máximo
    threshold_stop: float  # umbral para detener (litros o porcentaje)
    threshold_warning: float  # umbral de advertencia
    last_updated: datetime
    total_runtime_hours: float = 0.0

    def should_stop(self) -> bool:
        """Verifica si la bomba debe detenerse"""
        return self.current_level >= self.threshold_stop

    def should_warn(self) -> bool:
        """Verifica si se debe enviar una advertencia"""
        return self.current_level >= self.threshold_warning

    def update_level(self, new_level: float):
        """Actualiza el nivel actual"""
        if new_level < 0:
            raise ValueError("El nivel no puede ser negativo")
        if new_level > self.max_level:
            new_level = self.max_level
        self.current_level = new_level
        self.last_updated = datetime.now()

    def turn_on(self):
        """Enciende la bomba"""
        if self.should_stop():
            raise ValueError("No se puede encender la bomba: nivel máximo alcanzado")
        self.status = PumpStatus.ON
        self.last_updated = datetime.now()

    def turn_off(self):
        """Apaga la bomba"""
        self.status = PumpStatus.OFF
        self.last_updated = datetime.now()

    def get_level_percentage(self) -> float:
        """Obtiene el nivel como porcentaje"""
        if self.max_level == 0:
            return 0.0
        return (self.current_level / self.max_level) * 100
