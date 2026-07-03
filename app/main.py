from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.modules.auth.router import router as auth_router
from app.modules.authors.router import router as authors_router
from app.modules.publishers.router import router as publishers_router
from app.modules.categories.router import router as categories_router
from app.modules.books.router import router as books_router
from app.modules.librarians.router import router as librarians_router
from app.modules.students.router import router as students_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
