from typing import Optional


from fastapi import status, HTTPException, APIRouter

from app.services.llm_advice_picker import advice_picker

router = APIRouter(prefix="/advice", tags=["Advice"])


@router.post("/code")
async def advice_by_qr(): ...
