from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from src.domain.entities.flow_reading import FlowReading
from src.domain.entities.filling import Filling, FillingStatus
from src.domain.entities.pump import Pump
from src.domain.repositories.flow_reading_repository import FlowReadingRepository
from src.domain.repositories.filling_repository import FillingRepository
from src.domain.repositories.pump_repository import PumpRepository
from src.infrastructure.persistence.database import (
    DatabaseManager,
    FlowReadingModel,
    FillingModel,
    PumpModel,
)


class SQLAlchemyFlowReadingRepository(FlowReadingRepository):
    """Implementación de repositorio de lecturas de flujo con SQLAlchemy"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def save(self, reading: FlowReading) -> FlowReading:
        """Guarda una lectura de flujo"""
        async with self.db_manager.get_session() as session:
            model = FlowReadingModel(
                device_id=reading.device_id,
                flow_rate=reading.flow_rate,
                total_volume=reading.total_volume,
                timestamp=reading.timestamp,
                pulse_count=reading.pulse_count,
                unit=reading.unit,
                temperature=reading.temperature,
                pressure=reading.pressure,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            return FlowReading(
                id=model.id,
                device_id=model.device_id,
                flow_rate=model.flow_rate,
                total_volume=model.total_volume,
                timestamp=model.timestamp,
                pulse_count=model.pulse_count,
                unit=model.unit,
                temperature=model.temperature,
                pressure=model.pressure,
            )

    async def get_by_id(self, reading_id: int) -> Optional[FlowReading]:
        """Obtiene una lectura por ID"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FlowReadingModel).where(FlowReadingModel.id == reading_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return FlowReading(
                id=model.id,
                device_id=model.device_id,
                flow_rate=model.flow_rate,
                total_volume=model.total_volume,
                timestamp=model.timestamp,
                pulse_count=model.pulse_count,
                unit=model.unit,
                temperature=model.temperature,
                pressure=model.pressure,
            )

    async def get_by_device_id(
        self, device_id: str, limit: int = 100
    ) -> List[FlowReading]:
        """Obtiene lecturas por dispositivo"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FlowReadingModel)
                .where(FlowReadingModel.device_id == device_id)
                .order_by(FlowReadingModel.timestamp.desc())
                .limit(limit)
            )
            models = result.scalars().all()

            return [
                FlowReading(
                    id=m.id,
                    device_id=m.device_id,
                    flow_rate=m.flow_rate,
                    total_volume=m.total_volume,
                    timestamp=m.timestamp,
                    pulse_count=m.pulse_count,
                    unit=m.unit,
                    temperature=m.temperature,
                    pressure=m.pressure,
                )
                for m in models
            ]

    async def get_by_date_range(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> List[FlowReading]:
        """Obtiene lecturas en un rango de fechas"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FlowReadingModel)
                .where(
                    and_(
                        FlowReadingModel.device_id == device_id,
                        FlowReadingModel.timestamp >= start_date,
                        FlowReadingModel.timestamp <= end_date,
                    )
                )
                .order_by(FlowReadingModel.timestamp.asc())
            )
            models = result.scalars().all()

            return [
                FlowReading(
                    id=m.id,
                    device_id=m.device_id,
                    flow_rate=m.flow_rate,
                    total_volume=m.total_volume,
                    timestamp=m.timestamp,
                    pulse_count=m.pulse_count,
                    unit=m.unit,
                    temperature=m.temperature,
                    pressure=m.pressure,
                )
                for m in models
            ]

    async def delete(self, reading_id: int) -> bool:
        """Elimina una lectura"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FlowReadingModel).where(FlowReadingModel.id == reading_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            await session.delete(model)
            await session.commit()
            return True

    async def get_latest(self, device_id: str) -> Optional[FlowReading]:
        """Obtiene la lectura más reciente"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FlowReadingModel)
                .where(FlowReadingModel.device_id == device_id)
                .order_by(FlowReadingModel.timestamp.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return FlowReading(
                id=model.id,
                device_id=model.device_id,
                flow_rate=model.flow_rate,
                total_volume=model.total_volume,
                timestamp=model.timestamp,
                pulse_count=model.pulse_count,
                unit=model.unit,
                temperature=model.temperature,
                pressure=model.pressure,
            )


class SQLAlchemyFillingRepository(FillingRepository):
    """Implementación de repositorio de llenados con SQLAlchemy"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def save(self, filling: Filling) -> Filling:
        """Guarda un llenado"""
        async with self.db_manager.get_session() as session:
            model = FillingModel(
                device_id=filling.device_id,
                start_time=filling.start_time,
                end_time=filling.end_time,
                initial_volume=filling.initial_volume,
                final_volume=filling.final_volume,
                target_volume=filling.target_volume,
                status=filling.status,
                duration_seconds=filling.duration_seconds,
                avg_flow_rate=filling.avg_flow_rate,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            return Filling(
                id=model.id,
                device_id=model.device_id,
                start_time=model.start_time,
                end_time=model.end_time,
                initial_volume=model.initial_volume,
                final_volume=model.final_volume,
                target_volume=model.target_volume,
                status=model.status,
                duration_seconds=model.duration_seconds,
                avg_flow_rate=model.avg_flow_rate,
            )

    async def update(self, filling: Filling) -> Filling:
        """Actualiza un llenado"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel).where(FillingModel.id == filling.id)
            )
            model = result.scalar_one_or_none()

            if not model:
                raise ValueError(f"Llenado {filling.id} no encontrado")

            model.end_time = filling.end_time
            model.final_volume = filling.final_volume
            model.status = filling.status
            model.duration_seconds = filling.duration_seconds
            model.avg_flow_rate = filling.avg_flow_rate

            await session.commit()
            await session.refresh(model)

            return Filling(
                id=model.id,
                device_id=model.device_id,
                start_time=model.start_time,
                end_time=model.end_time,
                initial_volume=model.initial_volume,
                final_volume=model.final_volume,
                target_volume=model.target_volume,
                status=model.status,
                duration_seconds=model.duration_seconds,
                avg_flow_rate=model.avg_flow_rate,
            )

    async def get_by_id(self, filling_id: int) -> Optional[Filling]:
        """Obtiene un llenado por ID"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel).where(FillingModel.id == filling_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return Filling(
                id=model.id,
                device_id=model.device_id,
                start_time=model.start_time,
                end_time=model.end_time,
                initial_volume=model.initial_volume,
                final_volume=model.final_volume,
                target_volume=model.target_volume,
                status=model.status,
                duration_seconds=model.duration_seconds,
                avg_flow_rate=model.avg_flow_rate,
            )

    async def get_by_device_id(
        self, device_id: str, limit: int = 100
    ) -> List[Filling]:
        """Obtiene llenados por dispositivo"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel)
                .where(FillingModel.device_id == device_id)
                .order_by(FillingModel.start_time.desc())
                .limit(limit)
            )
            models = result.scalars().all()

            return [
                Filling(
                    id=m.id,
                    device_id=m.device_id,
                    start_time=m.start_time,
                    end_time=m.end_time,
                    initial_volume=m.initial_volume,
                    final_volume=m.final_volume,
                    target_volume=m.target_volume,
                    status=m.status,
                    duration_seconds=m.duration_seconds,
                    avg_flow_rate=m.avg_flow_rate,
                )
                for m in models
            ]

    async def get_by_date_range(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> List[Filling]:
        """Obtiene llenados en un rango de fechas"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel)
                .where(
                    and_(
                        FillingModel.device_id == device_id,
                        FillingModel.start_time >= start_date,
                        FillingModel.start_time <= end_date,
                    )
                )
                .order_by(FillingModel.start_time.asc())
            )
            models = result.scalars().all()

            return [
                Filling(
                    id=m.id,
                    device_id=m.device_id,
                    start_time=m.start_time,
                    end_time=m.end_time,
                    initial_volume=m.initial_volume,
                    final_volume=m.final_volume,
                    target_volume=m.target_volume,
                    status=m.status,
                    duration_seconds=m.duration_seconds,
                    avg_flow_rate=m.avg_flow_rate,
                )
                for m in models
            ]

    async def get_by_status(
        self, device_id: str, status: FillingStatus
    ) -> List[Filling]:
        """Obtiene llenados por estado"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel)
                .where(
                    and_(
                        FillingModel.device_id == device_id,
                        FillingModel.status == status,
                    )
                )
                .order_by(FillingModel.start_time.desc())
            )
            models = result.scalars().all()

            return [
                Filling(
                    id=m.id,
                    device_id=m.device_id,
                    start_time=m.start_time,
                    end_time=m.end_time,
                    initial_volume=m.initial_volume,
                    final_volume=m.final_volume,
                    target_volume=m.target_volume,
                    status=m.status,
                    duration_seconds=m.duration_seconds,
                    avg_flow_rate=m.avg_flow_rate,
                )
                for m in models
            ]

    async def get_active_filling(self, device_id: str) -> Optional[Filling]:
        """Obtiene el llenado activo"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel)
                .where(
                    and_(
                        FillingModel.device_id == device_id,
                        FillingModel.status == FillingStatus.IN_PROGRESS,
                    )
                )
                .order_by(FillingModel.start_time.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return Filling(
                id=model.id,
                device_id=model.device_id,
                start_time=model.start_time,
                end_time=model.end_time,
                initial_volume=model.initial_volume,
                final_volume=model.final_volume,
                target_volume=model.target_volume,
                status=model.status,
                duration_seconds=model.duration_seconds,
                avg_flow_rate=model.avg_flow_rate,
            )

    async def delete(self, filling_id: int) -> bool:
        """Elimina un llenado"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(FillingModel).where(FillingModel.id == filling_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return False

            await session.delete(model)
            await session.commit()
            return True


