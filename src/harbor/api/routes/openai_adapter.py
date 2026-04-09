from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from harbor.config import get_settings
from harbor.openai_adapter import openai_probe_payload, openai_runtime_payload

router = APIRouter(prefix="/openai", tags=["openai"])


class OpenAIProbeRequest(BaseModel):
    live_call: bool = Field(default=False)
    input_text: str = Field(default="Respond with the single word OK.")


@router.get("/runtime")
def openai_runtime() -> dict[str, object]:
    settings = get_settings()
    return openai_runtime_payload(settings)


@router.post("/probe")
def openai_probe(request: OpenAIProbeRequest) -> dict[str, object]:
    settings = get_settings()
    return openai_probe_payload(
        settings,
        live_call=request.live_call,
        input_text=request.input_text,
    )
