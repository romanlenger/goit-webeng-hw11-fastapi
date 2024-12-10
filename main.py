from contextlib import asynccontextmanager

from fastapi import FastAPI, Path
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.security import OAuth2PasswordBearer
import redis.asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware

from src.contacts.routers import router as contacts_router
from src.auth.routers import router as auth_routers
from config.general import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(settings.redis_url, encoding="utf-8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router=contacts_router, prefix="/contacts", tags=["contacts"])
app.include_router(router=auth_routers, prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


@app.get("/ping")
async def ping():
    return {"message": "pong"}









