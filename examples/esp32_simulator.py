"""
Simulador de ESP32 para testing
Envía datos simulados al servidor GraphQL
"""
import asyncio
import random
import httpx
from datetime import datetime


class ESP32Simulator:
    """Simula un ESP32 enviando datos del flujómetro"""

    def __init__(self, server_url: str, device_id: str):
        self.server_url = server_url
        self.device_id = device_id
        self.total_volume = 0.0
        self.is_running = False

    def simulate_flow_rate(self) -> float:
        """Simula un flujo de agua realista (10-20 L/min con variación)"""
        base_flow = 15.0
        variation = random.uniform(-3.0, 3.0)
        return max(0, base_flow + variation)

    def simulate_temperature(self) -> float:
        """Simula temperatura del agua (20-25°C)"""
        return random.uniform(20.0, 25.0)

    def simulate_pressure(self) -> float:
        """Simula presión del agua (1.5-2.5 PSI)"""
        return random.uniform(1.5, 2.5)

    async def send_flow_reading(self, flow_rate: float, temperature: float, pressure: float):
        """Envía una lectura de flujo al servidor"""
        mutation = """
        mutation RecordFlowReading($input: CreateFlowReadingInput!) {
            recordFlowReading(input: $input) {
                id
                flowRate
                totalVolume
                timestamp
            }
        }
        """

        variables = {
            "input": {
                "deviceId": self.device_id,
                "flowRate": round(flow_rate, 2),
                "totalVolume": round(self.total_volume, 2),
                "temperature": round(temperature, 2),
                "pressure": round(pressure, 2),
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.server_url,
                    json={"query": mutation, "variables": variables},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        print(f"❌ GraphQL Error: {data['errors']}")
                    else:
                        reading = data["data"]["recordFlowReading"]
                        print(
                            f"✓ Lectura enviada - ID: {reading['id']}, "
                            f"Flujo: {reading['flowRate']} L/min, "
                            f"Total: {reading['totalVolume']} L"
                        )
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error enviando datos: {e}")

    async def start_filling(self, target_volume: float):
        """Inicia un ciclo de llenado"""
        mutation = """
        mutation StartFilling($input: StartFillingInput!) {
            startFilling(input: $input) {
                id
                deviceId
                targetVolume
                status
            }
        }
        """

        variables = {
            "input": {
                "deviceId": self.device_id,
                "targetVolume": target_volume,
                "initialVolume": self.total_volume,
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.server_url,
                    json={"query": mutation, "variables": variables},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        print(f"❌ Error iniciando llenado: {data['errors']}")
                        return None
                    filling = data["data"]["startFilling"]
                    print(f"🚰 Llenado iniciado - ID: {filling['id']}, Target: {filling['targetVolume']}L")
                    return filling["id"]
        except Exception as e:
            print(f"❌ Error: {e}")
        return None

    async def complete_filling(self, filling_id: int):
        """Completa un ciclo de llenado"""
        mutation = """
        mutation CompleteFilling($input: CompleteFillingInput!) {
            completeFilling(input: $input) {
                id
                actualVolume
                efficiency
                durationSeconds
            }
        }
        """

        variables = {
            "input": {
                "fillingId": filling_id,
                "finalVolume": self.total_volume,
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.server_url,
                    json={"query": mutation, "variables": variables},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        print(f"❌ Error completando llenado: {data['errors']}")
                        return
                    filling = data["data"]["completeFilling"]
                    print(
                        f"✅ Llenado completado - Volumen: {filling['actualVolume']}L, "
                        f"Eficiencia: {filling['efficiency']:.1f}%, "
                        f"Duración: {filling['durationSeconds']:.1f}s"
                    )
        except Exception as e:
            print(f"❌ Error: {e}")

    async def simulate_filling_cycle(self, target_volume: float = 20.0):
        """Simula un ciclo completo de llenado"""
        print(f"\n{'='*60}")
        print(f"Iniciando ciclo de llenado de {target_volume}L")
        print(f"{'='*60}")

        # Iniciar llenado
        filling_id = await self.start_filling(target_volume)
        if not filling_id:
            return

        # Simular llenado (1 segundo = ~0.25 litros)
        initial_volume = self.total_volume
        filling_duration = target_volume / 15.0 * 60  # segundos aproximados

        for _ in range(int(filling_duration)):
            flow_rate = self.simulate_flow_rate()
            temperature = self.simulate_temperature()
            pressure = self.simulate_pressure()

            # Incrementar volumen (L/min convertido a L/segundo)
            self.total_volume += flow_rate / 60.0

            await self.send_flow_reading(flow_rate, temperature, pressure)
            await asyncio.sleep(1)

            # Verificar si alcanzamos el objetivo
            if self.total_volume >= initial_volume + target_volume:
                break

        # Completar llenado
        await self.complete_filling(filling_id)
        print(f"{'='*60}\n")

    async def run_continuous(self, interval: int = 5):
        """Ejecuta el simulador continuamente"""
        print(f"\n{'='*60}")
        print("ESP32 Simulator - Modo Continuo")
        print(f"{'='*60}")
        print(f"Servidor: {self.server_url}")
        print(f"Device ID: {self.device_id}")
        print(f"Intervalo: {interval} segundos")
        print(f"{'='*60}\n")

        self.is_running = True

        try:
            while self.is_running:
                flow_rate = self.simulate_flow_rate()
                temperature = self.simulate_temperature()
                pressure = self.simulate_pressure()

                # Incrementar volumen total
                self.total_volume += (flow_rate / 60.0) * interval

                await self.send_flow_reading(flow_rate, temperature, pressure)
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Simulador detenido por el usuario")
            self.is_running = False


async def main():
    """Función principal"""
    # Configuración
    SERVER_URL = "http://localhost:8000/graphql"
    DEVICE_ID = "ESP32_001"

    simulator = ESP32Simulator(SERVER_URL, DEVICE_ID)

    print("\n¿Qué deseas hacer?")
    print("1. Simular un ciclo de llenado")
    print("2. Ejecutar en modo continuo")
    print("3. Simular múltiples llenados")

    choice = input("\nSelecciona una opción (1-3): ")

    if choice == "1":
        volume = float(input("Volumen objetivo (litros): ") or "20.0")
        await simulator.simulate_filling_cycle(volume)

    elif choice == "2":
        interval = int(input("Intervalo de envío (segundos): ") or "5")
        await simulator.run_continuous(interval)

    elif choice == "3":
        num_fillings = int(input("Número de llenados: ") or "3")
        for i in range(num_fillings):
            print(f"\n--- Llenado {i+1}/{num_fillings} ---")
            volume = random.uniform(15.0, 25.0)
            await simulator.simulate_filling_cycle(volume)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
