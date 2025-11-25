from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime


@dataclass
class FlowMetrics:
    """Métricas de flujo de agua"""

    avg_flow_rate: float
    min_flow_rate: float
    max_flow_rate: float
    total_volume: float
    efficiency: float
    period_start: datetime
    period_end: datetime

    def to_dict(self) -> Dict:
        return {
            "avg_flow_rate": round(self.avg_flow_rate, 2),
            "min_flow_rate": round(self.min_flow_rate, 2),
            "max_flow_rate": round(self.max_flow_rate, 2),
            "total_volume": round(self.total_volume, 2),
            "efficiency": round(self.efficiency, 2),
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
        }


@dataclass
class FillingMetrics:
    """Métricas de llenados"""

    total_fillings: int
    completed_fillings: int
    cancelled_fillings: int
    avg_duration_seconds: float
    avg_volume: float
    avg_efficiency: float
    total_volume_dispensed: float
    period_start: datetime
    period_end: datetime

    def get_completion_rate(self) -> float:
        """Tasa de completitud de llenados"""
        if self.total_fillings == 0:
            return 0.0
        return (self.completed_fillings / self.total_fillings) * 100

    def to_dict(self) -> Dict:
        return {
            "total_fillings": self.total_fillings,
            "completed_fillings": self.completed_fillings,
            "cancelled_fillings": self.cancelled_fillings,
            "avg_duration_seconds": round(self.avg_duration_seconds, 2),
            "avg_volume": round(self.avg_volume, 2),
            "avg_efficiency": round(self.avg_efficiency, 2),
            "total_volume_dispensed": round(self.total_volume_dispensed, 2),
            "completion_rate": round(self.get_completion_rate(), 2),
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
        }


@dataclass
class BusinessMetrics:
    """Métricas de negocio"""

    revenue: float
    fillings_by_hour: Dict[int, int]
    fillings_by_day: Dict[str, int]
    peak_hours: List[int]
    avg_fillings_per_day: float
    water_efficiency: float

    def to_dict(self) -> Dict:
        return {
            "revenue": round(self.revenue, 2),
            "fillings_by_hour": self.fillings_by_hour,
            "fillings_by_day": self.fillings_by_day,
            "peak_hours": self.peak_hours,
            "avg_fillings_per_day": round(self.avg_fillings_per_day, 2),
            "water_efficiency": round(self.water_efficiency, 2),
        }
