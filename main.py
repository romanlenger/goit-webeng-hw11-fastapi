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
    """Менеджер контексту для ініціалізації та закриття підключення до Redis.

    Цей менеджер контексту використовується для ініціалізації кешування за допомогою Redis при запуску
    FastAPI додатку і закриття підключення при його завершенні.

    Параметри:
        app (FastAPI): Екземпляр додатку FastAPI.
    
    Використовує:
        RedisBackend для кешування в Redis.
    """
    redis = aioredis.from_url(settings.redis_url, encoding="utf-8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)
"""Екземпляр FastAPI додатку.

Ініціалізує FastAPI додаток з підтримкою кешування через Redis і включає необхідні роутери
для контактів та автентифікації.
"""

app.include_router(router=contacts_router, prefix="/contacts", tags=["contacts"])
"""Роутер для роботи з контактами.

Імпортується з `src.contacts.routers` і доступний за шляхом `/contacts`.
"""

app.include_router(router=auth_routers, prefix="/auth", tags=["auth"])
"""Роутер для автентифікації.

Імпортується з `src.auth.routers` і доступний за шляхом `/auth`.
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
"""OAuth2 схема безпеки для автентифікації.

Використовує FastAPI стандарт для отримання токена доступу за допомогою `/auth/token`.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
"""Міжмодульне програмне забезпечення (middleware) для підтримки CORS.

Це middleware дозволяє доступ з будь-якого джерела, підтримує всі методи HTTP, 
забезпечує передачу cookies та інші заголовки.
"""

@app.get("/ping")
async def ping():
    """Тестовий маршрут для перевірки доступності сервера.

    Повертає повідомлення, що сервер працює.

    Відповідь:
        JSON об'єкт з полем "message" = "pong".
    """
    return {"message": "pong"}
