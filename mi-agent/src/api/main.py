from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.agent.runner import run_agent

app = FastAPI(
    title="mi-agent API",
    description="Agente investigador financiero LATAM",
    version="0.1.0",
)


class ReportRequest(BaseModel):
    empresa: str


class ReportResponse(BaseModel):
    empresa: str
    reporte: str


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest) -> ReportResponse:
    try:
        result = await run_agent(request.empresa)
        return ReportResponse(empresa=request.empresa, reporte=result["reporte"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
