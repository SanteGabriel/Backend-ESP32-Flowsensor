# Docker Hub + Railway Deployment

## 🐳 Despliegue usando Docker Hub

Esta guía explica cómo subir tu imagen a Docker Hub y desplegarla en Railway desde ahí.

## 📋 Requisitos

- Cuenta en [Docker Hub](https://hub.docker.com)
- Cuenta en [Railway](https://railway.app)
- Repositorio en GitHub
- Docker instalado localmente

## 🚀 Opción 1: Manual (Testing)

### 1. Build Local

```bash
# Build de la imagen
docker build -t tuusuario/water-dispenser:latest .

# Test local
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite+aiosqlite:///./data/water_dispenser.db \
  tuusuario/water-dispenser:latest

# Verificar
curl http://localhost:8000/api/v1/health
```

### 2. Push a Docker Hub

```bash
# Login en Docker Hub
docker login

# Push de la imagen
docker push tuusuario/water-dispenser:latest

# Verificar en https://hub.docker.com/r/tuusuario/water-dispenser
```

### 3. Deploy en Railway

**Opción A: Desde Dashboard**
1. Crear proyecto en Railway
2. Click **"+ New"** → **"Empty Service"**
3. Settings → **"Deploy from Docker Image"**
4. Imagen: `tuusuario/water-dispenser:latest`
5. Agregar PostgreSQL
6. Configurar variables de entorno

**Opción B: Desde CLI**
```bash
railway login
railway init
railway up --service tuusuario/water-dispenser:latest
```

## 🤖 Opción 2: Automatizado (CI/CD con GitHub Actions)

### 1. Configurar Secretos en GitHub

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions**

Agrega estos secretos:

| Secret | Valor |
|--------|-------|
| `DOCKER_USERNAME` | Tu usuario de Docker Hub |
| `DOCKER_PASSWORD` | Tu password o [Access Token](https://hub.docker.com/settings/security) |

### 2. Workflow de GitHub Actions

Ya está configurado en [`.github/workflows/docker-publish.yml`](../.github/workflows/docker-publish.yml)

**Actualizar nombre de imagen:**
```yaml
env:
  IMAGE_NAME: tuusuario/water-dispenser  # ← Cambiar aquí
```

### 3. Cómo Funciona

```mermaid
graph LR
    A[Push a main] --> B[GitHub Actions]
    B --> C[Build con UV]
    C --> D[Push a Docker Hub]
    D --> E[Railway detecta]
    E --> F[Deploy automático]
```

**Proceso automático:**
1. Haces push a `main` o `master`
2. GitHub Actions ejecuta
3. Build de imagen con UV (rápido)
4. Push a Docker Hub con tags:
   - `latest` (última versión)
   - `main` (rama main)
   - `v1.0.0` (si haces release)
5. Railway puede auto-deploy (opcional)

### 4. Tags Automáticos

El workflow crea tags automáticamente:

```bash
# Push a main
git push origin main
# → tuusuario/water-dispenser:latest
# → tuusuario/water-dispenser:main

# Crear release
git tag v1.0.0
git push origin v1.0.0
# → tuusuario/water-dispenser:v1.0.0
# → tuusuario/water-dispenser:1.0
# → tuusuario/water-dispenser:1
# → tuusuario/water-dispenser:latest
```

## 🔧 Configurar Railway con Docker Hub

### Método 1: Variables de Entorno

En Railway, Settings → Variables:

```env
# Railway usa la imagen de Docker Hub
RAILWAY_DOCKERFILE_PATH=Dockerfile
```

### Método 2: Railway CLI

```bash
railway login

# Link proyecto existente
railway link

# Deploy desde Docker Hub
railway up docker://tuusuario/water-dispenser:latest

# Con variables
railway run --service tuusuario/water-dispenser:latest \
  -e DATABASE_URL=$DATABASE_URL \
  -e PORT=8000
```

### Método 3: railway.json

Crear `railway.json`:
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "image": "tuusuario/water-dispenser:latest",
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 📊 Versioning

### Semantic Versioning

```bash
# Desarrollo
git push origin main
# → latest, main

# Release candidato
git tag v1.0.0-rc.1
git push origin v1.0.0-rc.1
# → v1.0.0-rc.1

# Release estable
git tag v1.0.0
git push origin v1.0.0
# → v1.0.0, 1.0, 1, latest

# Hotfix
git tag v1.0.1
git push origin v1.0.1
# → v1.0.1, 1.0, 1, latest
```

### Pinning de Versión

En Railway, usar versión específica:

```bash
# Producción: usar versión específica
railway up docker://tuusuario/water-dispenser:v1.0.0

# Staging: usar latest
railway up docker://tuusuario/water-dispenser:latest
```

## 🔐 Seguridad

### Access Token (Recomendado)

En lugar de password, usa Access Token:

1. Docker Hub → **Account Settings** → **Security**
2. **New Access Token**
3. Nombre: "GitHub Actions"
4. Permisos: Read, Write, Delete
5. Copiar token
6. GitHub Secrets → `DOCKER_PASSWORD` = token

### Private Repository

```bash
# Hacer repo privado
# Docker Hub → Repository → Settings → Private

# Railway necesitará credenciales
railway variables set DOCKER_USERNAME=tuusuario
railway variables set DOCKER_PASSWORD=tu_token
```

## 💰 Costos

### Docker Hub

**Plan Free:**
- ✅ Repos públicos ilimitados
- ✅ 1 repo privado
- ✅ 200 pulls/6 horas
- ✅ Gratis

**Plan Pro ($5/mes):**
- ✅ Repos privados ilimitados
- ✅ 5000 pulls/day
- ✅ Parallel builds

### Railway

Igual que antes:
- **Free:** 500 hrs/mes
- **Pro:** $20/mes ilimitado

**Usando Docker Hub no cambia costos de Railway**

## 🚀 Multi-Platform Builds

El workflow soporta múltiples arquitecturas:

```yaml
platforms: linux/amd64,linux/arm64
```

**Ventajas:**
- ✅ x86_64 (Intel/AMD)
- ✅ ARM64 (Apple Silicon, Raspberry Pi)
- ✅ Compatible con Railway
- ✅ Compatible con local

## 📈 Optimizaciones

### Cache de Layers

```yaml
cache-from: type=registry,ref=tuusuario/water-dispenser:buildcache
cache-to: type=registry,ref=tuusuario/water-dispenser:buildcache,mode=max
```

**Beneficios:**
- 🚀 Builds más rápidos (usa cache)
- 💾 Menos data transfer
- ⚡ CI/CD más eficiente

### Tamaño de Imagen

```bash
# Verificar tamaño
docker images tuusuario/water-dispenser

# Imagen actual: ~200MB
# - Multi-stage build
# - python:3.13-slim base
# - UV dependencies
```

## 🔄 CI/CD Workflow

```bash
# 1. Desarrollo local
git checkout -b feature/new-sensor
# ... hacer cambios ...
git commit -m "Add new sensor support"
git push origin feature/new-sensor

# 2. Pull Request
# → GitHub Actions builds pero NO push a Docker Hub

# 3. Merge a main
git checkout main
git pull origin main
# → GitHub Actions builds Y push a Docker Hub
# → Railway auto-deploy (si configurado)

# 4. Release
git tag v1.1.0
git push origin v1.1.0
# → GitHub Actions crea tags múltiples
# → Railway puede usar v1.1.0 específico
```

## 🐛 Troubleshooting

### Error: "denied: requested access to the resource is denied"

```bash
# Verificar login
docker logout
docker login

# Verificar permisos del token
# Docker Hub → Security → Revisar permisos
```

### Error: "manifest unknown"

```bash
# Verificar que la imagen existe
docker pull tuusuario/water-dispenser:latest

# Verificar tags disponibles
# https://hub.docker.com/r/tuusuario/water-dispenser/tags
```

### Error: GitHub Actions falla

```bash
# Verificar secretos
# GitHub → Settings → Secrets → Verificar:
# - DOCKER_USERNAME
# - DOCKER_PASSWORD

# Ver logs detallados
# GitHub → Actions → Click en workflow → Ver error
```

### Railway no puede pull imagen

```bash
# Si repo es privado, agregar credenciales
railway variables set DOCKER_USERNAME=tu_usuario
railway variables set DOCKER_PASSWORD=tu_token

# Verificar que la imagen es pública
# Docker Hub → Repository → Settings → Public
```

## 📚 Comandos Útiles

```bash
# Ver imágenes locales
docker images | grep water-dispenser

# Eliminar imagen local
docker rmi tuusuario/water-dispenser:latest

# Pull desde Docker Hub
docker pull tuusuario/water-dispenser:latest

# Ver historial de imagen
docker history tuusuario/water-dispenser:latest

# Inspeccionar imagen
docker inspect tuusuario/water-dispenser:latest

# Ver tags en Docker Hub (requires jq)
curl -s "https://hub.docker.com/v2/repositories/tuusuario/water-dispenser/tags" | jq

# Test local con PostgreSQL
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  tuusuario/water-dispenser:latest
```

## 🎯 Best Practices

1. **Usar tags específicos en producción**
   ```bash
   # ❌ Malo
   image: tuusuario/water-dispenser:latest

   # ✅ Bueno
   image: tuusuario/water-dispenser:v1.0.0
   ```

2. **Testear localmente antes de push**
   ```bash
   docker build -t test:local .
   docker run -p 8000:8000 test:local
   # Test endpoints
   # Si funciona, hacer push
   ```

3. **Usar semantic versioning**
   ```bash
   v1.0.0  # Major release
   v1.1.0  # Minor (nuevas features)
   v1.1.1  # Patch (bugfixes)
   ```

4. **Mantener README en Docker Hub**
   - Ir a Docker Hub → Repository → Description
   - Agregar instrucciones de uso
   - Agregar badges

## 🔗 Enlaces

- [Docker Hub](https://hub.docker.com)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Railway Docker Deploy](https://docs.railway.app/deploy/dockerfiles)
- [Docker Multi-platform](https://docs.docker.com/build/building/multi-platform/)

## ✅ Checklist

- [ ] Cuenta en Docker Hub creada
- [ ] Repositorio público/privado configurado
- [ ] Secretos de GitHub configurados
- [ ] Workflow actualizado con tu usuario
- [ ] Primera imagen subida a Docker Hub
- [ ] Railway conectado a Docker Hub
- [ ] Variables de entorno configuradas
- [ ] PostgreSQL agregado en Railway
- [ ] Health check funcionando
- [ ] ESP32 apuntando a Railway URL

---

**¡Tu pipeline CI/CD con Docker Hub está listo!** 🐳🚀
