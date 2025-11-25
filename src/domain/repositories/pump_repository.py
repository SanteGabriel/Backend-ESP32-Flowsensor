from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.pump import Pump


class PumpRepository(ABC):
    """Interfaz del repositorio de bombas"""

    @abstractmethod
    async def save(self, pump: Pump) -> Pump:
        """Guarda el estado de la bomba"""
        pass

    @abstractmethod
    async def update(self, pump: Pump) -> Pump:
        """Actualiza el estado de la bomba"""
        pass

    @abstractmethod
    async def get_by_id(self, pump_id: str) -> Optional[Pump]:
        """Obtiene una bomba por ID"""
        pass

    @abstractmethod
    async def get_by_device_id(self, device_id: str) -> Optional[Pump]:
        """Obtiene la bomba de un dispositivo"""
        pass