class SQLAlchemyPumpRepository(PumpRepository):
    """Implementación de repositorio de bombas con SQLAlchemy"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def save(self, pump: Pump) -> Pump:
        """Guarda el estado de la bomba"""
        async with self.db_manager.get_session() as session:
            model = PumpModel(
                id=pump.id,
                device_id=pump.device_id,
                status=pump.status,
                current_level=pump.current_level,
                max_level=pump.max_level,
                threshold_stop=pump.threshold_stop,
                threshold_warning=pump.threshold_warning,
                last_updated=pump.last_updated,
                total_runtime_hours=pump.total_runtime_hours,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            return Pump(
                id=model.id,
                device_id=model.device_id,
                status=model.status,
                current_level=model.current_level,
                max_level=model.max_level,
                threshold_stop=model.threshold_stop,
                threshold_warning=model.threshold_warning,
                last_updated=model.last_updated,
                total_runtime_hours=model.total_runtime_hours,
            )

    async def update(self, pump: Pump) -> Pump:
        """Actualiza el estado de la bomba"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(PumpModel).where(PumpModel.id == pump.id)
            )
            model = result.scalar_one_or_none()

            if not model:
                raise ValueError(f"Bomba {pump.id} no encontrada")

            model.status = pump.status
            model.current_level = pump.current_level
            model.last_updated = pump.last_updated
            model.total_runtime_hours = pump.total_runtime_hours

            await session.commit()
            await session.refresh(model)

            return Pump(
                id=model.id,
                device_id=model.device_id,
                status=model.status,
                current_level=model.current_level,
                max_level=model.max_level,
                threshold_stop=model.threshold_stop,
                threshold_warning=model.threshold_warning,
                last_updated=model.last_updated,
                total_runtime_hours=model.total_runtime_hours,
            )

    async def get_by_id(self, pump_id: str) -> Optional[Pump]:
        """Obtiene una bomba por ID"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(PumpModel).where(PumpModel.id == pump_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return Pump(
                id=model.id,
                device_id=model.device_id,
                status=model.status,
                current_level=model.current_level,
                max_level=model.max_level,
                threshold_stop=model.threshold_stop,
                threshold_warning=model.threshold_warning,
                last_updated=model.last_updated,
                total_runtime_hours=model.total_runtime_hours,
            )

    async def get_by_device_id(self, device_id: str) -> Optional[Pump]:
        """Obtiene la bomba de un dispositivo"""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(PumpModel).where(PumpModel.device_id == device_id)
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return Pump(
                id=model.id,
                device_id=model.device_id,
                status=model.status,
                current_level=model.current_level,
                max_level=model.max_level,
                threshold_stop=model.threshold_stop,
                threshold_warning=model.threshold_warning,
                last_updated=model.last_updated,
                total_runtime_hours=model.total_runtime_hours,
            )
