from fastapi import FastAPI
from app.configuration.logging_configuration import setup_logging
from app.controller import calculator_controller

setup_logging()
app = FastAPI(title="Calculator",)
app.include_router(calculator_controller.router)

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}