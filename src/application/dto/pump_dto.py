from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UpdatePumpLevelDTO:
    """DTO para actualizar el nivel de la bomba"""

    device_id: str
    current_level: float


@dataclass
class PumpControlDTO:
    """DTO para controlar la bomba"""

    device_id: str
    action: str  # "on" o "off"


@dataclass
class PumpResponseDTO:
    """DTO de respuesta de bomba"""

    id: str
    device_id: str
    status: str
    current_level: float
    max_level: float
    threshold_stop: float
    threshold_warning: float
    last_updated: datetime
    level_percentage: float
    should_stop: bool
    should_warn: bool

    @staticmethod
    def from_entity(entity):
        """Crea un DTO desde la entidad"""
        return PumpResponseDTO(
            id=entity.id,
            device_id=entity.device_id,
            status=entity.status.value,
            current_level=entity.current_level,
            max_level=entity.max_level,
            threshold_stop=entity.threshold_stop,
            threshold_warning=entity.threshold_warning,
            last_updated=entity.last_updated,
            level_percentage=entity.get_level_percentage(),
            should_stop=entity.should_stop(),
            should_warn=entity.should_warn(),
        )
