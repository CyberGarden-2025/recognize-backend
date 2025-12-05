from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from cashews import cache

from app.api.routes import main_router
from app.settings import SETTINGS
from app.services import s3_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.setup("mem://")

    if (
        s3_client.endpoint_url
        and s3_client.aws_access_key_id
        and s3_client.aws_secret_access_key
        and SETTINGS.S3_BUCKET_NAME
    ):
        logger.info("S3 connecting...")
        await s3_client.create_bucket(SETTINGS.S3_BUCKET_NAME)
        logger.info("S3 is connected")
    else:
        logger.info("S3 is not configured")

    yield
    ...


app = FastAPI(
    title=f"Recognizer CyberGarden 2025",
    lifespan=lifespan,
    version="1.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(main_router)


def log_fastapi_error(exc: Exception) -> None:
    logger.error(f"[CORE]: {exc.__class__.__name__} in FastAPI: {exc}")


@app.exception_handler(Exception)
async def any_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_fastapi_error(exc)
    return JSONResponse(
        status_code=500, content={"message": "Something went wrong: " + str(exc)}
    )


@app.get("/")
async def hello_world():
    return {"message": "Hello World"}
