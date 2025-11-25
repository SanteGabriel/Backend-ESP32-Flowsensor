from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.entities.filling import Filling, FillingStatus


class FillingRepository(ABC):
    """Interfaz del repositorio de llenados"""

    @abstractmethod
    async def save(self, filling: Filling) -> Filling:
        """Guarda un llenado"""
        pass

    @abstractmethod
    async def update(self, filling: Filling) -> Filling:
        """Actualiza un llenado"""
        pass

    @abstractmethod
    async def get_by_id(self, filling_id: int) -> Optional[Filling]:
        """Obtiene un llenado por ID"""
        pass

    @abstractmethod
    async def get_by_device_id(
        self, device_id: str, limit: int = 100
    ) -> List[Filling]:
        """Obtiene llenados por dispositivo"""
        pass

    @abstractmethod
    async def get_by_date_range(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> List[Filling]:
        """Obtiene llenados en un rango de fechas"""
        pass

    @abstractmethod
    async def get_by_status(
        self, device_id: str, status: FillingStatus
    ) -> List[Filling]:
        """Obtiene llenados por estado"""
        pass

    @abstractmethod
    async def get_active_filling(self, device_id: str) -> Optional[Filling]:
        """Obtiene el llenado activo (en progreso)"""
        pass

    @abstractmethod
    async def delete(self, filling_id: int) -> bool:
        """Elimina un llenado"""
        pass
