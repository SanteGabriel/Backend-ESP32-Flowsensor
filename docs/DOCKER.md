# Docker Deployment Guide

## Introducción

Este proyecto incluye configuración completa de Docker con:

- ✅ **Dockerfile multi-stage** optimizado
- ✅ **UV** para instalación ultra-rápida de dependencias
- ✅ **Docker Compose** para orquestación
- ✅ **SQLite** (desarrollo) y **PostgreSQL** (producción)
- ✅ **Health checks** automáticos
- ✅ **Usuario no-root** para seguridad
- ✅ **Volúmenes persistentes** para datos

## Quick Start

### 1. Construcción y Ejecución

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f water-dispenser

# Verificar estado
docker-compose ps
```

La API estará disponible en:
- **REST API:** http://localhost:8000/api/v1
- **GraphQL:** http://localhost:8000/graphql
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/v1/health

### 2. Detener Servicios

```bash
# Detener sin borrar volúmenes
docker-compose down

# Detener y borrar TODO (¡CUIDADO!)
docker-compose down -v
```

## Estructura de Archivos Docker

```
.
├── Dockerfile              # Imagen multi-stage con UV
├── docker-compose.yml      # Orquestación de servicios
├── .dockerignore          # Archivos excluidos del build
└── docs/
    └── DOCKER.md          # Esta documentación
```

## Dockerfile

### Características

**Stage 1: Builder**
- Python 3.13 slim
- UV para instalación rápida
- Solo instala dependencias

**Stage 2: Runtime**
- Imagen final optimizada
- Solo runtime + código
- Usuario no-root
- Health checks

### Build Manual

```bash
# Construir imagen
docker build -t water-dispenser:latest .

# Ejecutar contenedor
docker run -d \
  --name water-dispenser \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=sqlite+aiosqlite:///./data/water_dispenser.db \
  water-dispenser:latest

# Ver logs
docker logs -f water-dispenser

# Detener
docker stop water-dispenser
docker rm water-dispenser
```

## Docker Compose

### Configuración SQLite (Default)

```yaml
# docker-compose.yml
services:
  water-dispenser:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/water_dispenser.db
```

**Usar:**
```bash
docker-compose up -d
```

### Configuración PostgreSQL (Producción)

Editar `docker-compose.yml` y descomentar la sección `postgres`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=water_dispenser
      - POSTGRES_PASSWORD=secure_password_123
      - POSTGRES_DB=water_dispenser
    volumes:
      - postgres-data:/var/lib/postgresql/data

  water-dispenser-postgres:
    build: .
    environment:
      - DATABASE_URL=postgresql+asyncpg://water_dispenser:secure_password_123@postgres:5432/water_dispenser
    depends_on:
      - postgres
```

**Usar:**
```bash
docker-compose up -d postgres water-dispenser-postgres
```

## Variables de Entorno

### Configuración Básica

```bash
# .env
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Base de datos
DATABASE_URL=sqlite+aiosqlite:///./data/water_dispenser.db

# Notificaciones
NOTIFICATION_SERVICE=console
FCM_SERVER_KEY=your_key_here

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

### Cargar .env en Docker Compose

```yaml
services:
  water-dispenser:
    env_file:
      - .env
```

## Volúmenes Persistentes

### SQLite

```yaml
volumes:
  - ./data:/app/data  # Base de datos SQLite
  - ./logs:/app/logs  # Logs (opcional)
```

Los datos se guardan en `./data/water_dispenser.db`

### PostgreSQL

```yaml
volumes:
  postgres-data:
    driver: local
```

Los datos se guardan en un volumen Docker

**Backup PostgreSQL:**
```bash
docker-compose exec postgres pg_dump -U water_dispenser water_dispenser > backup.sql
```

**Restore PostgreSQL:**
```bash
docker-compose exec -T postgres psql -U water_dispenser water_dispenser < backup.sql
```

## Comandos Útiles

### Gestión de Servicios

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f water-dispenser

# Reiniciar servicio
docker-compose restart water-dispenser

# Reconstruir imagen
docker-compose build --no-cache

# Actualizar servicios
docker-compose up -d --build
```

### Ejecutar Comandos en el Contenedor

```bash
# Acceder al shell
docker-compose exec water-dispenser /bin/bash

# Ejecutar migraciones
docker-compose exec water-dispenser python scripts/migrate_add_pulse_fields.py

# Inicializar base de datos
docker-compose exec water-dispenser python scripts/init_database.py

# Ver logs Python
docker-compose exec water-dispenser python -c "import sys; print(sys.version)"
```

### Gestión de Imágenes

