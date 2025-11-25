import strawberry
from typing import List, Optional
from datetime import datetime
from strawberry.fastapi import BaseContext
from src.infrastructure.graphql.schema import (
    FlowReading,
    Filling,
    Pump,
    FlowMetricsType,
    FillingMetricsType,
    BusinessMetricsType,
    CreateFlowReadingInput,
    StartFillingInput,
    CompleteFillingInput,
    UpdatePumpLevelInput,
    PumpControlInput,
    ThresholdStatus,
)
from src.application.use_cases.record_flow_reading import RecordFlowReadingUseCase
from src.application.use_cases.manage_filling import (
    StartFillingUseCase,
    CompleteFillingUseCase,
    CancelFillingUseCase,
)
from src.application.use_cases.control_pump import (
    UpdatePumpLevelUseCase,
    ControlPumpUseCase,
    CheckPumpThresholdUseCase,
)
from src.application.dto.flow_reading_dto import CreateFlowReadingDTO
from src.application.dto.filling_dto import StartFillingDTO, CompleteFillingDTO
from src.application.dto.pump_dto import UpdatePumpLevelDTO, PumpControlDTO


class Context(BaseContext):
    """Contexto de GraphQL con dependencias"""

    def __init__(
        self,
        record_flow_reading_use_case: RecordFlowReadingUseCase,
        start_filling_use_case: StartFillingUseCase,
        complete_filling_use_case: CompleteFillingUseCase,
        cancel_filling_use_case: CancelFillingUseCase,
        update_pump_level_use_case: UpdatePumpLevelUseCase,
        control_pump_use_case: ControlPumpUseCase,
        check_pump_threshold_use_case: CheckPumpThresholdUseCase,
        flow_reading_repository,
        filling_repository,
        pump_repository,
        metrics_service,
    ):
        self.record_flow_reading_use_case = record_flow_reading_use_case
        self.start_filling_use_case = start_filling_use_case
        self.complete_filling_use_case = complete_filling_use_case
        self.cancel_filling_use_case = cancel_filling_use_case
        self.update_pump_level_use_case = update_pump_level_use_case
        self.control_pump_use_case = control_pump_use_case
        self.check_pump_threshold_use_case = check_pump_threshold_use_case
        self.flow_reading_repository = flow_reading_repository
        self.filling_repository = filling_repository
        self.pump_repository = pump_repository
        self.metrics_service = metrics_service


