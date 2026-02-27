import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services import prediction_service
from app.routers import auth, trips, vehicles, drivers, analytics, recommendations, budgets, predictions, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load ML model
    logger.info("Loading ML model...")
    loaded = prediction_service.load_model(settings.ML_MODEL_PATH)
    if not loaded:
        logger.warning("ML model not loaded — using fallback predictions")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="FuelIQ API",
    description="Fleet fuel management API for Kenya's transport industry",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")
app.include_router(drivers.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "FuelIQ API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
