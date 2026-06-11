from fastapi import FastAPI

from app.api.v1 import (
    activity,
    analytics,
    auth,
    exports,
    health,
    notifications,
    organizations,
    projects,
    tasks,
    users,
)
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, request_logging_middleware
from app.core.rate_limit import rate_limit_middleware


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.state.logger = configure_logging()
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(rate_limit_middleware)
    register_exception_handlers(app)
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
    app.include_router(projects.router, prefix="/api/v1/organizations", tags=["projects"])
    app.include_router(tasks.router, prefix="/api/v1/organizations", tags=["tasks"])
    app.include_router(activity.router, prefix="/api/v1/organizations", tags=["activity"])
    app.include_router(analytics.router, prefix="/api/v1/organizations", tags=["analytics"])
    app.include_router(notifications.router, prefix="/api/v1/organizations", tags=["notifications"])
    app.include_router(exports.router, prefix="/api/v1/organizations", tags=["exports"])
    return app


app = create_app()
