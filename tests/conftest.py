import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app
from src.auth.models import Role, User
from src.auth.schema import RoleEnum
from config.general import settings
from config.db import Base, get_db
from src.auth.pass_utils import get_password_hash
from src.auth.utils import create_acces_token, create_refresh_token
from src.contacts.models import Contact
 
DATABASE_URL = settings.database_test_url

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database=setup_database):
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def override_get_db(db_session):
    async def _get_db():
        async with db_session() as session:
            yield session
    app.dependency_overrides[get_db] = _get_db 
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def user_role(db_session) -> Role:
    role = Role(
        id=1, 
        name=RoleEnum.USER.value, 
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope="function")
async def user_password(faker):
    return faker.password()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session, faker, user_role, user_password):
    hashed_password = get_password_hash(user_password)
    user = User(
        email=faker.email(),
        username=faker.name(),
        hashed_password=hashed_password,
        role_id=user_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def auth_header(test_user: User):
    access_token = create_acces_token({"sub": test_user.username})
    refresh_token = create_refresh_token({"sub": test_user.username})
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Token-Refresh": refresh_token,
    }
    return headers


@pytest_asyncio.fixture(scope="function")
async def test_user_contact(db_session, test_user, faker) -> Contact:
    contact = Contact(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        owner_id=test_user.id,
        phone_number=faker.phone_number(),
        birthday=faker.date_of_birth(),
        additional_info=faker.text(),
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)
    return contact