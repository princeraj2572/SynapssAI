from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router_track      import router as track_router
from api.router_analytics  import router as analytics_router
from api.router_streaks    import router as streaks_router
from api.router_memory     import router as memory_router
from api.router_journal    import router as journal_router
from api.router_alerts     import router as alerts_router
from api.router_activities import router as activities_router
from api.router_export     import router as export_router
from services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="Personal Life OS API",
    version="1.0.0",
    description="Privacy-first local life analytics with AI coaching",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(track_router)
app.include_router(analytics_router)
app.include_router(streaks_router)
app.include_router(memory_router)
app.include_router(journal_router)
app.include_router(alerts_router)
app.include_router(activities_router)
app.include_router(export_router)


@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup."""
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on app shutdown."""
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "running", "version": "1.0.0"}


@app.get("/")
def root():
    return {
        "message": "Personal Life OS API",
        "docs": "http://localhost:8080/docs",
        "health": "http://localhost:8080/health",
    }
