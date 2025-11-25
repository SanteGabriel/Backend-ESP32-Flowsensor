from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FlowReading:
    """Entidad que representa una lectura del flujómetro"""

    id: Optional[int]
    device_id: str
    flow_rate: float  # litros por minuto
    total_volume: float  # litros totales
    timestamp: datetime
    pulse_count: Optional[int] = None  # contador de pulsos del sensor
    unit: Optional[str] = None  # unidad de medida (ej: "L/min")
    temperature: Optional[float] = None  # temperatura del agua en °C
    pressure: Optional[float] = None  # presión en PSI

    def __post_init__(self):
        if self.flow_rate < 0:
            raise ValueError("El flujo no puede ser negativo")
        if self.total_volume < 0:
            raise ValueError("El volumen total no puede ser negativo")
        if self.pulse_count is not None and self.pulse_count < 0:
            raise ValueError("El contador de pulsos no puede ser negativo")

    def is_anomaly(self, threshold: float = 100.0) -> bool:
        """Detecta si la lectura es anómala basándose en el flujo"""
        return self.flow_rate > threshold or self.flow_rate < 0
