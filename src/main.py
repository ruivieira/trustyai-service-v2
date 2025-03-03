from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from fastapi.middleware.cors import CORSMiddleware
import logging

# Endpoint routers
from src.endpoints.consumer import router as consumer_router
from src.endpoints.dir import router as dir_router
from src.endpoints.data_upload import router as data_upload_router
# from src.endpoints.drift_metrics import router as drift_metrics_router
from src.endpoints.drift_metrics_collection.approx_ks_test import router as drift_approx_ks_test_router
from src.endpoints.drift_metrics_collection.fourier_mmd import router as drift_fourier_mmd_router
from src.endpoints.drift_metrics_collection.ks_test import router as drift_ks_test_router
from src.endpoints.drift_metrics_collection.meanshift import router as drift_meanshift_router
# from src.endpoints.explainers import router as explainers_router
from src.endpoints.explainers_collection.global_exp import router as explainers_global_router
from src.endpoints.explainers_collection.local_exp import router as explainers_local_router
from src.endpoints.fairness_metrics import router as fairness_metrics_router
from src.endpoints.identity import router as identity_router
from src.endpoints.metadata import router as metadata_router
from src.endpoints.metrics_info import router as metrics_info_router
from src.endpoints.data_download import router as data_download_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TrustyAI Service API",
    version="1.0.0rc0",
    description="TrustyAI Service API",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(consumer_router, tags=["{Internal Only} Inference Consumer"])
app.include_router(dir_router, tags=["Fairness Metrics: Group: Disparate Impact Ratio"])
app.include_router(data_upload_router, tags=["Data Upload"])
# app.include_router(
#     drift_metrics_router,
#     tags=[
#         "Drift Metrics: ApproxKSTest",
#         "Drift Metrics: FourierMMD Drift",
#         "Drift Metrics: KSTest",
#         "Drift Metrics: Meanshift",
#     ],
# )
app.include_router(
    drift_approx_ks_test_router,
    tags=[
        "Drift Metrics: ApproxKSTest",
    ],
)
app.include_router(
    drift_fourier_mmd_router,
    tags=[
        "Drift Metrics: FourierMMD Drift",
    ],
)
app.include_router(
    drift_ks_test_router,
    tags=[
        "Drift Metrics: KSTest",
    ],
)
app.include_router(
    drift_meanshift_router,
    tags=[
        "Drift Metrics: Meanshift",
    ],
)
# app.include_router(explainers_router, tags=["Explainers: Global", "Explainers: Local"])
app.include_router(explainers_global_router, tags=["Explainers: Global"])
app.include_router(explainers_local_router, tags=["Explainers: Local"])
app.include_router(
    fairness_metrics_router,
    tags=["Fairness Metrics: Group: Statistical Parity Difference"],
)
app.include_router(identity_router, tags=["Identity Endpoint"])
app.include_router(metadata_router, tags=["Service Metadata"])
app.include_router(metrics_info_router, tags=["Metrics Information Endpoint"])
app.include_router(data_download_router, tags=["Download Endpoint"])

# Deprecated endpoints
app.include_router(
    dir_router, prefix="/metrics", tags=["{Legacy}: Disparate Impact Ratio"]
)
app.include_router(
    fairness_metrics_router,
    prefix="/metrics",
    tags=["{Legacy}: Statistical Parity Difference"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to TrustyAI Explainability Service"}


@app.get("/p/metrics")
async def metrics(request: Request):
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Readiness probe
@app.get("/q/health/ready")
async def readiness_probe():
    return JSONResponse(content={"status": "ready"}, status_code=200)


# Liveness probe endpoint
@app.get("/q/health/live")
async def liveness_probe():
    return JSONResponse(content={"status": "live"}, status_code=200)
