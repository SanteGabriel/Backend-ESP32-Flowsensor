from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.entities.flow_reading import FlowReading


class FlowReadingRepository(ABC):
    """Interfaz del repositorio de lecturas de flujo"""

    @abstractmethod
    async def save(self, reading: FlowReading) -> FlowReading:
        """Guarda una lectura de flujo"""
        pass

    @abstractmethod
    async def get_by_id(self, reading_id: int) -> Optional[FlowReading]:
        """Obtiene una lectura por ID"""
        pass

    @abstractmethod
    async def get_by_device_id(
        self, device_id: str, limit: int = 100
    ) -> List[FlowReading]:
        """Obtiene lecturas por dispositivo"""
        pass

    @abstractmethod
    async def get_by_date_range(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> List[FlowReading]:
        """Obtiene lecturas en un rango de fechas"""
        pass

    @abstractmethod
    async def delete(self, reading_id: int) -> bool:
        """Elimina una lectura"""
        pass

    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[FlowReading]:
        """Obtiene la lectura más reciente"""
        pass