```bash
# Listar imágenes
docker images

# Eliminar imagen
docker rmi water-dispenser:latest

# Limpiar imágenes no usadas
docker image prune -a

# Ver espacio usado
docker system df
```

### Debugging

```bash
# Ver procesos en contenedor
docker-compose exec water-dispenser ps aux

# Ver variables de entorno
docker-compose exec water-dispenser env

# Probar conectividad
docker-compose exec water-dispenser ping postgres

# Ver contenido de un archivo
docker-compose exec water-dispenser cat /app/main.py
```

## Health Checks

### Configuración

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1
```

### Verificar Estado

```bash
# Ver estado de health check
docker inspect water-dispenser-api | jq '.[0].State.Health'

# Ver logs de health check
docker inspect water-dispenser-api | jq '.[0].State.Health.Log'
```

## Optimizaciones

### Caché de Capas

El Dockerfile usa multi-stage build y copia dependencias primero:

```dockerfile
# ✅ Bueno: Dependencias se cachean
COPY pyproject.toml requirements.txt ./
RUN uv pip install --system -r requirements.txt
COPY . .

# ❌ Malo: Todo se reconstruye
COPY . .
RUN uv pip install --system -r requirements.txt
```

### Tamaño de Imagen

```bash
# Ver tamaño de imagen
docker images water-dispenser

# Optimización actual: ~200MB
# - python:3.13-slim base
# - Multi-stage build
# - .dockerignore completo
# - No dev dependencies
```

### UV vs pip

**Instalación de dependencias:**
- `pip install`: ~60 segundos
- `uv pip install`: ~5 segundos ⚡

**10-12x más rápido!**

## Producción

### Configuración Recomendada

1. **Usar PostgreSQL**
```yaml
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
```

2. **Deshabilitar Debug**
```yaml
DEBUG=False
```

3. **Configurar CORS**
```python
# src/infrastructure/graphql/server.py
allow_origins=["https://tu-dominio.com"]
```

4. **Usar Secrets**
```bash
# NO hardcodear passwords
docker secret create db_password /path/to/password.txt
```

5. **Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name api.tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Swarm (Escalado)

```bash
# Inicializar swarm
docker swarm init

# Desplegar stack
docker stack deploy -c docker-compose.yml water-dispenser

# Escalar servicio
docker service scale water-dispenser_water-dispenser=3

# Ver servicios
docker service ls
```

### Kubernetes (Avanzado)

Crear manifiestos:
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: water-dispenser
spec:
  replicas: 3
  selector:
    matchLabels:
      app: water-dispenser
  template:
    metadata:
      labels:
        app: water-dispenser
    spec:
      containers:
      - name: water-dispenser
        image: water-dispenser:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://..."
```

## Troubleshooting

### Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs water-dispenser

# Ver últimas 100 líneas
docker-compose logs --tail=100 water-dispenser

# Ejecutar en primer plano
docker-compose up
```

### No puede conectar a PostgreSQL

```bash
# Verificar que postgres esté corriendo
docker-compose ps postgres

# Verificar health check
docker inspect water-dispenser-db | jq '.[0].State.Health'

# Probar conexión manualmente
docker-compose exec water-dispenser python -c "
import asyncio
from src.infrastructure.persistence.database import DatabaseManager
asyncio.run(DatabaseManager('postgresql://...').create_tables())
"
```

### Permisos de archivos

```bash
# Si hay problemas de permisos en ./data
sudo chown -R 1000:1000 ./data

# O cambiar en Dockerfile
USER root
RUN chown -R appuser:appuser /app/data
USER appuser
```

### Imagen muy grande

```bash
# Analizar capas
docker history water-dispenser:latest

# Usar .dockerignore
echo "*.db" >> .dockerignore
echo "node_modules/" >> .dockerignore

# Limpiar cache en build
docker build --no-cache -t water-dispenser:latest .
```

## Integración con ESP32

### Configurar IP del Servidor

En el código Arduino:
```cpp
const char* SERVER_URL = "http://192.168.1.100:8000/api/v1/sensor/readings";
```

Donde `192.168.1.100` es la IP del host que ejecuta Docker.

### Encontrar IP del Host

```bash
# Linux/Mac
ifconfig | grep "inet "

# Docker container
docker inspect water-dispenser-api | jq '.[0].NetworkSettings.IPAddress'

# Usar host.docker.internal (Mac/Windows)
SERVER_URL = "http://host.docker.internal:8000/api/v1/sensor/readings"
```

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build image
        run: docker build -t water-dispenser:latest .
      - name: Run tests
        run: docker run water-dispenser:latest pytest
```

## Referencias

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [UV Package Installer](https://github.com/astral-sh/uv)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
