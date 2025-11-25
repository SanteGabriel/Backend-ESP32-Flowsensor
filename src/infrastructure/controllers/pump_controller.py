import asyncio
from typing import Optional, Callable
from datetime import datetime
from src.domain.repositories.pump_repository import PumpRepository
from src.domain.entities.pump import PumpStatus


class PumpController:
    """Controlador de bomba con monitoreo automático de umbrales"""

    def __init__(
        self,
        pump_repository: PumpRepository,
        check_interval: int = 5,  # segundos
        on_threshold_stop: Optional[Callable] = None,
        on_threshold_warning: Optional[Callable] = None,
    ):
        self.pump_repository = pump_repository
        self.check_interval = check_interval
        self.on_threshold_stop = on_threshold_stop
        self.on_threshold_warning = on_threshold_warning
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False

    async def start_monitoring(self, device_id: str):
        """Inicia el monitoreo automático de la bomba"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_loop(device_id))

    async def stop_monitoring(self):
        """Detiene el monitoreo automático"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self, device_id: str):
        """Loop de monitoreo de la bomba"""
        warning_sent = False
        stop_sent = False

        while self.is_monitoring:
            try:
                pump = await self.pump_repository.get_by_device_id(device_id)

                if not pump:
                    await asyncio.sleep(self.check_interval)
                    continue

                # Verificar umbral de parada
                if pump.should_stop():
                    if pump.status == PumpStatus.ON:
                        # Apagar bomba automáticamente
                        pump.turn_off()
                        await self.pump_repository.update(pump)

                    # Enviar notificación de parada
                    if not stop_sent and self.on_threshold_stop:
                        await self.on_threshold_stop(pump)
                        stop_sent = True

                # Verificar umbral de advertencia
                elif pump.should_warn():
                    if not warning_sent and self.on_threshold_warning:
                        await self.on_threshold_warning(pump)
                        warning_sent = True
                else:
                    # Resetear flags si el nivel baja
                    warning_sent = False
                    stop_sent = False

                await asyncio.sleep(self.check_interval)

            except Exception as e:
                print(f"Error en monitoreo de bomba: {e}")
                await asyncio.sleep(self.check_interval)

    async def emergency_stop(self, device_id: str) -> bool:
        """Detiene la bomba de emergencia"""
        try:
            pump = await self.pump_repository.get_by_device_id(device_id)
            if not pump:
                return False

            pump.turn_off()
            await self.pump_repository.update(pump)
            return True
        except Exception as e:
            print(f"Error en parada de emergencia: {e}")
            return False

    async def get_pump_status(self, device_id: str) -> dict:
        """Obtiene el estado actual de la bomba"""
        pump = await self.pump_repository.get_by_device_id(device_id)
        if not pump:
            return {"error": "Bomba no encontrada"}

        return {
            "id": pump.id,
            "device_id": pump.device_id,
            "status": pump.status.value,
            "current_level": pump.current_level,
            "max_level": pump.max_level,
            "level_percentage": pump.get_level_percentage(),
            "threshold_stop": pump.threshold_stop,
            "threshold_warning": pump.threshold_warning,
            "should_stop": pump.should_stop(),
            "should_warn": pump.should_warn(),
            "last_updated": pump.last_updated.isoformat(),
        }
