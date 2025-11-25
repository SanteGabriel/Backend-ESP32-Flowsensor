"""
Script de migración para agregar campos pulse_count y unit a flow_readings

Este script agrega las columnas pulse_count y unit a la tabla flow_readings
de forma segura sin perder datos existentes.
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.infrastructure.persistence.database import DatabaseManager
from src.shared.config.settings import settings


async def migrate():
    """Ejecuta la migración"""
    print("🔄 Iniciando migración de base de datos...")

    db_manager = DatabaseManager(settings.DATABASE_URL)

    try:
        async with db_manager.engine.begin() as conn:
            # Verificar si las columnas ya existen
            print("📊 Verificando estructura de la tabla...")

            # Para SQLite
            if "sqlite" in settings.DATABASE_URL:
                result = await conn.execute(text("PRAGMA table_info(flow_readings)"))
                columns = [row[1] for row in result]

                if "pulse_count" not in columns:
                    print("➕ Agregando columna pulse_count...")
                    await conn.execute(
                        text("ALTER TABLE flow_readings ADD COLUMN pulse_count INTEGER")
                    )
                    print("✅ Columna pulse_count agregada")
                else:
                    print("ℹ️  Columna pulse_count ya existe")

                if "unit" not in columns:
                    print("➕ Agregando columna unit...")
                    await conn.execute(
                        text("ALTER TABLE flow_readings ADD COLUMN unit VARCHAR")
                    )
                    print("✅ Columna unit agregada")
                else:
                    print("ℹ️  Columna unit ya existe")

            # Para PostgreSQL
            elif "postgresql" in settings.DATABASE_URL:
                # Verificar si las columnas existen
                result = await conn.execute(
                    text("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'flow_readings'
                    """)
                )
                columns = [row[0] for row in result]

                if "pulse_count" not in columns:
                    print("➕ Agregando columna pulse_count...")
                    await conn.execute(
                        text("ALTER TABLE flow_readings ADD COLUMN pulse_count INTEGER")
                    )
                    print("✅ Columna pulse_count agregada")
                else:
                    print("ℹ️  Columna pulse_count ya existe")

                if "unit" not in columns:
                    print("➕ Agregando columna unit...")
                    await conn.execute(
                        text("ALTER TABLE flow_readings ADD COLUMN unit VARCHAR")
                    )
                    print("✅ Columna unit agregada")
                else:
                    print("ℹ️  Columna unit ya existe")

        print("✅ Migración completada exitosamente")

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        raise
    finally:
        await db_manager.engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate())
