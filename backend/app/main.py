import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.generators.manual_allure_codegen import ManualTestGenerator
from app.generators.auto_ui_playwright_codegen import AutoUiGenerator
from app.generators.auto_api_pytest_codegen import AutoApiGenerator
from app.validators.allure_standard_validator import AllureValidator
from app.optimizers.test_suite_optimizer import TestSuiteOptimizer
from app.utils.errors import GenerationError, ValidationError


class GeneratedFile(BaseModel):
    path: str
    content: str


class ManualGenerateRequest(BaseModel):
    source_type: str
    text: Optional[str] = None
    openapi_yaml: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class AutoUiGenerateRequest(BaseModel):
    requirements_text: str
    manual_tests: Optional[List[GeneratedFile]] = None
    base_url: Optional[str] = None


class AutoApiGenerateRequest(BaseModel):
    openapi_yaml: str
    base_url: str
    auth: Optional[Dict[str, str]] = None


class ValidateRequest(BaseModel):
    manual_tests: List[GeneratedFile]
    ruleset: Optional[str] = Field(default="default")


class OptimizeRequest(BaseModel):
    manual_tests: List[GeneratedFile]
    requirements_text: Optional[str] = None
    openapi_yaml: Optional[str] = None


app = FastAPI(title="TestOps Copilot", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manual_generator = ManualTestGenerator()
auto_ui_generator = AutoUiGenerator()
auto_api_generator = AutoApiGenerator()
validator = AllureValidator()
optimizer = TestSuiteOptimizer()


@app.post("/api/generate/manual")
async def generate_manual(req: ManualGenerateRequest):
    try:
        files, summary = manual_generator.generate(
            source_type=req.source_type,
            text=req.text,
            openapi_yaml=req.openapi_yaml,
            meta=req.meta or {},
        )
        return {"files": files, "summary": summary}
    except GenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/generate/auto/ui")
async def generate_auto_ui(req: AutoUiGenerateRequest):
    files, summary = auto_ui_generator.generate(
        requirements_text=req.requirements_text,
        manual_tests=req.manual_tests or [],
        base_url=req.base_url,
    )
    return {"files": files, "summary": summary}


@app.post("/api/generate/auto/api")
async def generate_auto_api(req: AutoApiGenerateRequest):
    files, summary = auto_api_generator.generate(
        openapi_yaml=req.openapi_yaml,
        base_url=req.base_url,
        auth=req.auth or {},
    )
    return {"files": files, "summary": summary}


@app.post("/api/validate")
async def validate_manual(req: ValidateRequest):
    try:
        report = validator.validate(req.manual_tests, ruleset=req.ruleset)
        return {"report": report}
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/optimize")
async def optimize(req: OptimizeRequest):
    report = optimizer.optimize(
        manual_tests=req.manual_tests,
        requirements_text=req.requirements_text,
        openapi_yaml=req.openapi_yaml,
    )
    return {"report": report}


@app.get("/health")
async def health():
    return {"status": "ok"}
