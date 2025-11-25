# REST API Documentation

## Introducción

El sistema de dispensador de agua proporciona una API REST además de la API GraphQL para facilitar la integración con dispositivos IoT como el ESP32.

La API REST está optimizada para:
- Dispositivos con recursos limitados
- Simplicidad en el envío de datos
- Compatibilidad con bibliotecas HTTP estándar

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### 1. Registrar Lectura de Sensor

**Endpoint:** `POST /sensor/readings`

**Descripción:** Recibe datos del sensor de flujo y los registra en el sistema.

**Headers:**
```http
Content-Type: application/json
```

**Request Body:**

```json
{
  "device_id": "flowsensor_001",
  "timestamp": "2025-11-17T03:00:00Z",
  "flow_rate": 1.25,
  "pulse_count": 75,
  "unit": "L/min",
  "temperature": 22.5,
  "pressure": 2.1
}
```

**Campos:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `device_id` | string | ✅ | Identificador único del dispositivo |
| `timestamp` | string | ✅ | Timestamp ISO 8601 (UTC) |
| `flow_rate` | float | ✅ | Tasa de flujo en L/min |
| `pulse_count` | integer | ✅ | Contador de pulsos del sensor |
| `unit` | string | ❌ | Unidad de medida (default: "L/min") |
| `temperature` | float | ❌ | Temperatura del agua en °C |
| `pressure` | float | ❌ | Presión en PSI |

**Response (201 Created):**

```json
{
  "id": 123,
  "device_id": "flowsensor_001",
  "flow_rate": 1.25,
  "total_volume": 10.5,
  "timestamp": "2025-11-17T03:00:00Z",
  "pulse_count": 75,
  "unit": "L/min",
  "temperature": 22.5,
  "pressure": 2.1,
  "message": "Lectura registrada exitosamente"
}
```

**Errores:**

- `400 Bad Request` - Datos inválidos
- `500 Internal Server Error` - Error del servidor

**Ejemplo con cURL:**

```bash
curl -X POST http://localhost:8000/api/v1/sensor/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "flowsensor_001",
    "timestamp": "2025-11-17T03:00:00Z",
    "flow_rate": 1.25,
    "pulse_count": 75,
    "unit": "L/min"
  }'
```

**Ejemplo con Python:**

```python
import requests
from datetime import datetime

url = "http://localhost:8000/api/v1/sensor/readings"

data = {
    "device_id": "flowsensor_001",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "flow_rate": 1.25,
    "pulse_count": 75,
    "unit": "L/min"
}

response = requests.post(url, json=data)
print(response.json())
```

### 2. Health Check

**Endpoint:** `GET /health`

**Descripción:** Verifica que el servicio esté activo.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T03:00:00Z",
  "service": "Water Dispenser API"
}
```

**Ejemplo con cURL:**

```bash
curl http://localhost:8000/api/v1/health
```

## Integración con ESP32

### Código Arduino Básico

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* SERVER_URL = "http://192.168.1.100:8000/api/v1/sensor/readings";

void sendData(float flowRate, unsigned long pulseCount) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    // Crear JSON
    StaticJsonDocument<256> doc;
    doc["device_id"] = "flowsensor_001";
    doc["timestamp"] = getISOTimestamp();  // Implementar función
    doc["flow_rate"] = flowRate;
    doc["pulse_count"] = pulseCount;
    doc["unit"] = "L/min";

    String jsonString;
    serializeJson(doc, jsonString);

    // Enviar POST
    int httpCode = http.POST(jsonString);

    if (httpCode == 201) {
      Serial.println("✅ Datos enviados");
    }

    http.end();
  }
}
```

Ver el archivo completo en: [`examples/esp32_flow_sensor_rest.ino`](../examples/esp32_flow_sensor_rest.ino)

## Cálculo Automático de Volumen

El sistema **calcula automáticamente** el `total_volume` basándose en el `pulse_count`:

