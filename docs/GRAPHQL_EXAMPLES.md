# Ejemplos de GraphQL API

Este documento contiene ejemplos prácticos para usar la API GraphQL del sistema de gestión de dispensador de agua.

## Configuración Inicial

Antes de usar la API, asegúrate de que el servidor esté corriendo:

```bash
python main.py
```

Accede a GraphiQL en: `http://localhost:8000/graphql`

## Escenario 1: Configuración Inicial del Sistema

### 1.1 Crear una bomba

Primero, necesitas inicializar una bomba en el sistema:

```graphql
mutation {
  # Nota: Esto requeriría un endpoint adicional de inicialización
  # Por ahora, la bomba se crea manualmente en la base de datos
}
```

## Escenario 2: Flujo de Trabajo ESP32 → Servidor

### 2.1 ESP32 envía lectura de flujo

```graphql
mutation {
  recordFlowReading(input: {
    deviceId: "ESP32_001"
    flowRate: 12.5
    totalVolume: 150.75
    temperature: 23.2
    pressure: 2.0
  }) {
    id
    deviceId
    flowRate
    totalVolume
    timestamp
  }
}
```

**Respuesta esperada:**
```json
{
  "data": {
    "recordFlowReading": {
      "id": 1,
      "deviceId": "ESP32_001",
      "flowRate": 12.5,
      "totalVolume": 150.75,
      "timestamp": "2024-10-30T18:30:00"
    }
  }
}
```

### 2.2 Consultar última lectura

```graphql
query {
  latestFlowReading(deviceId: "ESP32_001") {
    id
    flowRate
    totalVolume
    timestamp
    temperature
    pressure
  }
}
```

## Escenario 3: Gestión de Llenados

### 3.1 Iniciar un llenado de 20 litros

```graphql
mutation {
  startFilling(input: {
    deviceId: "ESP32_001"
    targetVolume: 20.0
    initialVolume: 150.75
  }) {
    id
    deviceId
    targetVolume
    initialVolume
    status
    startTime
  }
}
```

### 3.2 Consultar llenado activo

```graphql
query {
  activeFilling(deviceId: "ESP32_001") {
    id
    startTime
    targetVolume
    initialVolume
    status
  }
}
```

### 3.3 Completar el llenado

```graphql
mutation {
  completeFilling(input: {
    fillingId: 1
    finalVolume: 170.5
  }) {
    id
    status
    actualVolume
    efficiency
    durationSeconds
    avgFlowRate
  }
}
```

**Respuesta esperada:**
```json
{
  "data": {
    "completeFilling": {
      "id": 1,
      "status": "completed",
      "actualVolume": 19.75,
      "efficiency": 98.75,
      "durationSeconds": 45.2,
      "avgFlowRate": 26.22
    }
  }
}
```

### 3.4 Ver historial de llenados

```graphql
query {
  fillings(deviceId: "ESP32_001", limit: 10) {
    id
    startTime
    endTime
    actualVolume
    targetVolume
    efficiency
    status
    durationSeconds
  }
}
```

## Escenario 4: Control de Bomba

### 4.1 Actualizar nivel de la bomba

```graphql
mutation {
  updatePumpLevel(input: {
    deviceId: "ESP32_001"
    currentLevel: 75.5
  }) {
    id
    currentLevel
    levelPercentage
    shouldStop
    shouldWarn
    status
  }
}
```

### 4.2 Encender la bomba

```graphql
mutation {
  controlPump(input: {
    deviceId: "ESP32_001"
    action: "on"
  }) {
    id
    status
    currentLevel
    levelPercentage
  }
}
```

### 4.3 Apagar la bomba

```graphql
mutation {
  controlPump(input: {
    deviceId: "ESP32_001"
    action: "off"
  }) {
    id
    status
    currentLevel
  }
}
```

### 4.4 Consultar estado de la bomba

```graphql
query {
  pumpStatus(deviceId: "ESP32_001") {
    id
    deviceId
    status
    currentLevel
    maxLevel
    levelPercentage
    thresholdStop
    thresholdWarning
    shouldStop
    shouldWarn
    lastUpdated
  }
}
```

## Escenario 5: Métricas y Análisis

### 5.1 Métricas de flujo del último mes

```graphql
query {
  flowMetrics(
    deviceId: "ESP32_001"
    startDate: "2024-10-01T00:00:00"
    endDate: "2024-10-31T23:59:59"
  ) {
    avgFlowRate
    minFlowRate
    maxFlowRate
    totalVolume
    efficiency
    periodStart
    periodEnd
  }
}
```

### 5.2 Métricas de llenados

```graphql
query {
  fillingMetrics(
    deviceId: "ESP32_001"
    startDate: "2024-10-01T00:00:00"
    endDate: "2024-10-31T23:59:59"
  ) {
    totalFillings
    completedFillings
    cancelledFillings
    avgDurationSeconds
    avgVolume
    avgEfficiency
    completionRate
    totalVolumeDispensed
  }
}
```

### 5.3 Métricas de negocio con ingresos

