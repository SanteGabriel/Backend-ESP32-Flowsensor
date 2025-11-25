/**
 * ESP32 Flow Sensor - REST API Version
 *
 * Este código lee datos del sensor de flujo YF-S201 y los envía
 * al servidor mediante el endpoint REST POST /api/v1/sensor/readings
 *
 * Hardware:
 * - ESP32
 * - Sensor de flujo YF-S201 (o compatible)
 * - Conexión WiFi
 *
 * Conexiones:
 * - Sensor VCC -> 5V
 * - Sensor GND -> GND
 * - Sensor Signal -> GPIO 2 (configurable)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>

// ========== CONFIGURACIÓN ==========
// WiFi
const char* WIFI_SSID = "TU_WIFI";
const char* WIFI_PASSWORD = "TU_PASSWORD";

// Servidor
const char* SERVER_URL = "http://192.168.1.100:8000/api/v1/sensor/readings";
const char* DEVICE_ID = "flowsensor_001";

// Hardware
const int FLOW_SENSOR_PIN = 2;  // GPIO para el sensor de flujo

// Calibración del sensor
// YF-S201: ~7.5 pulsos por litro (450 pulsos por minuto a 1 L/min)
const float CALIBRATION_FACTOR = 7.5;  // Ajustar según tu sensor

// Intervalos
const unsigned long SEND_INTERVAL = 5000;  // Enviar cada 5 segundos
const unsigned long SAMPLE_INTERVAL = 1000;  // Muestrear cada 1 segundo

// NTP para timestamp
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = -21600;  // GMT-6 (ajustar según tu zona)
const int DAYLIGHT_OFFSET_SEC = 0;

// ========== VARIABLES GLOBALES ==========
volatile unsigned long pulseCount = 0;
unsigned long totalPulseCount = 0;
float flowRate = 0.0;
unsigned long lastSampleTime = 0;
unsigned long lastSendTime = 0;

// ========== FUNCIONES ==========

/**
 * Interrupción para contar pulsos del sensor
 */
void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

/**
 * Obtiene timestamp en formato ISO 8601
 */
String getISOTimestamp() {
  time_t now;
  struct tm timeinfo;

  if (!getLocalTime(&timeinfo)) {
    Serial.println("⚠️ Error obteniendo tiempo");
    return "";
  }

  time(&now);
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", gmtime(&now));
  return String(buffer);
}

/**
 * Conecta al WiFi
 */
void connectWiFi() {
  Serial.println("🔌 Conectando a WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi conectado");
    Serial.print("📡 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Error conectando a WiFi");
  }
}

/**
 * Calcula el flujo en L/min
 */
void calculateFlowRate() {
  unsigned long currentTime = millis();
  unsigned long elapsedTime = currentTime - lastSampleTime;

  if (elapsedTime >= SAMPLE_INTERVAL) {
    // Deshabilitar interrupciones temporalmente
    detachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN));

    // Calcular flujo en L/min
    // flowRate (L/min) = (pulsos / tiempo_en_segundos) / calibración
    float seconds = elapsedTime / 1000.0;
    flowRate = (pulseCount / seconds) / CALIBRATION_FACTOR;

    // Acumular pulsos totales
    totalPulseCount += pulseCount;

    // Mostrar en serial
    Serial.printf("💧 Flujo: %.2f L/min | Pulsos: %lu | Total: %lu\n",
                  flowRate, pulseCount, totalPulseCount);

    // Reset contador
    pulseCount = 0;
    lastSampleTime = currentTime;

    // Reactivar interrupciones
    attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulseCounter, FALLING);
  }
}

/**
 * Envía datos al servidor mediante REST API
 */
void sendDataToServer() {
  unsigned long currentTime = millis();

  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;

      // Configurar request
      http.begin(SERVER_URL);
      http.addHeader("Content-Type", "application/json");

      // Crear JSON con los datos
      StaticJsonDocument<256> doc;
      doc["device_id"] = DEVICE_ID;
      doc["timestamp"] = getISOTimestamp();
      doc["flow_rate"] = flowRate;
      doc["pulse_count"] = totalPulseCount;
      doc["unit"] = "L/min";

      // Opcional: agregar temperatura y presión si tienes sensores
      // doc["temperature"] = 25.5;
      // doc["pressure"] = 2.1;

      // Serializar JSON
      String jsonString;
      serializeJson(doc, jsonString);

      // Enviar POST
      Serial.println("📤 Enviando datos al servidor...");
      Serial.println(jsonString);

      int httpCode = http.POST(jsonString);

      // Procesar respuesta
      if (httpCode > 0) {
        String payload = http.getString();
        Serial.printf("✅ Respuesta del servidor [%d]: %s\n", httpCode, payload.c_str());

        if (httpCode == 201) {
          Serial.println("✅ Datos registrados exitosamente");
        }
      } else {
        Serial.printf("❌ Error en HTTP: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    } else {
      Serial.println("❌ WiFi desconectado, reconectando...");
      connectWiFi();
    }

    lastSendTime = currentTime;
  }
}

/**
 * Setup inicial
 */
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("=================================");
  Serial.println("🚰 ESP32 Flow Sensor - REST API");
  Serial.println("=================================");

  // Configurar pin del sensor
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);

  // Configurar interrupción
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulseCounter, FALLING);

  // Conectar WiFi
  connectWiFi();

  // Configurar NTP para timestamps
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
  Serial.println("⏰ Sincronizando tiempo con NTP...");
  delay(2000);

  // Inicializar contadores
  lastSampleTime = millis();
  lastSendTime = millis();

  Serial.println("✅ Sistema iniciado");
  Serial.println("=================================");
}

/**
 * Loop principal
 */
void loop() {
  // Calcular flujo continuamente
  calculateFlowRate();

  // Enviar datos al servidor periódicamente
  sendDataToServer();

  // Pequeño delay para no saturar el CPU
  delay(10);
}

/**
 * NOTAS DE USO:
 *
 * 1. Actualizar credenciales WiFi en WIFI_SSID y WIFI_PASSWORD
 *
 * 2. Actualizar SERVER_URL con la IP y puerto de tu servidor:
 *    http://192.168.1.100:8000/api/v1/sensor/readings
 *
 * 3. Ajustar CALIBRATION_FACTOR según tu sensor:
 *    - YF-S201: ~7.5 pulsos/litro
 *    - YF-B1: ~90 pulsos/litro
 *    - Otros: consultar datasheet
 *
 * 4. Ajustar GMT_OFFSET_SEC según tu zona horaria:
 *    - GMT-6 (México): -21600
 *    - GMT-5 (Colombia): -18000
 *    - GMT-3 (Argentina): -10800
 *
 * 5. El servidor debe estar ejecutándose en:
 *    python main.py
 *
 * 6. Endpoint REST disponible en:
 *    POST http://tu-servidor:8000/api/v1/sensor/readings
 *
 * 7. Formato JSON esperado:
 *    {
 *      "device_id": "flowsensor_001",
 *      "timestamp": "2025-11-17T03:00:00Z",
 *      "flow_rate": 1.25,
 *      "pulse_count": 75,
 *      "unit": "L/min"
 *    }
 */
