import time
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter(tags=["health"])
START_TIME = time.time()


@router.get("/health")
async def health() -> dict[str, str | int]:
    return {
        "status": "healthy",
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "0.1.0",
    }


@router.get("/health/detailed")
async def health_detailed(request: Request) -> dict[str, object]:
    checks: dict[str, str] = {}

    try:
        database = request.app.state.container.database()
        async with database.session() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "healthy"
    except Exception as exc:
        checks["postgres"] = f"unhealthy: {exc}"

    all_healthy = all(value == "healthy" for value in checks.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "uptime_seconds": int(time.time() - START_TIME),
    }
