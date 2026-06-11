from fastapi import FastAPI

from app.api.v1 import activity, analytics, auth, health, organizations, projects, tasks, users
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
    app.include_router(projects.router, prefix="/api/v1/organizations", tags=["projects"])
    app.include_router(tasks.router, prefix="/api/v1/organizations", tags=["tasks"])
    app.include_router(activity.router, prefix="/api/v1/organizations", tags=["activity"])
    app.include_router(analytics.router, prefix="/api/v1/organizations", tags=["analytics"])
    return app


app = create_app()
