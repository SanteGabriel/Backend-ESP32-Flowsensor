from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from src.infrastructure.graphql.resolvers import schema, Context
from src.infrastructure.persistence.repositories import (
    SQLAlchemyFlowReadingRepository,
    SQLAlchemyFillingRepository,
    SQLAlchemyPumpRepository,
)
from src.infrastructure.persistence.database import DatabaseManager
from src.application.use_cases.record_flow_reading import RecordFlowReadingUseCase
from src.application.use_cases.manage_filling import (
    StartFillingUseCase,
    CompleteFillingUseCase,
    CancelFillingUseCase,
)
from src.application.use_cases.control_pump import (
    UpdatePumpLevelUseCase,
    ControlPumpUseCase,
    CheckPumpThresholdUseCase,
)
from src.infrastructure.persistence.metrics_service_impl import MetricsServiceImpl
from src.infrastructure.rest import create_sensor_router


class GraphQLServer:
    """Servidor GraphQL con FastAPI"""

    def __init__(self, database_url: str):
        self.app = FastAPI(title="Water Dispenser API", version="1.0.0")
        self.db_manager = DatabaseManager(database_url)

        # Inicializar repositorios
        self.flow_reading_repo = SQLAlchemyFlowReadingRepository(self.db_manager)
        self.filling_repo = SQLAlchemyFillingRepository(self.db_manager)
        self.pump_repo = SQLAlchemyPumpRepository(self.db_manager)

        # Inicializar servicios
        self.metrics_service = MetricsServiceImpl(
            self.flow_reading_repo, self.filling_repo
        )

        # Inicializar casos de uso
        self.record_flow_reading_use_case = RecordFlowReadingUseCase(
            self.flow_reading_repo
        )
        self.start_filling_use_case = StartFillingUseCase(self.filling_repo)
        self.complete_filling_use_case = CompleteFillingUseCase(self.filling_repo)
        self.cancel_filling_use_case = CancelFillingUseCase(self.filling_repo)
        self.update_pump_level_use_case = UpdatePumpLevelUseCase(self.pump_repo)
        self.control_pump_use_case = ControlPumpUseCase(self.pump_repo)
        self.check_pump_threshold_use_case = CheckPumpThresholdUseCase(self.pump_repo)

        # Configurar contexto
        self.context = Context(
            record_flow_reading_use_case=self.record_flow_reading_use_case,
            start_filling_use_case=self.start_filling_use_case,
            complete_filling_use_case=self.complete_filling_use_case,
            cancel_filling_use_case=self.cancel_filling_use_case,
            update_pump_level_use_case=self.update_pump_level_use_case,
            control_pump_use_case=self.control_pump_use_case,
            check_pump_threshold_use_case=self.check_pump_threshold_use_case,
            flow_reading_repository=self.flow_reading_repo,
            filling_repository=self.filling_repo,
            pump_repository=self.pump_repo,
            metrics_service=self.metrics_service,
        )

        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # En producción, especificar orígenes permitidos
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Crear router GraphQL
        graphql_router = GraphQLRouter(
            schema, context_getter=self.get_context, path="/graphql"
        )
        self.app.include_router(graphql_router)

        # Crear y agregar router REST
        rest_router = create_sensor_router(self.record_flow_reading_use_case)
        self.app.include_router(rest_router)

        # Evento de inicio
        @self.app.on_event("startup")
        async def startup():
            await self.db_manager.create_tables()

    async def get_context(self):
        """Obtiene el contexto para GraphQL"""
        return self.context

    def get_app(self) -> FastAPI:
        """Obtiene la aplicación FastAPI"""
        return self.app


# Crear instancia de la aplicación para uvicorn
from src.shared.config.settings import settings

_server = GraphQLServer(settings.DATABASE_URL)
app = _server.get_app()
