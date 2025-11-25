from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Base de datos
    DATABASE_URL: str = "sqlite+aiosqlite:///./water_dispenser.db"

    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Notificaciones Push
    NOTIFICATION_SERVICE: str = "console"  # console, fcm, expo
    FCM_SERVER_KEY: Optional[str] = None
    EXPO_ACCESS_TOKEN: Optional[str] = None

    # Control de bomba
    PUMP_CHECK_INTERVAL: int = 5  # segundos
    PUMP_MAX_LEVEL: float = 100.0  # litros
    PUMP_THRESHOLD_STOP: float = 95.0  # litros o porcentaje
    PUMP_THRESHOLD_WARNING: float = 80.0  # litros o porcentaje

    # Métricas
    PRICE_PER_LITER: float = 2.0  # precio por litro para cálculos de ingresos

    # ESP32
    ESP32_DEVICE_ID: str = "flowsensor_001"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convertir DATABASE_URL de Railway (postgresql://) a formato asyncpg
        self._convert_database_url()

    def _convert_database_url(self):
        """
        Convierte DATABASE_URL de Railway al formato correcto para asyncpg

        Railway proporciona: postgresql://user:pass@host:port/db
        SQLAlchemy asyncpg necesita: postgresql+asyncpg://user:pass@host:port/db
        """
        if self.DATABASE_URL.startswith("postgresql://"):
            # Convertir postgresql:// a postgresql+asyncpg://
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
            print(f"✅ DATABASE_URL convertida para asyncpg")
        elif self.DATABASE_URL.startswith("postgres://"):
            # Heroku y algunos servicios usan postgres:// en lugar de postgresql://
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgres://", "postgresql+asyncpg://", 1
            )
            print(f"✅ DATABASE_URL convertida desde postgres:// a asyncpg")


settings = Settings()