1. **Primera lectura:** `total_volume = pulse_count / 7.5`
2. **Lecturas subsecuentes:** `total_volume = total_volume_anterior + (pulse_diff / 7.5)`

Donde:
- `pulse_diff = pulse_count_actual - pulse_count_anterior`
- `7.5` es el factor de calibración del sensor YF-S201 (ajustable)

Por lo tanto, **no es necesario enviar** el campo `total_volume` desde el ESP32.

## Formato de Timestamp

El timestamp debe estar en formato **ISO 8601 UTC**:

```
2025-11-17T03:00:00Z
```

Ejemplos válidos:
- `2025-11-17T03:00:00Z`
- `2025-11-17T03:00:00.000Z`
- `2025-11-17T03:00:00+00:00`

## CORS

La API REST tiene CORS habilitado para desarrollo. En producción, configurar orígenes específicos en:

```python
# src/infrastructure/graphql/server.py
allow_origins=["https://tu-dominio.com"]
```

## Documentación Interactiva

FastAPI proporciona documentación automática en:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Comparación REST vs GraphQL

| Característica | REST | GraphQL |
|----------------|------|---------|
| Simplicidad | ✅ Muy simple | ⚠️ Más complejo |
| Flexible | ❌ Endpoints fijos | ✅ Queries flexibles |
| Mejor para | ESP32, IoT | Aplicaciones web/móvil |
| Sobrecarga | Baja | Media |
| Documentación | Swagger | GraphiQL |

**Recomendación:**
- **REST:** Para dispositivos IoT (ESP32, sensores)
- **GraphQL:** Para aplicaciones frontend y análisis de datos

## Ejemplos de Uso

### Enviar datos cada 5 segundos desde ESP32

```cpp
void loop() {
  static unsigned long lastSend = 0;
  unsigned long now = millis();

  if (now - lastSend >= 5000) {  // Cada 5 segundos
    calculateFlow();
    sendData(flowRate, totalPulseCount);
    lastSend = now;
  }
}
```

### Monitorear con Python

```python
import requests
import time
from datetime import datetime

url = "http://localhost:8000/api/v1/sensor/readings"

while True:
    data = {
        "device_id": "test_sensor",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "flow_rate": 1.5,
        "pulse_count": int(time.time() * 7.5),
        "unit": "L/min"
    }

    try:
        response = requests.post(url, json=data)
        print(f"✅ {response.status_code}: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

    time.sleep(5)
```

### Testing con HTTPie

```bash
# Instalar: pip install httpie

# Enviar datos
http POST localhost:8000/api/v1/sensor/readings \
  device_id="test_001" \
  timestamp="2025-11-17T03:00:00Z" \
  flow_rate:=1.25 \
  pulse_count:=75 \
  unit="L/min"

# Health check
http GET localhost:8000/api/v1/health
```

## Troubleshooting

### Error 422: Validation Error

**Problema:** Datos inválidos o campos faltantes

**Solución:** Verificar que todos los campos requeridos estén presentes y con el tipo correcto

```json
{
  "detail": [
    {
      "loc": ["body", "flow_rate"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Error 500: Internal Server Error

**Problema:** Error en el servidor (base de datos, cálculos, etc.)

**Solución:** Revisar logs del servidor

```bash
python main.py
# Ver mensajes de error en consola
```

### ESP32 no puede conectar

**Problemas comunes:**

1. **URL incorrecta:** Verificar IP y puerto del servidor
2. **Firewall:** Asegurar que el puerto 8000 esté abierto
3. **WiFi:** Verificar credenciales y conexión
4. **Timeout:** Aumentar timeout en ESP32

```cpp
http.setTimeout(10000);  // 10 segundos
```

## Próximos Pasos

Para consultar datos históricos y métricas, usar la **API GraphQL**:

- Ver [README.md](../README.md) para ejemplos GraphQL
- Playground: http://localhost:8000/graphql
