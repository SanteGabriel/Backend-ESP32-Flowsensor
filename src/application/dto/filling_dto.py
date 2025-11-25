from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StartFillingDTO:
    """DTO para iniciar un llenado"""

    device_id: str
    target_volume: float
    initial_volume: float


@dataclass
class CompleteFillingDTO:
    """DTO para completar un llenado"""

    filling_id: int
    final_volume: float


@dataclass
class FillingResponseDTO:
    """DTO de respuesta de llenado"""

    id: int
    device_id: str
    start_time: datetime
    end_time: Optional[datetime]
    initial_volume: float
    final_volume: Optional[float]
    target_volume: float
    status: str
    duration_seconds: Optional[float]
    avg_flow_rate: Optional[float]
    actual_volume: float
    efficiency: float

    @staticmethod
    def from_entity(entity):
        """Crea un DTO desde la entidad"""
        return FillingResponseDTO(
            id=entity.id,
            device_id=entity.device_id,
            start_time=entity.start_time,
            end_time=entity.end_time,
            initial_volume=entity.initial_volume,
            final_volume=entity.final_volume,
            target_volume=entity.target_volume,
            status=entity.status.value,
            duration_seconds=entity.duration_seconds,
            avg_flow_rate=entity.avg_flow_rate,
            actual_volume=entity.get_actual_volume(),
            efficiency=entity.get_efficiency(),
        )
