from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateFlowReadingDTO:
    """DTO para crear una lectura de flujo"""

    device_id: str
    flow_rate: float
    total_volume: Optional[float] = None  # Ahora es opcional, se puede calcular
    pulse_count: Optional[int] = None  # Contador de pulsos del sensor
    unit: Optional[str] = None  # Unidad de medida (ej: "L/min")
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    timestamp: Optional[str] = None  # Timestamp ISO 8601 del dispositivo


@dataclass
class FlowReadingResponseDTO:
    """DTO de respuesta de lectura de flujo"""

    id: int
    device_id: str
    flow_rate: float
    total_volume: float
    timestamp: datetime
    pulse_count: Optional[int] = None
    unit: Optional[str] = None
    temperature: Optional[float] = None
    pressure: Optional[float] = None

    @staticmethod
    def from_entity(entity):
        """Crea un DTO desde la entidad"""
        return FlowReadingResponseDTO(
            id=entity.id,
            device_id=entity.device_id,
            flow_rate=entity.flow_rate,
            total_volume=entity.total_volume,
            timestamp=entity.timestamp,
            pulse_count=entity.pulse_count,
            unit=entity.unit,
            temperature=entity.temperature,
            pressure=entity.pressure,
        )
