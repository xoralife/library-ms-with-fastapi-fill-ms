from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.modules.auth.router import router as auth_router
from app.modules.authors.router import router as authors_router
from app.modules.publishers.router import router as publishers_router
from app.modules.categories.router import router as categories_router
from app.modules.books.router import router as books_router
from app.modules.librarians.router import router as librarians_router
from app.modules.students.router import router as students_router
from app.modules.borrowing.router import router as borrowing_router
from app.modules.reservations.router import router as reservations_router
from app.modules.fines.router import router as fines_router
from app.modules.notifications.router import router as notifications_router
from app.modules.activity_logs.router import router as activity_logs_router
from app.modules.settings.router import router as settings_router
from app.modules.reports.router import router as reports_router
from app.modules.users.router import router as users_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import async_session_factory
    from app.modules.settings.crud import SettingCRUD
    from app.core.auth import create_user
    from app.models.user import User, UserRole
    from sqlalchemy import select

    async with async_session_factory() as db:
        setting_crud = SettingCRUD(db)
        await setting_crud.seed_defaults()

        existing = await db.execute(select(User).where(User.role == UserRole.ADMIN))
        if not existing.scalar_one_or_none():
            await create_user(
                db=db,
                email=settings.admin_email,
                username=settings.admin_username,
                password=settings.admin_password,
                full_name="System Admin",
                role=UserRole.ADMIN,
            )
        await db.commit()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(authors_router, prefix="/api/v1")
app.include_router(publishers_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(books_router, prefix="/api/v1")
app.include_router(librarians_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(borrowing_router, prefix="/api/v1")
app.include_router(reservations_router, prefix="/api/v1")
app.include_router(fines_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(activity_logs_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
