import uvicorn
import asyncio
from src.infrastructure.graphql.server import GraphQLServer
from src.shared.config.settings import settings
from src.infrastructure.controllers.pump_controller import PumpController
from src.infrastructure.notifications.push_notification_service import (
    NotificationManager,
    ConsoleNotificationService,
    FirebaseCloudMessagingService,
    ExpoNotificationService,
)


async def on_pump_threshold_stop(pump_data):
    """Callback cuando la bomba alcanza el umbral de parada"""
    print(f"🛑 ALERTA: Bomba {pump_data.device_id} detenida por umbral máximo")
    # Aquí se enviaría la notificación push a los usuarios
    # notification_manager.notify_pump_threshold_stop(pump_data, user_tokens)


async def on_pump_threshold_warning(pump_data):
    """Callback cuando la bomba alcanza el umbral de advertencia"""
    print(f"⚠️ ADVERTENCIA: Bomba {pump_data.device_id} cerca del umbral máximo")
    # notification_manager.notify_pump_threshold_warning(pump_data, user_tokens)


def create_notification_service():
    """Crea el servicio de notificaciones según la configuración"""
    if settings.NOTIFICATION_SERVICE == "fcm":
        if not settings.FCM_SERVER_KEY:
            print("⚠️ FCM_SERVER_KEY no configurado, usando servicio de consola")
            return ConsoleNotificationService()
        return FirebaseCloudMessagingService(settings.FCM_SERVER_KEY)
    elif settings.NOTIFICATION_SERVICE == "expo":
        return ExpoNotificationService()
    else:
        return ConsoleNotificationService()


async def main():
    """Función principal de la aplicación"""
    print("=" * 60)
    print("🚰 Water Dispenser Management System")
    print("=" * 60)
    print(f"📊 Base de datos: {settings.DATABASE_URL}")
    print(f"🔔 Servicio de notificaciones: {settings.NOTIFICATION_SERVICE}")
    print(f"⚙️  Puerto: {settings.PORT}")
    print("=" * 60)

    # Crear servidor GraphQL
    server = GraphQLServer(settings.DATABASE_URL)

    # Crear servicio de notificaciones
    notification_service = create_notification_service()
    notification_manager = NotificationManager(notification_service)

    # Crear controlador de bomba con monitoreo
    pump_controller = PumpController(
        pump_repository=server.pump_repo,
        check_interval=settings.PUMP_CHECK_INTERVAL,
        on_threshold_stop=on_pump_threshold_stop,
        on_threshold_warning=on_pump_threshold_warning,
    )

    # Iniciar monitoreo de bomba en segundo plano
    # asyncio.create_task(pump_controller.start_monitoring(settings.ESP32_DEVICE_ID))

    print("✅ Sistema iniciado correctamente")
    print(f"🔗 GraphQL Playground: http://{settings.HOST}:{settings.PORT}/graphql")
    print("=" * 60)

    # Iniciar servidor
    config = uvicorn.Config(
        server.get_app(),
        host=settings.HOST,
        port=settings.PORT,
        log_level="info" if settings.DEBUG else "warning",
    )
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


if __name__ == "__main__":
    asyncio.run(main())
