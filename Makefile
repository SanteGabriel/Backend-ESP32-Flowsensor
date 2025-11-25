.PHONY: help install init run test clean format lint

help:
	@echo "Water Dispenser Management System - Comandos disponibles:"
	@echo ""
	@echo "  make install    - Instalar dependencias"
	@echo "  make init       - Inicializar base de datos"
	@echo "  make run        - Ejecutar servidor"
	@echo "  make simulate   - Ejecutar simulador ESP32"
	@echo "  make test       - Ejecutar tests"
	@echo "  make format     - Formatear código con black"
	@echo "  make lint       - Revisar código con ruff"
	@echo "  make clean      - Limpiar archivos temporales"
	@echo ""

install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt
	@echo "✓ Dependencias instaladas"

init:
	@echo "Inicializando base de datos..."
	python scripts/init_database.py
	@echo "✓ Base de datos inicializada"

run:
	@echo "Iniciando servidor..."
	python main.py

simulate:
	@echo "Iniciando simulador ESP32..."
	python examples/esp32_simulator.py

test:
	@echo "Ejecutando tests..."
	pytest tests/ -v

test-coverage:
	@echo "Ejecutando tests con cobertura..."
	pytest tests/ --cov=src --cov-report=html
	@echo "✓ Reporte en htmlcov/index.html"

format:
	@echo "Formateando código..."
	black src/ scripts/ examples/
	@echo "✓ Código formateado"

lint:
	@echo "Revisando código..."
	ruff check src/
	@echo "✓ Revisión completada"

type-check:
	@echo "Verificando tipos..."
	mypy src/
	@echo "✓ Tipos verificados"

clean:
	@echo "Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
	@echo "✓ Limpieza completada"

clean-db:
	@echo "Limpiando base de datos..."
	rm -f water_dispenser.db
	@echo "✓ Base de datos eliminada"

reset: clean-db init
	@echo "✓ Sistema reiniciado"

dev: install init
	@echo "✓ Ambiente de desarrollo configurado"

all: install init run
