# Railway Deployment Guide

## 🚂 Despliegue en Railway con PostgreSQL

Esta guía te ayudará a desplegar el sistema de dispensador de agua en Railway con una base de datos PostgreSQL.

## Requisitos Previos

- Cuenta en [Railway](https://railway.app)
- Código en GitHub (recomendado) o deploy desde CLI
- Git configurado localmente

## 🚀 Paso a Paso

### 1. Crear Nuevo Proyecto en Railway

1. Ve a [railway.app](https://railway.app)
2. Click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a tu repositorio
5. Selecciona tu repositorio `Water_dispenser`

### 2. Agregar PostgreSQL

1. En tu proyecto de Railway, click en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente:
   - Base de datos PostgreSQL
   - Variable `DATABASE_URL` conectada a tu servicio
   - Credenciales seguras

### 3. Configurar Variables de Entorno

En tu servicio de la aplicación, ve a **"Variables"** y agrega:

#### Variables Requeridas

Railway ya configura automáticamente:
- ✅ `DATABASE_URL` - Conectado desde PostgreSQL
- ✅ `PORT` - Asignado por Railway

Agrega estas variables manualmente:

```env
# Servidor
HOST=0.0.0.0
DEBUG=False

# Notificaciones (opcional)
NOTIFICATION_SERVICE=console
FCM_SERVER_KEY=tu_key_aqui_si_usas_fcm

# Control de bomba
PUMP_CHECK_INTERVAL=5
PUMP_MAX_LEVEL=100.0
PUMP_THRESHOLD_STOP=95.0
PUMP_THRESHOLD_WARNING=80.0

# Métricas
PRICE_PER_LITER=2.0

# ESP32
ESP32_DEVICE_ID=flowsensor_001
```

### 4. Configurar Build

Railway detectará automáticamente el `Dockerfile` y usará la configuración en `railway.toml`:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python main.py"
restartPolicyType = "ON_FAILURE"
healthcheckPath = "/api/v1/health"
```

### 5. Deploy

Railway desplegará automáticamente cuando:
- Haces push a tu rama principal (main/master)
- Haces cambios en las variables de entorno
- Haces redeploy manual

**Deploy manual:**
1. Click en **"Deploy"** → **"Redeploy"**

### 6. Verificar Despliegue

Una vez desplegado, Railway te dará una URL pública:
```
https://tu-proyecto.up.railway.app
```

Verifica:
- ✅ Health check: `https://tu-proyecto.up.railway.app/api/v1/health`
- ✅ GraphQL: `https://tu-proyecto.up.railway.app/graphql`
- ✅ Docs: `https://tu-proyecto.up.railway.app/docs`

## 🔧 Configuración Avanzada

### Custom Domain

1. Ve a **"Settings"** → **"Domains"**
2. Click **"Add Domain"**
3. Sigue las instrucciones para configurar tu DNS

### CORS para Producción

Edita `src/infrastructure/graphql/server.py`:

```python
self.app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Escalar Recursos

En Railway, puedes ajustar:
- **Memory**: 512MB - 8GB
- **CPU**: Compartido o dedicado
- **Replicas**: 1-10 instancias

## 📊 Monitoreo

### Logs en Tiempo Real

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

O ver logs en el dashboard de Railway:
1. Click en tu servicio
2. Ve a la pestaña **"Logs"**

### Métricas

Railway proporciona:
- CPU usage
- Memory usage
- Request count
- Response times

## 🗄️ Base de Datos PostgreSQL

### Acceso a la Base de Datos

Railway proporciona variables:
- `DATABASE_URL` - URL completa de conexión
- `PGHOST` - Host
- `PGPORT` - Puerto (usualmente 5432)
- `PGUSER` - Usuario
- `PGPASSWORD` - Password
- `PGDATABASE` - Nombre de la base de datos

### Conectar desde Local

```bash
# Obtener URL de conexión
railway variables

# Conectar con psql
psql $DATABASE_URL

# O usar pgAdmin, DBeaver, etc.
```

### Migraciones

Ejecutar migraciones después del primer deploy:

```bash
# Opción 1: Railway CLI
railway run python scripts/migrate_add_pulse_fields.py

# Opción 2: Desde el dashboard
# Settings → Deploy Triggers → Add Migration Command
# Command: python scripts/migrate_add_pulse_fields.py
```

### Backup Automático

Railway hace backups automáticos de PostgreSQL:
- Retención: 7 días (plan free)
- Retención: 30 días (plan pro)

**Backup manual:**
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

## 🔐 Seguridad

### Secretos

Nunca subas a GitHub:
- ❌ `.env` con credenciales
- ❌ `FCM_SERVER_KEY`
- ❌ Passwords

Usa variables de entorno en Railway.

### HTTPS

Railway proporciona HTTPS automáticamente:
- ✅ Certificado SSL gratis
- ✅ Renovación automática
- ✅ HTTP → HTTPS redirect

### Rate Limiting (Recomendado)

Agrega rate limiting en producción:

```python
# requirements.txt
slowapi==0.1.9

# src/infrastructure/graphql/server.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/sensor/readings")
@limiter.limit("100/minute")
async def create_reading(...):
    ...
```

## 📱 Integración con ESP32

### Configurar URL en ESP32

Usa la URL de Railway en tu código Arduino:

```cpp
const char* SERVER_URL = "https://tu-proyecto.up.railway.app/api/v1/sensor/readings";
```

### HTTPS en ESP32

```cpp
#include <WiFiClientSecure.h>

WiFiClientSecure client;
client.setInsecure(); // Para desarrollo

// O usar certificado (producción)
client.setCACert(rootCACertificate);
```

### Testing

```bash
curl -X POST https://tu-proyecto.up.railway.app/api/v1/sensor/readings \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "flowsensor_001",
    "timestamp": "2025-11-17T03:00:00Z",
    "flow_rate": 1.25,
    "pulse_count": 75,
    "unit": "L/min"
  }'
```

## 💰 Costos

### Plan Free (Hobby)

- ✅ 500 horas/mes de ejecución
- ✅ 512MB RAM
- ✅ PostgreSQL incluido
- ✅ $5 de crédito mensual
- ❌ Sin custom domain

### Plan Pro ($20/mes)

- ✅ Ejecución ilimitada
- ✅ Hasta 8GB RAM
- ✅ Custom domains
- ✅ Más recursos de DB
- ✅ Priority support

**Estimación para este proyecto (Free):**
- API: ~100-150 horas/mes
- PostgreSQL: incluido
- **Total: $0** (dentro del free tier)

## 🔄 CI/CD Automático

Railway hace deploy automático cuando:

```bash
# 1. Haces push a main
git add .
git commit -m "Update sensor API"
git push origin main
# → Railway detecta cambio y despliega

# 2. Cambias variables de entorno
# → Railway reinicia con nuevas variables

# 3. Cambias configuración de DB
# → Railway reconfigura conexión
```

### Deshabilitar Auto-Deploy

Si quieres control manual:
1. Settings → Deployments
2. Deshabilita "Auto Deploy"

## 🐛 Troubleshooting

### Error: "Application failed to start"

```bash
# Ver logs
railway logs

# Verificar build
railway logs --deployment

# Verificar variables
railway variables
```

**Soluciones comunes:**
- Verificar `DATABASE_URL` está configurada
- Verificar `PORT` no está hardcodeado
- Verificar dependencias en `requirements.txt`

### Error: "Health check failed"

```bash
# Verificar endpoint
curl https://tu-proyecto.up.railway.app/api/v1/health

# Verificar logs
railway logs | grep health
```

**Soluciones:**
- Verificar que el servidor escucha en `0.0.0.0`
- Verificar que usa el `PORT` de Railway
- Aumentar `healthcheckTimeout` en `railway.toml`

### Error: "Database connection failed"

```bash
# Verificar conexión
railway run python -c "
from src.infrastructure.persistence.database import DatabaseManager
import asyncio
asyncio.run(DatabaseManager('$DATABASE_URL').create_tables())
"
```

**Soluciones:**
- Verificar PostgreSQL está corriendo
- Verificar `DATABASE_URL` es correcta
- Verificar formato: `postgresql+asyncpg://...`

### Error: "Out of memory"

Opciones:
1. Optimizar código (reducir uso de memoria)
2. Aumentar límite de memoria (Settings → Resources)
3. Upgrade a plan Pro

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [PostgreSQL en Railway](https://docs.railway.app/databases/postgresql)
- [Variables de Entorno](https://docs.railway.app/develop/variables)
- [Custom Domains](https://docs.railway.app/deploy/deployments#custom-domains)

## 🎯 Checklist de Despliegue

- [ ] Código subido a GitHub
- [ ] Proyecto creado en Railway
- [ ] PostgreSQL agregado
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso
- [ ] Health check pasando
- [ ] GraphQL funcionando
- [ ] REST API funcionando
- [ ] ESP32 conectando correctamente
- [ ] Logs monitoreados
- [ ] Backups configurados

## 🚀 Próximos Pasos

1. **Configurar dominio custom**
2. **Agregar monitoring (Sentry, LogRocket)**
3. **Implementar rate limiting**
4. **Configurar alertas**
5. **Optimizar performance**
6. **Agregar tests automáticos**

---

**¡Tu API está lista para producción en Railway!** 🎉
