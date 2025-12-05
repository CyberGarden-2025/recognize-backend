from fastapi import APIRouter
from .recognize import router as recognize_router

main_router = APIRouter()

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(recognize_router)

main_router.include_router(api_v1_router)
