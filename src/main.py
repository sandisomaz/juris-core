import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logging import logger

from src.api.auth import router as auth_router
from src.api.matters import router as matters_router
from src.api.documents import router as documents_router
from src.api.reviews import router as reviews_router
from src.api.rules import router as rules_router
from src.api.reports import router as reports_router
from src.api.audit import router as audit_router
from src.api.analytics import router as analytics_router

app = FastAPI(
    title=settings.APP_NAME,
    description="JurisCore — A human-in-the-loop legal and regulatory intelligence platform combining agentic AI, deterministic rules, retrieval, workflow automation, and continuous compliance monitoring.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(matters_router)
app.include_router(documents_router)
app.include_router(reviews_router)
app.include_router(rules_router)
app.include_router(reports_router)
app.include_router(audit_router)
app.include_router(analytics_router)

# Mount web UI static directory
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} platform engine in environment '{settings.ENVIRONMENT}'...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
