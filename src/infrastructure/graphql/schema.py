import strawberry
from typing import List, Optional
from datetime import datetime


@strawberry.type
class FlowReading:
    """Tipo GraphQL para lectura de flujo"""

    id: int
    device_id: str
    flow_rate: float
    total_volume: float
    timestamp: datetime
    pulse_count: Optional[int] = None
    unit: Optional[str] = None
    temperature: Optional[float] = None
    pressure: Optional[float] = None


@strawberry.type
class Filling:
    """Tipo GraphQL para llenado"""

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


@strawberry.type
class Pump:
    """Tipo GraphQL para bomba"""

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


@strawberry.type
class FlowMetricsType:
    """Tipo GraphQL para métricas de flujo"""

    avg_flow_rate: float
    min_flow_rate: float
    max_flow_rate: float
    total_volume: float
    efficiency: float
    period_start: datetime
    period_end: datetime


@strawberry.type
class FillingMetricsType:
    """Tipo GraphQL para métricas de llenados"""

    total_fillings: int
    completed_fillings: int
    cancelled_fillings: int
    avg_duration_seconds: float
    avg_volume: float
    avg_efficiency: float
    total_volume_dispensed: float
    completion_rate: float
    period_start: datetime
    period_end: datetime


@strawberry.type
class BusinessMetricsType:
    """Tipo GraphQL para métricas de negocio"""

    revenue: float
    peak_hours: List[int]
    avg_fillings_per_day: float
    water_efficiency: float


@strawberry.input
class CreateFlowReadingInput:
    """Input para crear lectura de flujo"""

    device_id: str
    flow_rate: float
    total_volume: Optional[float] = None  # Ahora es opcional
    pulse_count: Optional[int] = None  # Contador de pulsos del sensor
    unit: Optional[str] = None  # Unidad de medida (ej: "L/min")
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    timestamp: Optional[str] = None  # Timestamp ISO 8601 del dispositivo


@strawberry.input
class StartFillingInput:
    """Input para iniciar llenado"""

    device_id: str
    target_volume: float
    initial_volume: float


@strawberry.input
class CompleteFillingInput:
    """Input para completar llenado"""

    filling_id: int
    final_volume: float


@strawberry.input
class UpdatePumpLevelInput:
    """Input para actualizar nivel de bomba"""

    device_id: str
    current_level: float


@strawberry.input
class PumpControlInput:
    """Input para controlar bomba"""

    device_id: str
    action: str  # "on" o "off"


@strawberry.type
class ThresholdStatus:
    """Estado de umbrales de la bomba"""

    should_stop: bool
    should_warn: bool
    current_level: float
    threshold_stop: float
    threshold_warning: float
    level_percentage: float
