from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import services.groq_service as groq_service

router = APIRouter()


# ==========================================
# REQUEST MODEL
# ==========================================

class DebugRequest(BaseModel):
    code: str
    apiKey: Optional[str] = None
    api_key: Optional[str] = None
    key: Optional[str] = None


# ==========================================
# HELPERS
# ==========================================

def safe_json_text(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return value.encode("ascii", errors="backslashreplace").decode("ascii")


# ==========================================
# ROUTES
# ==========================================

@router.post("/")
async def debug(payload: DebugRequest):
    code = payload.code

    if not code or not code.strip():
        raise HTTPException(status_code=422, detail="Field 'code' must not be empty.")

    api_key = (
        payload.apiKey
        or payload.api_key
        or payload.key
    )

    try:
        result = groq_service.analyze_code(code, api_key)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=safe_json_text(f"Server error: {exc}")
        )

    if isinstance(result, dict):
        result.setdefault("provider", "groq")
        # Normalise legacy field names
        if "errors" in result and "issues" not in result:
            result["issues"] = result.pop("errors")
        if "explanation" in result and "analysis" not in result:
            result["analysis"] = result.pop("explanation")

    return result


@router.get("/status")
async def status():
    """Check Groq connectivity. Referenced in README."""
    return groq_service.check_connectivity()
