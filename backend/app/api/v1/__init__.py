# API v1 module
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["v1"])

# Import and include sub-routers
from app.api.v1.questions import router as questions_router
from app.api.v1.search import router as search_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.subscriptions import router as subscriptions_router

router.include_router(questions_router)
router.include_router(search_router)
router.include_router(dashboard_router)
router.include_router(subscriptions_router)

