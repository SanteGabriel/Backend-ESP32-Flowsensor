# Quick Start Guide

Guía rápida para poner en marcha el sistema de gestión de dispensador de agua en menos de 5 minutos.

## Paso 1: Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd Water_dispenser

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En macOS/Linux:
source .venv/bin/activate
# En Windows:
# .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Paso 2: Configuración Básica

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# La configuración por defecto funciona sin cambios
# Para producción, edita .env según tus necesidades
```

## Paso 3: Inicializar Base de Datos

```bash
# Ejecutar script de inicialización
python scripts/init_database.py

# Cuando pregunte si deseas crear datos de ejemplo, presiona 's'
```

## Paso 4: Iniciar el Servidor

```bash
# Ejecutar la aplicación
python main.py
```

Deberías ver:

```
============================================================
🚰 Water Dispenser Management System
============================================================
📊 Base de datos: sqlite+aiosqlite:///./water_dispenser.db
🔔 Servicio de notificaciones: console
⚙️  Puerto: 8000
============================================================
✅ Sistema iniciado correctamente
🔗 GraphQL Playground: http://0.0.0.0:8000/graphql
============================================================
```

## Paso 5: Probar la API

Abre tu navegador y ve a: `http://localhost:8000/graphql`

### Primera Query: Ver estado de la bomba

```graphql
query {
  pumpStatus(deviceId: "ESP32_001") {
    status
    currentLevel
    levelPercentage
  }
}
```

### Primera Mutation: Registrar lectura de flujo

```graphql
mutation {
  recordFlowReading(input: {
    deviceId: "ESP32_001"
    flowRate: 15.5
    totalVolume: 100.0
    temperature: 23.0
    pressure: 2.0
  }) {
    id
    flowRate
    timestamp
  }
}
```

## Paso 6: Simular ESP32 (Opcional)

En otra terminal:

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar simulador
python examples/esp32_simulator.py

# Selecciona opción 1 para simular un llenado
# O opción 2 para modo continuo
```

## Estructura de Carpetas

```
Water_dispenser/
├── src/
│   ├── domain/           # Lógica de negocio
│   ├── application/      # Casos de uso
│   ├── infrastructure/   # Implementaciones (GraphQL, DB)
│   └── shared/          # Configuración y utilidades
├── scripts/             # Scripts de utilidad
├── examples/            # Ejemplos de uso
├── docs/               # Documentación adicional
├── tests/              # Tests
├── main.py             # Punto de entrada
└── requirements.txt    # Dependencias
```

## Próximos Pasos

### 1. Explorar la API GraphQL

Visita [docs/GRAPHQL_EXAMPLES.md](docs/GRAPHQL_EXAMPLES.md) para ver ejemplos completos de queries y mutations.

### 2. Configurar Notificaciones Push

Edita [.env](.env) para configurar Firebase o Expo:

```env
NOTIFICATION_SERVICE=fcm
FCM_SERVER_KEY=tu_clave_aqui
```

### 3. Conectar ESP32 Real

Usa el código de ejemplo en el [README.md](README.md) para programar tu ESP32 y conectarlo al servidor.

### 4. Cambiar a PostgreSQL (Producción)

Para producción, es recomendable usar PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/water_dispenser
```

Luego ejecuta:

```bash
python scripts/init_database.py
```

## Comandos Útiles

### Verificar instalación

```bash
pip list | grep -E "fastapi|strawberry|sqlalchemy|pandas"
```

### Ver logs del servidor

Los logs se muestran en la consola donde ejecutaste `python main.py`

### Detener el servidor

Presiona `Ctrl+C` en la terminal donde está corriendo el servidor

### Limpiar base de datos

```bash
rm water_dispenser.db
python scripts/init_database.py
```

## Ejemplos Rápidos

### Consultar últimas 10 lecturas

```graphql
query {
  flowReadings(deviceId: "ESP32_001", limit: 10) {
    flowRate
    totalVolume
    timestamp
  }
}
```

### Ver métricas del día

```graphql
query {
  fillingMetrics(
    deviceId: "ESP32_001"
    startDate: "2024-10-30T00:00:00"
    endDate: "2024-10-30T23:59:59"
  ) {
    totalFillings
    avgEfficiency
    totalVolumeDispensed
  }
}
```

### Iniciar un llenado

```graphql
mutation {
  startFilling(input: {
    deviceId: "ESP32_001"
    targetVolume: 20.0
    initialVolume: 0.0
  }) {
    id
    status
  }
}
```

## Solución de Problemas

### Error: No module named 'src'

Asegúrate de estar en el directorio raíz del proyecto:

```bash
cd Water_dispenser
python main.py
```

### Error: Database locked

Si usas SQLite y ves este error, detén todas las instancias del servidor y elimina el archivo de base de datos:

```bash
rm water_dispenser.db
python scripts/init_database.py
```

### Puerto 8000 ya en uso

Cambia el puerto en [.env](.env):

```env
PORT=8001
```

### Las queries no retornan datos

Verifica que la bomba esté inicializada:

```bash
python scripts/init_database.py
```

Y acepta crear datos de ejemplo.

## Recursos Adicionales

- **Documentación completa**: [README.md](README.md)
- **Ejemplos de GraphQL**: [docs/GRAPHQL_EXAMPLES.md](docs/GRAPHQL_EXAMPLES.md)
- **Configuración avanzada**: [.env.example](.env.example)

## Obtener Ayuda

Si encuentras problemas:

1. Revisa los logs en la consola
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que el puerto 8000 esté disponible
4. Consulta la documentación completa en [README.md](README.md)

## Contribuir

Consulta el [README.md](README.md) para información sobre cómo contribuir al proyecto.
