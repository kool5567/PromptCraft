from fastapi import APIRouter

from app.api.v1 import auth, users, prompts, generator, library, categories
from app.api.v1 import tags, models, favorites, collections, templates
from app.api.v1 import ratings, import_export, search, subscriptions, admin

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
router.include_router(generator.router, prefix="/generator", tags=["Generator"])
router.include_router(library.router, prefix="/library", tags=["Library"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(tags.router, prefix="/tags", tags=["Tags"])
router.include_router(models.router, prefix="/models", tags=["AI Models"])
router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
router.include_router(collections.router, prefix="/collections", tags=["Collections"])
router.include_router(templates.router, prefix="/templates", tags=["Templates"])
router.include_router(ratings.router, prefix="/prompts", tags=["Ratings"])
router.include_router(import_export.router, prefix="/import", tags=["Import/Export"])
router.include_router(search.router, prefix="/search", tags=["Search"])
router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