```graphql
query {
  businessMetrics(
    deviceId: "ESP32_001"
    startDate: "2024-10-01T00:00:00"
    endDate: "2024-10-31T23:59:59"
    pricePerLiter: 2.5
  ) {
    revenue
    peakHours
    avgFillingsPerDay
    waterEfficiency
  }
}
```

**Respuesta esperada:**
```json
{
  "data": {
    "businessMetrics": {
      "revenue": 1250.50,
      "peakHours": [14, 18, 20],
      "avgFillingsPerDay": 15.3,
      "waterEfficiency": 96.8
    }
  }
}
```

## Escenario 6: Consultas Combinadas

### 6.1 Dashboard completo

```graphql
query DashboardData {
  # Estado actual
  latestReading: latestFlowReading(deviceId: "ESP32_001") {
    flowRate
    totalVolume
    timestamp
  }

  # Bomba
  pump: pumpStatus(deviceId: "ESP32_001") {
    status
    levelPercentage
    shouldWarn
  }

  # Llenado activo
  active: activeFilling(deviceId: "ESP32_001") {
    id
    targetVolume
    initialVolume
    startTime
  }

  # Métricas del día
  todayMetrics: fillingMetrics(
    deviceId: "ESP32_001"
    startDate: "2024-10-30T00:00:00"
    endDate: "2024-10-30T23:59:59"
  ) {
    totalFillings
    completedFillings
    totalVolumeDispensed
  }
}
```

## Escenario 7: Simulación Completa de un Día

### Paso 1: Inicio del día - Consultar estado

```graphql
query {
  pumpStatus(deviceId: "ESP32_001") {
    status
    currentLevel
  }
  latestFlowReading(deviceId: "ESP32_001") {
    totalVolume
  }
}
```

### Paso 2: Cliente llega - Iniciar llenado

```graphql
mutation {
  startFilling(input: {
    deviceId: "ESP32_001"
    targetVolume: 20.0
    initialVolume: 100.0
  }) {
    id
    targetVolume
  }
}
```

### Paso 3: Durante el llenado - ESP32 envía datos

```graphql
mutation {
  recordFlowReading(input: {
    deviceId: "ESP32_001"
    flowRate: 15.2
    totalVolume: 105.3
  }) {
    id
    flowRate
  }
}
```

### Paso 4: Finalizar llenado

```graphql
mutation {
  completeFilling(input: {
    fillingId: 1
    finalVolume: 120.0
  }) {
    efficiency
    actualVolume
  }
}
```

### Paso 5: Actualizar nivel de bomba

```graphql
mutation {
  updatePumpLevel(input: {
    deviceId: "ESP32_001"
    currentLevel: 85.0
  }) {
    shouldWarn
    shouldStop
  }
}
```

### Paso 6: Fin del día - Ver métricas

```graphql
query {
  businessMetrics(
    deviceId: "ESP32_001"
    startDate: "2024-10-30T00:00:00"
    endDate: "2024-10-30T23:59:59"
    pricePerLiter: 2.0
  ) {
    revenue
    peakHours
    avgFillingsPerDay
  }
}
```

## Variables en GraphQL

Puedes usar variables para hacer tus queries más reutilizables:

```graphql
query GetFlowMetrics($deviceId: String!, $start: DateTime!, $end: DateTime!) {
  flowMetrics(
    deviceId: $deviceId
    startDate: $start
    endDate: $end
  ) {
    avgFlowRate
    totalVolume
    efficiency
  }
}
```

**Variables:**
```json
{
  "deviceId": "ESP32_001",
  "start": "2024-10-01T00:00:00",
  "end": "2024-10-31T23:59:59"
}
```

## Manejo de Errores

### Error: Llenado ya en progreso

```graphql
mutation {
  startFilling(input: {
    deviceId: "ESP32_001"
    targetVolume: 20.0
    initialVolume: 100.0
  }) {
    id
  }
}
```

**Respuesta de error:**
```json
{
  "errors": [
    {
      "message": "Ya hay un llenado en progreso",
      "path": ["startFilling"]
    }
  ]
}
```

### Error: Bomba en nivel máximo

```graphql
mutation {
  controlPump(input: {
    deviceId: "ESP32_001"
    action: "on"
  }) {
    status
  }
}
```

**Respuesta de error:**
```json
{
  "errors": [
    {
      "message": "No se puede encender la bomba: nivel máximo alcanzado",
      "path": ["controlPump"]
    }
  ]
}
```

## Tips y Mejores Prácticas

1. **Usa aliases** para múltiples queries del mismo tipo:
```graphql
query {
  today: fillingMetrics(deviceId: "ESP32_001", startDate: "2024-10-30T00:00:00", endDate: "2024-10-30T23:59:59") {
    totalFillings
  }
  yesterday: fillingMetrics(deviceId: "ESP32_001", startDate: "2024-10-29T00:00:00", endDate: "2024-10-29T23:59:59") {
    totalFillings
  }
}
```

2. **Usa fragmentos** para evitar repetición:
```graphql
fragment FillingDetails on Filling {
  id
  actualVolume
  efficiency
  status
}

query {
  fillings(deviceId: "ESP32_001") {
    ...FillingDetails
  }
}
```

3. **Solicita solo los campos necesarios** para optimizar performance.

4. **Usa variables** en lugar de hardcodear valores.
