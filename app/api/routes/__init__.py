from fastapi import APIRouter
from .recognize import router as recognize_router
from .packaging_records import router as packaging_records_router

main_router = APIRouter()

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(recognize_router)
api_v1_router.include_router(packaging_records_router)

main_router.include_router(api_v1_router)
