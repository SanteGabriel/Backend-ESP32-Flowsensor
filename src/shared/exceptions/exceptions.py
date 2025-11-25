class WaterDispenserException(Exception):
    """Excepción base de la aplicación"""

    pass


class EntityNotFoundException(WaterDispenserException):
    """Excepción cuando no se encuentra una entidad"""

    pass


class InvalidOperationException(WaterDispenserException):
    """Excepción cuando se intenta una operación inválida"""

    pass


class PumpException(WaterDispenserException):
    """Excepción relacionada con la bomba"""

    pass


class FillingException(WaterDispenserException):
    """Excepción relacionada con llenados"""

    pass


class NotificationException(WaterDispenserException):
    """Excepción relacionada con notificaciones"""

    pass
