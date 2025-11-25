# ============================================
# Dockerfile for Water Dispenser
# Optimized for Railway with UV
# ============================================

FROM python:3.13-slim

# Metadata
LABEL maintainer="Water Dispenser Team"
LABEL description="Water Dispenser Management System - GraphQL + REST API"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    HOST=0.0.0.0 \
    PORT=8000

# Instalar UV (ultra-fast Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Crear usuario no-root para mayor seguridad
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Establecer directorio de trabajo
WORKDIR /app


# Copiar archivos de dependencias primero (mejor cache)
COPY --chown=appuser:appuser requirements.txt pyproject.toml ./

# Instalar dependencias usando UV (mucho más rápido que pip)
RUN uv pip install --system --no-cache -r requirements.txt

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Comando por defecto
CMD ["python", "main.py"]
