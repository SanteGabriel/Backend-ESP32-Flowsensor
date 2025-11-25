from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import httpx
import json


class NotificationPriority(Enum):
    """Prioridad de notificación"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Modelo de notificación"""

    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Optional[Dict] = None


class PushNotificationService(ABC):
    """Interfaz del servicio de notificaciones push"""

    @abstractmethod
    async def send(self, notification: Notification, user_tokens: List[str]) -> bool:
        """Envía una notificación push"""
        pass


class FirebaseCloudMessagingService(PushNotificationService):
    """Servicio de notificaciones usando Firebase Cloud Messaging"""

    def __init__(self, server_key: str, fcm_url: str = "https://fcm.googleapis.com/fcm/send"):
        self.server_key = server_key
        self.fcm_url = fcm_url

    async def send(self, notification: Notification, user_tokens: List[str]) -> bool:
        """Envía notificación a través de FCM"""
        if not user_tokens:
            return False

        headers = {
            "Authorization": f"Bearer {self.server_key}",
            "Content-Type": "application/json",
        }

        # Mapear prioridad
        priority_map = {
            NotificationPriority.LOW: "normal",
            NotificationPriority.NORMAL: "normal",
            NotificationPriority.HIGH: "high",
            NotificationPriority.URGENT: "high",
        }

        payload = {
            "registration_ids": user_tokens,
            "priority": priority_map[notification.priority],
            "notification": {
                "title": notification.title,
                "body": notification.message,
                "sound": "default",
            },
            "data": notification.data or {},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url, headers=headers, json=payload, timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error enviando notificación FCM: {e}")
            return False


class ExpoNotificationService(PushNotificationService):
    """Servicio de notificaciones usando Expo Push Notifications (React Native)"""

    def __init__(self, expo_url: str = "https://exp.host/--/api/v2/push/send"):
        self.expo_url = expo_url

    async def send(self, notification: Notification, user_tokens: List[str]) -> bool:
        """Envía notificación a través de Expo"""
        if not user_tokens:
            return False

        # Mapear prioridad
        priority_map = {
            NotificationPriority.LOW: "default",
            NotificationPriority.NORMAL: "default",
            NotificationPriority.HIGH: "high",
            NotificationPriority.URGENT: "high",
        }

        messages = [
            {
                "to": token,
                "sound": "default",
                "title": notification.title,
                "body": notification.message,
                "priority": priority_map[notification.priority],
                "data": notification.data or {},
            }
            for token in user_tokens
        ]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.expo_url, json=messages, timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error enviando notificación Expo: {e}")
            return False


class ConsoleNotificationService(PushNotificationService):
    """Servicio de notificaciones para desarrollo (imprime en consola)"""

    async def send(self, notification: Notification, user_tokens: List[str]) -> bool:
        """Imprime la notificación en consola"""
        print("\n" + "=" * 50)
        print(f"🔔 NOTIFICACIÓN PUSH [{notification.priority.value.upper()}]")
        print("=" * 50)
        print(f"Título: {notification.title}")
        print(f"Mensaje: {notification.message}")
        print(f"Destinatarios: {len(user_tokens)}")
        if notification.data:
            print(f"Datos: {json.dumps(notification.data, indent=2)}")
        print("=" * 50 + "\n")
        return True


class NotificationManager:
    """Gestor de notificaciones para diferentes eventos del sistema"""

    def __init__(self, notification_service: PushNotificationService):
        self.notification_service = notification_service

    async def notify_pump_threshold_stop(self, pump_data: Dict, user_tokens: List[str]):
        """Notifica que la bomba alcanzó el umbral de parada"""
        notification = Notification(
            title="🛑 Bomba detenida",
            message=f"La bomba ha alcanzado el nivel máximo ({pump_data['current_level']:.1f}L) y se ha detenido automáticamente.",
            priority=NotificationPriority.HIGH,
            data={
                "type": "pump_stop",
                "device_id": pump_data["device_id"],
                "level": pump_data["current_level"],
                "level_percentage": pump_data.get("level_percentage", 0),
            },
        )
        return await self.notification_service.send(notification, user_tokens)

    async def notify_pump_threshold_warning(
        self, pump_data: Dict, user_tokens: List[str]
    ):
        """Notifica advertencia de nivel cercano al máximo"""
        notification = Notification(
            title="⚠️ Nivel de agua alto",
            message=f"La bomba está alcanzando el nivel máximo ({pump_data['current_level']:.1f}L). Nivel actual: {pump_data.get('level_percentage', 0):.1f}%",
            priority=NotificationPriority.NORMAL,
            data={
                "type": "pump_warning",
                "device_id": pump_data["device_id"],
                "level": pump_data["current_level"],
                "level_percentage": pump_data.get("level_percentage", 0),
            },
        )
        return await self.notification_service.send(notification, user_tokens)

    async def notify_filling_complete(self, filling_data: Dict, user_tokens: List[str]):
        """Notifica que un llenado se completó"""
        notification = Notification(
            title="✅ Llenado completado",
            message=f"Llenado completado: {filling_data['actual_volume']:.1f}L en {filling_data.get('duration_seconds', 0):.1f}s. Eficiencia: {filling_data.get('efficiency', 0):.1f}%",
            priority=NotificationPriority.NORMAL,
            data={
                "type": "filling_complete",
                "filling_id": filling_data["id"],
                "volume": filling_data["actual_volume"],
                "efficiency": filling_data.get("efficiency", 0),
            },
        )
        return await self.notification_service.send(notification, user_tokens)

    async def notify_anomaly_detected(
        self, anomaly_data: Dict, user_tokens: List[str]
    ):
        """Notifica detección de anomalía en el flujo"""
        notification = Notification(
            title="⚡ Anomalía detectada",
            message=f"Se detectó un flujo anormal: {anomaly_data['flow_rate']:.1f}L/min. {anomaly_data.get('reason', '')}",
            priority=NotificationPriority.HIGH,
            data={
                "type": "anomaly",
                "reading_id": anomaly_data.get("id"),
                "flow_rate": anomaly_data["flow_rate"],
                "reason": anomaly_data.get("reason", ""),
            },
        )
        return await self.notification_service.send(notification, user_tokens)

    async def notify_low_efficiency(
        self, efficiency_data: Dict, user_tokens: List[str]
    ):
        """Notifica baja eficiencia del sistema"""
        notification = Notification(
            title="📊 Eficiencia baja",
            message=f"La eficiencia del sistema es baja: {efficiency_data['efficiency']:.1f}%. Requiere atención.",
            priority=NotificationPriority.NORMAL,
            data={
                "type": "low_efficiency",
                "efficiency": efficiency_data["efficiency"],
                "device_id": efficiency_data.get("device_id"),
            },
        )
        return await self.notification_service.send(notification, user_tokens)
