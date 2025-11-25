from datetime import datetime
from src.domain.entities.filling import Filling, FillingStatus
from src.domain.repositories.filling_repository import FillingRepository
from src.application.dto.filling_dto import (
    StartFillingDTO,
    CompleteFillingDTO,
    FillingResponseDTO,
)


class StartFillingUseCase:
    """Caso de uso para iniciar un llenado"""

    def __init__(self, filling_repository: FillingRepository):
        self.filling_repository = filling_repository

    async def execute(self, dto: StartFillingDTO) -> FillingResponseDTO:
        """Ejecuta el caso de uso"""
        # Verificar que no haya un llenado activo
        active = await self.filling_repository.get_active_filling(dto.device_id)
        if active:
            raise ValueError("Ya hay un llenado en progreso")

        filling = Filling(
            id=None,
            device_id=dto.device_id,
            start_time=datetime.now(),
            end_time=None,
            initial_volume=dto.initial_volume,
            final_volume=None,
            target_volume=dto.target_volume,
            status=FillingStatus.IN_PROGRESS,
        )

        saved_filling = await self.filling_repository.save(filling)
        return FillingResponseDTO.from_entity(saved_filling)


class CompleteFillingUseCase:
    """Caso de uso para completar un llenado"""

    def __init__(self, filling_repository: FillingRepository):
        self.filling_repository = filling_repository

    async def execute(self, dto: CompleteFillingDTO) -> FillingResponseDTO:
        """Ejecuta el caso de uso"""
        filling = await self.filling_repository.get_by_id(dto.filling_id)
        if not filling:
            raise ValueError(f"Llenado {dto.filling_id} no encontrado")

        if filling.status != FillingStatus.IN_PROGRESS:
            raise ValueError("El llenado no está en progreso")

        filling.complete(datetime.now(), dto.final_volume)
        updated_filling = await self.filling_repository.update(filling)
        return FillingResponseDTO.from_entity(updated_filling)


class CancelFillingUseCase:
    """Caso de uso para cancelar un llenado"""

    def __init__(self, filling_repository: FillingRepository):
        self.filling_repository = filling_repository

    async def execute(self, filling_id: int, final_volume: float) -> FillingResponseDTO:
        """Ejecuta el caso de uso"""
        filling = await self.filling_repository.get_by_id(filling_id)
        if not filling:
            raise ValueError(f"Llenado {filling_id} no encontrado")

        if filling.status != FillingStatus.IN_PROGRESS:
            raise ValueError("El llenado no está en progreso")

        filling.cancel(datetime.now(), final_volume)
        updated_filling = await self.filling_repository.update(filling)
        return FillingResponseDTO.from_entity(updated_filling)
