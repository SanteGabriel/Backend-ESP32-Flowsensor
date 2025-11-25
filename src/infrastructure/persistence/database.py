from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from src.domain.entities.filling import FillingStatus
from src.domain.entities.pump import PumpStatus

Base = declarative_base()


class FlowReadingModel(Base):
    """Modelo de base de datos para lecturas de flujo"""

    __tablename__ = "flow_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    flow_rate = Column(Float, nullable=False)
    total_volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now, index=True)
    pulse_count = Column(Integer, nullable=True)  # Contador de pulsos del sensor
    unit = Column(String, nullable=True)  # Unidad de medida (ej: "L/min")
    temperature = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)


class FillingModel(Base):
    """Modelo de base de datos para llenados"""

    __tablename__ = "fillings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, default=datetime.now, index=True)
    end_time = Column(DateTime, nullable=True)
    initial_volume = Column(Float, nullable=False)
    final_volume = Column(Float, nullable=True)
    target_volume = Column(Float, nullable=False)
    status = Column(SQLEnum(FillingStatus), nullable=False, index=True)
    duration_seconds = Column(Float, nullable=True)
    avg_flow_rate = Column(Float, nullable=True)


class PumpModel(Base):
    """Modelo de base de datos para bombas"""

    __tablename__ = "pumps"

    id = Column(String, primary_key=True)
    device_id = Column(String, nullable=False, unique=True, index=True)
    status = Column(SQLEnum(PumpStatus), nullable=False)
    current_level = Column(Float, nullable=False)
    max_level = Column(Float, nullable=False)
    threshold_stop = Column(Float, nullable=False)
    threshold_warning = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False, default=datetime.now)
    total_runtime_hours = Column(Float, nullable=False, default=0.0)


class DatabaseManager:
    """Gestor de base de datos"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Crea las tablas en la base de datos"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Elimina las tablas de la base de datos"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def get_session(self) -> AsyncSession:
        """Obtiene una sesión de base de datos"""
        return self.async_session()
