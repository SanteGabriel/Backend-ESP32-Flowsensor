"""
Script para inicializar la base de datos con datos de ejemplo
"""
import asyncio
from datetime import datetime
from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.persistence.repositories import (
    SQLAlchemyPumpRepository,
    SQLAlchemyFlowReadingRepository,
    SQLAlchemyFillingRepository,
)
from src.domain.entities.pump import Pump, PumpStatus
from src.domain.entities.flow_reading import FlowReading
from src.domain.entities.filling import Filling, FillingStatus
from src.shared.config.settings import settings


async def init_pump(pump_repo: SQLAlchemyPumpRepository):
    """Inicializa una bomba de ejemplo"""
    print("Creando bomba de ejemplo...")

    pump = Pump(
        id="pump_001",
        device_id=settings.ESP32_DEVICE_ID,
        status=PumpStatus.OFF,
        current_level=0.0,
        max_level=settings.PUMP_MAX_LEVEL,
        threshold_stop=settings.PUMP_THRESHOLD_STOP,
        threshold_warning=settings.PUMP_THRESHOLD_WARNING,
        last_updated=datetime.now(),
        total_runtime_hours=0.0,
    )

    try:
        saved_pump = await pump_repo.save(pump)
        print(f"✓ Bomba creada: {saved_pump.id}")
        print(f"  - Device ID: {saved_pump.device_id}")
        print(f"  - Max Level: {saved_pump.max_level}L")
        print(f"  - Threshold Stop: {saved_pump.threshold_stop}L")
        print(f"  - Threshold Warning: {saved_pump.threshold_warning}L")
    except Exception as e:
        print(f"✗ Error creando bomba: {e}")


async def init_sample_data(
    flow_repo: SQLAlchemyFlowReadingRepository,
    filling_repo: SQLAlchemyFillingRepository,
):
    """Crea datos de ejemplo para testing"""
    print("\nCreando datos de ejemplo...")

    # Crear algunas lecturas de flujo
    readings = [
        FlowReading(
            id=None,
            device_id=settings.ESP32_DEVICE_ID,
            flow_rate=12.5,
            total_volume=100.0,
            timestamp=datetime.now(),
            temperature=22.5,
            pressure=2.0,
        ),
        FlowReading(
            id=None,
            device_id=settings.ESP32_DEVICE_ID,
            flow_rate=15.3,
            total_volume=115.3,
            timestamp=datetime.now(),
            temperature=23.0,
            pressure=2.1,
        ),
    ]

    for reading in readings:
        try:
            await flow_repo.save(reading)
            print(f"✓ Lectura de flujo creada: {reading.flow_rate}L/min")
        except Exception as e:
            print(f"✗ Error creando lectura: {e}")

    # Crear un llenado completado de ejemplo
    filling = Filling(
        id=None,
        device_id=settings.ESP32_DEVICE_ID,
        start_time=datetime.now(),
        end_time=None,
        initial_volume=100.0,
        final_volume=120.0,
        target_volume=20.0,
        status=FillingStatus.COMPLETED,
        duration_seconds=45.5,
        avg_flow_rate=26.37,
    )

    try:
        await filling_repo.save(filling)
        print(f"✓ Llenado de ejemplo creado: {filling.get_actual_volume()}L")
        print(f"  - Eficiencia: {filling.get_efficiency():.1f}%")
    except Exception as e:
        print(f"✗ Error creando llenado: {e}")


async def main():
    """Función principal"""
    print("=" * 60)
    print("Inicializando Base de Datos")
    print("=" * 60)

    # Crear gestor de base de datos
    db_manager = DatabaseManager(settings.DATABASE_URL)

    # Crear tablas
    print("\nCreando tablas...")
    await db_manager.create_tables()
    print("✓ Tablas creadas")

    # Crear repositorios
    pump_repo = SQLAlchemyPumpRepository(db_manager)
    flow_repo = SQLAlchemyFlowReadingRepository(db_manager)
    filling_repo = SQLAlchemyFillingRepository(db_manager)

    # Inicializar bomba
    await init_pump(pump_repo)

    # Crear datos de ejemplo
    response = input("\n¿Deseas crear datos de ejemplo? (s/n): ")
    if response.lower() == "s":
        await init_sample_data(flow_repo, filling_repo)

    print("\n" + "=" * 60)
    print("✓ Inicialización completada")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
