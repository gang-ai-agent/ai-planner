from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import GuardrailViolation, PlannerError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(GuardrailViolation)
    async def guardrail_handler(_: Request, exc: GuardrailViolation) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc), "type": "guardrail_violation"})

    @app.exception_handler(PlannerError)
    async def planner_handler(_: Request, exc: PlannerError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc), "type": "planner_error"})
