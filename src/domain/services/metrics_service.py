from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
from src.domain.value_objects.metrics import FlowMetrics, FillingMetrics, BusinessMetrics


class MetricsService(ABC):
    """Interfaz del servicio de métricas"""

    @abstractmethod
    async def calculate_flow_metrics(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> FlowMetrics:
        """Calcula métricas de flujo para un período"""
        pass

    @abstractmethod
    async def calculate_filling_metrics(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> FillingMetrics:
        """Calcula métricas de llenados para un período"""
        pass

    @abstractmethod
    async def calculate_business_metrics(
        self, device_id: str, start_date: datetime, end_date: datetime, price_per_liter: float = 0.0
    ) -> BusinessMetrics:
        """Calcula métricas de negocio para un período"""
        pass

    @abstractmethod
    async def get_efficiency_report(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Genera un reporte de eficiencia completo"""
        pass

    @abstractmethod
    async def detect_anomalies(
        self, device_id: str, threshold: float = 100.0
    ) -> Dict[str, Any]:
        """Detecta anomalías en las lecturas"""
        pass
