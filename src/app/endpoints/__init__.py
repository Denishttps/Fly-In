from .users import router as users
from .api import router as api

from fastapi import APIRouter


router = APIRouter()

router.include_router(api)
router.include_router(users)
