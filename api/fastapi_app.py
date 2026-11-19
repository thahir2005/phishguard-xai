"""
FastAPI Production Implementation for PhishGuard-XAI
Can be served with Uvicorn / Gunicorn for enterprise deployment.
Usage: uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000
"""

import os
import sys
from typing import List
from pydantic import BaseModel, HttpUrl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml_engine.model_core import PhishGuardEngine
from ml_engine.evaluate_benchmark import get_comparison_table
from ml_engine.feature_extractor import FEATURE_COLUMNS

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles

    app = FastAPI(
        title="PhishGuard-XAI API",
        description="Explainable Machine Learning URL Phishing Detection Engine",
        version="2.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = PhishGuardEngine.get_instance()

    class ScanRequest(BaseModel):
        url: str

    class BatchScanRequest(BaseModel):
        urls: List[str]

    @app.get("/api/health")
    def health():
        return {
            "status": "healthy",
            "service": "PhishGuard-XAI Engine",
            "metrics": engine.test_metrics
        }

    @app.get("/api/benchmark")
    def benchmark():
        return {
            "paper_reference": "Dirchaoui et al. (Procedia Computer Science 2026)",
            "table_1_comparison": get_comparison_table()
        }

    @app.post("/api/scan")
    def scan(req: ScanRequest):
        if not req.url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")
        return engine.scan_url(req.url)

    @app.post("/api/batch-scan")
    def batch_scan(req: BatchScanRequest):
        results = [engine.scan_url(u) for u in req.urls[:50]]
        return {"batch_count": len(results), "results": results}

except ImportError:
    # If fastapi is not installed yet
    app = None
