"""
Rutas REST API para el sistema de dispensador de agua
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from src.application.use_cases.record_flow_reading import RecordFlowReadingUseCase
from src.application.dto.flow_reading_dto import CreateFlowReadingDTO


class SensorDataInput(BaseModel):
    """Modelo de entrada para datos del sensor (formato ESP32)"""

    device_id: str = Field(..., description="ID del dispositivo")
    timestamp: str = Field(..., description="Timestamp ISO 8601")
    flow_rate: float = Field(..., description="Tasa de flujo en L/min")
    pulse_count: int = Field(..., description="Contador de pulsos del sensor")
    unit: str = Field(default="L/min", description="Unidad de medida")
    temperature: Optional[float] = Field(None, description="Temperatura en °C")
    pressure: Optional[float] = Field(None, description="Presión en PSI")

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "flowsensor_001",
                "timestamp": "2025-11-17T03:00:00Z",
                "flow_rate": 1.25,
                "pulse_count": 75,
                "unit": "L/min",
            }
        }


class FlowReadingResponse(BaseModel):
    """Modelo de respuesta para lectura de flujo"""

    id: int
    device_id: str
    flow_rate: float
    total_volume: float
    timestamp: datetime
    pulse_count: Optional[int] = None
    unit: Optional[str] = None
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    message: str = "Lectura registrada exitosamente"


class HealthResponse(BaseModel):
    """Respuesta para el health check"""

    status: str
    timestamp: datetime
    service: str


def create_sensor_router(record_flow_reading_use_case: RecordFlowReadingUseCase) -> APIRouter:
    """
    Crea el router para los endpoints del sensor

    Args:
        record_flow_reading_use_case: Caso de uso para registrar lecturas

    Returns:
        APIRouter configurado
    """
    router = APIRouter(prefix="/api/v1", tags=["sensor"])

    @router.post("/sensor/readings", response_model=FlowReadingResponse, status_code=201)
    async def create_flow_reading(data: SensorDataInput):
        """
        Endpoint POST para recibir datos del sensor de flujo (ESP32)

        Este endpoint recibe datos directamente del ESP32 en formato JSON
        y los registra en el sistema.

        Args:
            data: Datos del sensor en formato JSON

        Returns:
            Confirmación con los datos registrados

        Raises:
            HTTPException: Si hay un error al procesar los datos
        """
        try:
            # Convertir el input del sensor al DTO interno
            dto = CreateFlowReadingDTO(
                device_id=data.device_id,
                flow_rate=data.flow_rate,
                pulse_count=data.pulse_count,
                unit=data.unit,
                temperature=data.temperature,
                pressure=data.pressure,
                timestamp=data.timestamp,
                total_volume=None,  # Se calculará automáticamente
            )

            # Ejecutar el caso de uso
            result = await record_flow_reading_use_case.execute(dto)

            # Retornar la respuesta
            return FlowReadingResponse(
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

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error interno del servidor: {str(e)}"
            )

    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Health check endpoint para verificar que el servicio está activo

        Returns:
            Estado del servicio
        """
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            service="Water Dispenser API",
        )

    @router.get("/sensor/latest/{device_id}")
    async def get_latest_reading(device_id: str):
        """
        Obtiene la última lectura de un dispositivo

        Args:
            device_id: ID del dispositivo

        Returns:
            Última lectura registrada
        """
        # Este endpoint puede implementarse según necesidad
        return {"message": "Use GraphQL endpoint for queries"}

    return router
