from src.domain.entities.pump import Pump, PumpStatus
from src.domain.repositories.pump_repository import PumpRepository
from src.application.dto.pump_dto import (
    UpdatePumpLevelDTO,
    PumpControlDTO,
    PumpResponseDTO,
)


class UpdatePumpLevelUseCase:
    """Caso de uso para actualizar el nivel de la bomba"""

    def __init__(self, pump_repository: PumpRepository):
        self.pump_repository = pump_repository

    async def execute(self, dto: UpdatePumpLevelDTO) -> PumpResponseDTO:
        """Ejecuta el caso de uso"""
        pump = await self.pump_repository.get_by_device_id(dto.device_id)
        if not pump:
            raise ValueError(f"Bomba no encontrada para dispositivo {dto.device_id}")

        pump.update_level(dto.current_level)
        updated_pump = await self.pump_repository.update(pump)
        return PumpResponseDTO.from_entity(updated_pump)


class ControlPumpUseCase:
    """Caso de uso para controlar la bomba (encender/apagar)"""

    def __init__(self, pump_repository: PumpRepository):
        self.pump_repository = pump_repository

    async def execute(self, dto: PumpControlDTO) -> PumpResponseDTO:
        """Ejecuta el caso de uso"""
        pump = await self.pump_repository.get_by_device_id(dto.device_id)
        if not pump:
            raise ValueError(f"Bomba no encontrada para dispositivo {dto.device_id}")

        if dto.action == "on":
            pump.turn_on()
        elif dto.action == "off":
            pump.turn_off()
        else:
            raise ValueError(f"Acción no válida: {dto.action}")

        updated_pump = await self.pump_repository.update(pump)
        return PumpResponseDTO.from_entity(updated_pump)


class CheckPumpThresholdUseCase:
    """Caso de uso para verificar umbrales de la bomba"""

    def __init__(self, pump_repository: PumpRepository):
        self.pump_repository = pump_repository

    async def execute(self, device_id: str) -> dict:
        """Ejecuta el caso de uso y retorna el estado de los umbrales"""
        pump = await self.pump_repository.get_by_device_id(device_id)
        if not pump:
            raise ValueError(f"Bomba no encontrada para dispositivo {device_id}")

        return {
            "should_stop": pump.should_stop(),
            "should_warn": pump.should_warn(),
            "current_level": pump.current_level,
            "threshold_stop": pump.threshold_stop,
            "threshold_warning": pump.threshold_warning,
            "level_percentage": pump.get_level_percentage(),
        }
