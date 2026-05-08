# API v1 module
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["v1"])

# Import and include sub-routers
from app.api.v1.questions import router as questions_router
from app.api.v1.search import router as search_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.discussions import router as discussions_router
from app.api.v1.practice import router as practice_router
from app.api.v1.bookmarks import router as bookmarks_router
from app.api.v1.revisions import router as revisions_router
from app.api.v1.mistakes import router as mistakes_router
from app.api.v1.leaderboard import router as leaderboard_router

router.include_router(bookmarks_router)
router.include_router(revisions_router)
router.include_router(mistakes_router)
router.include_router(leaderboard_router)
router.include_router(questions_router)
router.include_router(search_router)
router.include_router(dashboard_router)
router.include_router(subscriptions_router)
router.include_router(practice_router)
router.include_router(discussions_router, tags=["Discussions"])

