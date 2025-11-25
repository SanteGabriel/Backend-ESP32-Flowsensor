from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class FillingStatus(Enum):
    """Estado del llenado"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class Filling:
    """Entidad que representa un ciclo de llenado de agua"""

    id: Optional[int]
    device_id: str
    start_time: datetime
    end_time: Optional[datetime]
    initial_volume: float
    final_volume: Optional[float]
    target_volume: float
    status: FillingStatus
    duration_seconds: Optional[float] = None
    avg_flow_rate: Optional[float] = None

    def complete(self, end_time: datetime, final_volume: float):
        """Marca el llenado como completado"""
        self.end_time = end_time
        self.final_volume = final_volume
        self.status = FillingStatus.COMPLETED
        self.duration_seconds = (end_time - self.start_time).total_seconds()
        if self.duration_seconds > 0:
            self.avg_flow_rate = (final_volume - self.initial_volume) / (
                self.duration_seconds / 60
            )

    def cancel(self, end_time: datetime, final_volume: float):
        """Cancela el llenado"""
        self.end_time = end_time
        self.final_volume = final_volume
        self.status = FillingStatus.CANCELLED

    def get_actual_volume(self) -> float:
        """Obtiene el volumen real llenado"""
        if self.final_volume is None:
            return 0.0
        return self.final_volume - self.initial_volume

    def get_efficiency(self) -> float:
        """Calcula la eficiencia del llenado (0-100%)"""
        if self.final_volume is None:
            return 0.0
        actual = self.get_actual_volume()
        if self.target_volume == 0:
            return 0.0
        return min((actual / self.target_volume) * 100, 100.0)
