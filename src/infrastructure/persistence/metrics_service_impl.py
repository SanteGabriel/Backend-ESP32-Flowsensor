import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from src.domain.services.metrics_service import MetricsService
from src.domain.value_objects.metrics import FlowMetrics, FillingMetrics, BusinessMetrics
from src.domain.repositories.flow_reading_repository import FlowReadingRepository
from src.domain.repositories.filling_repository import FillingRepository
from src.domain.entities.filling import FillingStatus


class MetricsServiceImpl(MetricsService):
    """Implementación del servicio de métricas usando pandas"""

    def __init__(
        self,
        flow_reading_repository: FlowReadingRepository,
        filling_repository: FillingRepository,
    ):
        self.flow_reading_repository = flow_reading_repository
        self.filling_repository = filling_repository

    async def calculate_flow_metrics(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> FlowMetrics:
        """Calcula métricas de flujo usando pandas"""
        readings = await self.flow_reading_repository.get_by_date_range(
            device_id, start_date, end_date
        )

        if not readings:
            return FlowMetrics(
                avg_flow_rate=0.0,
                min_flow_rate=0.0,
                max_flow_rate=0.0,
                total_volume=0.0,
                efficiency=0.0,
                period_start=start_date,
                period_end=end_date,
            )

        # Convertir a DataFrame
        df = pd.DataFrame(
            [
                {
                    "flow_rate": r.flow_rate,
                    "total_volume": r.total_volume,
                    "timestamp": r.timestamp,
                }
                for r in readings
            ]
        )

        # Calcular métricas
        avg_flow = df["flow_rate"].mean()
        min_flow = df["flow_rate"].min()
        max_flow = df["flow_rate"].max()
        total_vol = df["total_volume"].iloc[-1] if len(df) > 0 else 0.0

        # Calcular eficiencia (basado en estabilidad del flujo)
        flow_std = df["flow_rate"].std()
        efficiency = max(0, 100 - (flow_std / avg_flow * 100)) if avg_flow > 0 else 0

        return FlowMetrics(
            avg_flow_rate=float(avg_flow),
            min_flow_rate=float(min_flow),
            max_flow_rate=float(max_flow),
            total_volume=float(total_vol),
            efficiency=float(efficiency),
            period_start=start_date,
            period_end=end_date,
        )

    async def calculate_filling_metrics(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> FillingMetrics:
        """Calcula métricas de llenados usando pandas"""
        fillings = await self.filling_repository.get_by_date_range(
            device_id, start_date, end_date
        )

        if not fillings:
            return FillingMetrics(
                total_fillings=0,
                completed_fillings=0,
                cancelled_fillings=0,
                avg_duration_seconds=0.0,
                avg_volume=0.0,
                avg_efficiency=0.0,
                total_volume_dispensed=0.0,
                period_start=start_date,
                period_end=end_date,
            )

        # Convertir a DataFrame
        df = pd.DataFrame(
            [
                {
                    "status": f.status.value,
                    "duration_seconds": f.duration_seconds or 0,
                    "actual_volume": f.get_actual_volume(),
                    "efficiency": f.get_efficiency(),
                    "start_time": f.start_time,
                }
                for f in fillings
            ]
        )

        # Calcular métricas
        total = len(df)
        completed = len(df[df["status"] == FillingStatus.COMPLETED.value])
        cancelled = len(df[df["status"] == FillingStatus.CANCELLED.value])

        # Filtrar solo completados para promedios
        completed_df = df[df["status"] == FillingStatus.COMPLETED.value]

        avg_duration = (
            completed_df["duration_seconds"].mean() if len(completed_df) > 0 else 0.0
        )
        avg_volume = (
            completed_df["actual_volume"].mean() if len(completed_df) > 0 else 0.0
        )
        avg_efficiency = (
            completed_df["efficiency"].mean() if len(completed_df) > 0 else 0.0
        )
        total_volume = df["actual_volume"].sum()

        return FillingMetrics(
            total_fillings=total,
            completed_fillings=completed,
            cancelled_fillings=cancelled,
            avg_duration_seconds=float(avg_duration),
            avg_volume=float(avg_volume),
            avg_efficiency=float(avg_efficiency),
            total_volume_dispensed=float(total_volume),
            period_start=start_date,
            period_end=end_date,
        )

    async def calculate_business_metrics(
        self,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
        price_per_liter: float = 0.0,
    ) -> BusinessMetrics:
        """Calcula métricas de negocio usando pandas"""
        fillings = await self.filling_repository.get_by_date_range(
            device_id, start_date, end_date
        )

        if not fillings:
            return BusinessMetrics(
                revenue=0.0,
                fillings_by_hour={},
                fillings_by_day={},
                peak_hours=[],
                avg_fillings_per_day=0.0,
                water_efficiency=0.0,
            )

        # Convertir a DataFrame
        df = pd.DataFrame(
            [
                {
                    "start_time": f.start_time,
                    "actual_volume": f.get_actual_volume(),
                    "efficiency": f.get_efficiency(),
                }
                for f in fillings
            ]
        )

        # Agregar columnas de tiempo
        df["hour"] = pd.to_datetime(df["start_time"]).dt.hour
        df["date"] = pd.to_datetime(df["start_time"]).dt.date

        # Calcular ingresos
        total_volume = df["actual_volume"].sum()
        revenue = total_volume * price_per_liter

        # Llenados por hora
        fillings_by_hour = df.groupby("hour").size().to_dict()
        fillings_by_hour = {int(k): int(v) for k, v in fillings_by_hour.items()}

        # Llenados por día
        fillings_by_day = df.groupby("date").size().to_dict()
        fillings_by_day = {str(k): int(v) for k, v in fillings_by_day.items()}

        # Horas pico (top 3)
        peak_hours_series = df.groupby("hour").size().nlargest(3)
        peak_hours = [int(h) for h in peak_hours_series.index.tolist()]

        # Promedio de llenados por día
        num_days = (end_date - start_date).days + 1
        avg_fillings_per_day = len(df) / num_days if num_days > 0 else 0

        # Eficiencia promedio
        water_efficiency = df["efficiency"].mean()

        return BusinessMetrics(
            revenue=float(revenue),
            fillings_by_hour=fillings_by_hour,
            fillings_by_day=fillings_by_day,
            peak_hours=peak_hours,
            avg_fillings_per_day=float(avg_fillings_per_day),
            water_efficiency=float(water_efficiency),
        )

    async def get_efficiency_report(
        self, device_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Genera un reporte de eficiencia completo"""
        flow_metrics = await self.calculate_flow_metrics(device_id, start_date, end_date)
        filling_metrics = await self.calculate_filling_metrics(
            device_id, start_date, end_date
        )

        fillings = await self.filling_repository.get_by_date_range(
            device_id, start_date, end_date
        )

        if fillings:
            df = pd.DataFrame(
                [
                    {
                        "efficiency": f.get_efficiency(),
                        "actual_volume": f.get_actual_volume(),
                        "target_volume": f.target_volume,
                    }
                    for f in fillings
                ]
            )

            # Estadísticas de eficiencia
            efficiency_stats = {
                "mean": float(df["efficiency"].mean()),
                "median": float(df["efficiency"].median()),
                "std": float(df["efficiency"].std()),
                "min": float(df["efficiency"].min()),
                "max": float(df["efficiency"].max()),
            }

            # Distribución de eficiencia
            efficiency_distribution = {
                "excellent (>95%)": len(df[df["efficiency"] > 95]),
                "good (85-95%)": len(
                    df[(df["efficiency"] >= 85) & (df["efficiency"] <= 95)]
                ),
                "fair (70-85%)": len(
                    df[(df["efficiency"] >= 70) & (df["efficiency"] < 85)]
                ),
                "poor (<70%)": len(df[df["efficiency"] < 70]),
            }
        else:
            efficiency_stats = {}
            efficiency_distribution = {}

        return {
            "flow_metrics": flow_metrics.to_dict(),
            "filling_metrics": filling_metrics.to_dict(),
            "efficiency_stats": efficiency_stats,
            "efficiency_distribution": efficiency_distribution,
        }

    async def detect_anomalies(
        self, device_id: str, threshold: float = 100.0
    ) -> Dict[str, Any]:
        """Detecta anomalías en las lecturas usando pandas"""
        # Obtener últimas 1000 lecturas
        readings = await self.flow_reading_repository.get_by_device_id(device_id, 1000)

        if not readings:
            return {"anomalies": [], "total_anomalies": 0}

        df = pd.DataFrame(
            [
                {
                    "id": r.id,
                    "flow_rate": r.flow_rate,
                    "timestamp": r.timestamp,
                    "total_volume": r.total_volume,
                }
                for r in readings
            ]
        )

        # Detectar anomalías usando desviación estándar
        mean = df["flow_rate"].mean()
        std = df["flow_rate"].std()
        upper_bound = mean + (3 * std)
        lower_bound = max(0, mean - (3 * std))

        # Anomalías estadísticas
        statistical_anomalies = df[
            (df["flow_rate"] > upper_bound) | (df["flow_rate"] < lower_bound)
        ]

        # Anomalías por umbral
        threshold_anomalies = df[df["flow_rate"] > threshold]

        # Combinar anomalías
        all_anomalies = pd.concat([statistical_anomalies, threshold_anomalies]).drop_duplicates()

        anomaly_list = [
            {
                "id": int(row["id"]),
                "flow_rate": float(row["flow_rate"]),
                "timestamp": row["timestamp"].isoformat(),
                "reason": "Fuera de rango estadístico" if row["flow_rate"] > upper_bound or row["flow_rate"] < lower_bound else "Excede umbral",
            }
            for _, row in all_anomalies.iterrows()
        ]

        return {
            "anomalies": anomaly_list,
            "total_anomalies": len(anomaly_list),
            "mean_flow_rate": float(mean),
            "std_flow_rate": float(std),
            "upper_bound": float(upper_bound),
            "lower_bound": float(lower_bound),
        }