@strawberry.type
class Query:
    """Consultas GraphQL"""

    @strawberry.field
    async def flow_readings(
        self, info: strawberry.Info, device_id: str, limit: int = 100
    ) -> List[FlowReading]:
        """Obtiene lecturas de flujo"""
        ctx: Context = info.context
        readings = await ctx.flow_reading_repository.get_by_device_id(device_id, limit)
        return [
            FlowReading(
                id=r.id,
                device_id=r.device_id,
                flow_rate=r.flow_rate,
                total_volume=r.total_volume,
                timestamp=r.timestamp,
                pulse_count=r.pulse_count,
                unit=r.unit,
                temperature=r.temperature,
                pressure=r.pressure,
            )
            for r in readings
        ]

    @strawberry.field
    async def latest_flow_reading(
        self, info: strawberry.Info, device_id: str
    ) -> Optional[FlowReading]:
        """Obtiene la lectura más reciente"""
        ctx: Context = info.context
        reading = await ctx.flow_reading_repository.get_latest(device_id)
        if not reading:
            return None
        return FlowReading(
            id=reading.id,
            device_id=reading.device_id,
            flow_rate=reading.flow_rate,
            total_volume=reading.total_volume,
            timestamp=reading.timestamp,
            pulse_count=reading.pulse_count,
            unit=reading.unit,
            temperature=reading.temperature,
            pressure=reading.pressure,
        )

    @strawberry.field
    async def fillings(
        self, info: strawberry.Info, device_id: str, limit: int = 100
    ) -> List[Filling]:
        """Obtiene llenados"""
        ctx: Context = info.context
        fillings = await ctx.filling_repository.get_by_device_id(device_id, limit)
        return [
            Filling(
                id=f.id,
                device_id=f.device_id,
                start_time=f.start_time,
                end_time=f.end_time,
                initial_volume=f.initial_volume,
                final_volume=f.final_volume,
                target_volume=f.target_volume,
                status=f.status.value,
                duration_seconds=f.duration_seconds,
                avg_flow_rate=f.avg_flow_rate,
                actual_volume=f.get_actual_volume(),
                efficiency=f.get_efficiency(),
            )
            for f in fillings
        ]

    @strawberry.field
    async def active_filling(
        self, info: strawberry.Info, device_id: str
    ) -> Optional[Filling]:
        """Obtiene el llenado activo"""
        ctx: Context = info.context
        filling = await ctx.filling_repository.get_active_filling(device_id)
        if not filling:
            return None
        return Filling(
            id=filling.id,
            device_id=filling.device_id,
            start_time=filling.start_time,
            end_time=filling.end_time,
            initial_volume=filling.initial_volume,
            final_volume=filling.final_volume,
            target_volume=filling.target_volume,
            status=filling.status.value,
            duration_seconds=filling.duration_seconds,
            avg_flow_rate=filling.avg_flow_rate,
            actual_volume=filling.get_actual_volume(),
            efficiency=filling.get_efficiency(),
        )

    @strawberry.field
    async def pump_status(
        self, info: strawberry.Info, device_id: str
    ) -> Optional[Pump]:
        """Obtiene el estado de la bomba"""
        ctx: Context = info.context
        pump = await ctx.pump_repository.get_by_device_id(device_id)
        if not pump:
            return None
        return Pump(
            id=pump.id,
            device_id=pump.device_id,
            status=pump.status.value,
            current_level=pump.current_level,
            max_level=pump.max_level,
            threshold_stop=pump.threshold_stop,
            threshold_warning=pump.threshold_warning,
            last_updated=pump.last_updated,
            level_percentage=pump.get_level_percentage(),
            should_stop=pump.should_stop(),
            should_warn=pump.should_warn(),
        )

    @strawberry.field
    async def flow_metrics(
        self,
        info: strawberry.Info,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> FlowMetricsType:
        """Obtiene métricas de flujo"""
        ctx: Context = info.context
        metrics = await ctx.metrics_service.calculate_flow_metrics(
            device_id, start_date, end_date
        )
        return FlowMetricsType(
            avg_flow_rate=metrics.avg_flow_rate,
            min_flow_rate=metrics.min_flow_rate,
            max_flow_rate=metrics.max_flow_rate,
            total_volume=metrics.total_volume,
            efficiency=metrics.efficiency,
            period_start=metrics.period_start,
            period_end=metrics.period_end,
        )

    @strawberry.field
    async def filling_metrics(
        self,
        info: strawberry.Info,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> FillingMetricsType:
        """Obtiene métricas de llenados"""
        ctx: Context = info.context
        metrics = await ctx.metrics_service.calculate_filling_metrics(
            device_id, start_date, end_date
        )
        return FillingMetricsType(
            total_fillings=metrics.total_fillings,
            completed_fillings=metrics.completed_fillings,
            cancelled_fillings=metrics.cancelled_fillings,
            avg_duration_seconds=metrics.avg_duration_seconds,
            avg_volume=metrics.avg_volume,
            avg_efficiency=metrics.avg_efficiency,
            total_volume_dispensed=metrics.total_volume_dispensed,
            completion_rate=metrics.get_completion_rate(),
            period_start=metrics.period_start,
            period_end=metrics.period_end,
        )

    @strawberry.field
    async def business_metrics(
        self,
        info: strawberry.Info,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
        price_per_liter: float = 0.0,
    ) -> BusinessMetricsType:
        """Obtiene métricas de negocio"""
        ctx: Context = info.context
        metrics = await ctx.metrics_service.calculate_business_metrics(
            device_id, start_date, end_date, price_per_liter
        )
        return BusinessMetricsType(
            revenue=metrics.revenue,
            peak_hours=metrics.peak_hours,
            avg_fillings_per_day=metrics.avg_fillings_per_day,
            water_efficiency=metrics.water_efficiency,
        )


@strawberry.type
class Mutation:
    """Mutaciones GraphQL"""

    @strawberry.mutation
    async def record_flow_reading(
        self, info: strawberry.Info, input: CreateFlowReadingInput
    ) -> FlowReading:
        """Registra una lectura de flujo desde el ESP32"""
        ctx: Context = info.context
        dto = CreateFlowReadingDTO(
            device_id=input.device_id,
            flow_rate=input.flow_rate,
            total_volume=input.total_volume,
            pulse_count=input.pulse_count,
            unit=input.unit,
            temperature=input.temperature,
            pressure=input.pressure,
            timestamp=input.timestamp,
        )
        result = await ctx.record_flow_reading_use_case.execute(dto)
        return FlowReading(
            id=result.id,
            device_id=result.device_id,
            flow_rate=result.flow_rate,
            total_volume=result.total_volume,
            timestamp=result.timestamp,
            pulse_count=result.pulse_count,
            unit=result.unit,
            temperature=result.temperature,
            pressure=result.pressure,
        )

    @strawberry.mutation
    async def start_filling(
        self, info: strawberry.Info, input: StartFillingInput
    ) -> Filling:
        """Inicia un llenado"""
        ctx: Context = info.context
        dto = StartFillingDTO(
            device_id=input.device_id,
            target_volume=input.target_volume,
            initial_volume=input.initial_volume,
        )
        result = await ctx.start_filling_use_case.execute(dto)
        return Filling(
            id=result.id,
            device_id=result.device_id,
            start_time=result.start_time,
            end_time=result.end_time,
            initial_volume=result.initial_volume,
            final_volume=result.final_volume,
            target_volume=result.target_volume,
            status=result.status,
            duration_seconds=result.duration_seconds,
            avg_flow_rate=result.avg_flow_rate,
            actual_volume=result.actual_volume,
            efficiency=result.efficiency,
        )

    @strawberry.mutation
    async def complete_filling(
        self, info: strawberry.Info, input: CompleteFillingInput
    ) -> Filling:
        """Completa un llenado"""
        ctx: Context = info.context
        dto = CompleteFillingDTO(
            filling_id=input.filling_id, final_volume=input.final_volume
        )
        result = await ctx.complete_filling_use_case.execute(dto)
        return Filling(
            id=result.id,
            device_id=result.device_id,
            start_time=result.start_time,
            end_time=result.end_time,
            initial_volume=result.initial_volume,
            final_volume=result.final_volume,
            target_volume=result.target_volume,
            status=result.status,
            duration_seconds=result.duration_seconds,
            avg_flow_rate=result.avg_flow_rate,
            actual_volume=result.actual_volume,
            efficiency=result.efficiency,
        )

    @strawberry.mutation
    async def update_pump_level(
        self, info: strawberry.Info, input: UpdatePumpLevelInput
    ) -> Pump:
        """Actualiza el nivel de la bomba"""
        ctx: Context = info.context
        dto = UpdatePumpLevelDTO(
            device_id=input.device_id, current_level=input.current_level
        )
        result = await ctx.update_pump_level_use_case.execute(dto)
        return Pump(
            id=result.id,
            device_id=result.device_id,
            status=result.status,
            current_level=result.current_level,
            max_level=result.max_level,
            threshold_stop=result.threshold_stop,
            threshold_warning=result.threshold_warning,
            last_updated=result.last_updated,
            level_percentage=result.level_percentage,
            should_stop=result.should_stop,
            should_warn=result.should_warn,
        )

    @strawberry.mutation
    async def control_pump(
        self, info: strawberry.Info, input: PumpControlInput
    ) -> Pump:
        """Controla la bomba (encender/apagar)"""
        ctx: Context = info.context
        dto = PumpControlDTO(device_id=input.device_id, action=input.action)
        result = await ctx.control_pump_use_case.execute(dto)
        return Pump(
            id=result.id,
            device_id=result.device_id,
            status=result.status,
            current_level=result.current_level,
            max_level=result.max_level,
            threshold_stop=result.threshold_stop,
            threshold_warning=result.threshold_warning,
            last_updated=result.last_updated,
            level_percentage=result.level_percentage,
            should_stop=result.should_stop,
            should_warn=result.should_warn,
        )


# Crear el schema de GraphQL
schema = strawberry.Schema(query=Query, mutation=Mutation)
