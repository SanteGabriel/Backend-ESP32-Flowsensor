from datetime import datetime
from src.domain.entities.flow_reading import FlowReading
from src.domain.repositories.flow_reading_repository import FlowReadingRepository
from src.application.dto.flow_reading_dto import (
    CreateFlowReadingDTO,
    FlowReadingResponseDTO,
)


class RecordFlowReadingUseCase:
    """Caso de uso para registrar una lectura de flujo"""

    def __init__(self, flow_reading_repository: FlowReadingRepository):
        self.flow_reading_repository = flow_reading_repository
        self._last_pulse_count = {}  # Mantener registro por device_id

    async def execute(
        self, dto: CreateFlowReadingDTO
    ) -> FlowReadingResponseDTO:
        """Ejecuta el caso de uso"""

        # Parsear timestamp del dispositivo si se proporciona
        if dto.timestamp:
            try:
                timestamp = datetime.fromisoformat(dto.timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        # Calcular total_volume si no se proporciona
        # Se puede calcular desde pulse_count o mantener un acumulador
        total_volume = dto.total_volume
        if total_volume is None:
            if dto.pulse_count is not None:
                # Obtener la última lectura para calcular el volumen incremental
                last_reading = await self.flow_reading_repository.get_latest(
                    dto.device_id
                )
                if last_reading and last_reading.pulse_count is not None:
                    # Calcular volumen desde el último pulse_count
                    pulse_diff = dto.pulse_count - last_reading.pulse_count
                    # Calibración típica: ~7.5 pulsos por litro (puede variar según sensor)
                    volume_increment = pulse_diff / 7.5
                    total_volume = last_reading.total_volume + volume_increment
                else:
                    # Primera lectura, calcular desde 0
                    total_volume = dto.pulse_count / 7.5
            else:
                # Si no hay pulse_count ni total_volume, usar 0
                total_volume = 0.0

        reading = FlowReading(
            id=None,
            device_id=dto.device_id,
            flow_rate=dto.flow_rate,
            total_volume=total_volume,
            timestamp=timestamp,
            pulse_count=dto.pulse_count,
            unit=dto.unit,
            temperature=dto.temperature,
            pressure=dto.pressure,
        )

        saved_reading = await self.flow_reading_repository.save(reading)
        return FlowReadingResponseDTO.from_entity(saved_reading)
