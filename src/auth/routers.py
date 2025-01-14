from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from cloudinary.uploader import upload

from config.db import get_db
from src.auth.schema import UserResponse, UserCreate, Token
from src.auth.repos import UserRepository
from src.auth.pass_utils import verify_password
from src.auth.mail_utils import send_verification_email, send_reset_password_email
from src.auth.utils import get_current_user, create_acces_token, create_refresh_token, create_verification_token, decode_verification_token


router = APIRouter()
env = Environment(loader=FileSystemLoader("src/templates"))


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Реєстрація нового користувача.

    Цей маршрут створює нового користувача, перевіряючи, чи не існує вже користувач з таким email.
    Після успішної реєстрації відправляється лист для підтвердження email.

    Параметри:
        user_create (UserCreate): Дані для створення нового користувача.
        background_tasks (BackgroundTasks): Фонова задача для відправки email.
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        UserResponse: Дані про зареєстрованого користувача.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered!"
        )
    user = await user_repo.create_user(user_create)
    verification_token = create_verification_token(user.email)
    verification_link = (
        f"http://localhost:8000/auth/verify-email?token={verification_token}"
    )
    template = env.get_template("verification_email.html")
    email_body = template.render(verification_link=verification_link)
    background_tasks.add_task(send_verification_email, user.email, email_body)
    return user


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Підтвердження email користувача за допомогою токена.

    Цей маршрут перевіряє токен підтвердження email, активує користувача після успішної перевірки.

    Параметри:
        token (str): Токен підтвердження email.
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        dict: Повідомлення про успішне підтвердження email.
    """
    email: str = decode_verification_token(token=token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    await user_repo.activate_user(user)
    return {"msg" : "Email verified successfully!"}


@router.post("/forgot-password")
async def forgot_password(email: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Запит на відновлення паролю через email.

    Цей маршрут генерує токен для відновлення паролю та відправляє email з посиланням для зміни паролю.

    Параметри:
        email (str): Email користувача для відновлення паролю.
        background_tasks (BackgroundTasks): Фонова задача для відправки email.
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        dict: Повідомлення про успішну відправку email.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    reset_token = create_verification_token(email)
    reset_link = f"http://localhost:8000/auth/reset-password-form?token={reset_token}"
    template = env.get_template("reset_password_email.html")
    email_body = template.render(reset_link=reset_link)
    background_tasks.add_task(send_reset_password_email, user.email, email_body)

    return {"msg": "Password reset email sent"}


@router.get("/reset-password-form", response_class=HTMLResponse)
async def get_reset_password_form(token: str, db: AsyncSession = Depends(get_db)):
    """Відкриває форму для введення нового паролю після перевірки токена.

    Параметри:
        token (str): Токен для відновлення паролю.
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        HTMLResponse: HTML форма для введення нового паролю.
    """
    try:
        email = decode_verification_token(token)
        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_email(email=email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    template = env.get_template("reset_password_form.html")
    form_html = template.render(token=token)
    return HTMLResponse(content=form_html)


@router.post("/reset-password")
async def reset_password(token: str = Form(...), new_password: str = Form(...), db: AsyncSession = Depends(get_db)):
    """Зміна паролю користувача після перевірки токена.

    Параметри:
        token (str): Токен для зміни паролю.
        new_password (str): Новий пароль для користувача.
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        dict: Повідомлення про успішне оновлення паролю.
    """
    email = decode_verification_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await user_repo.update_password(user, new_password=new_password)

    return {"msg": "Password reset successful"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Отримання токена для автентифікації.

    Цей маршрут дозволяє користувачеві увійти за допомогою логіну та паролю і отримати токен доступу.

    Параметри:
        form_data (OAuth2PasswordRequestForm): Дані для входу (логін та пароль).
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        Token: Токен доступу та токен оновлення для користувача.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username',
            headers={"WWW-Authenticate" : "Bearer"}
        )
    access_token = create_acces_token(data={"sub" : user.username})
    refresh_token = create_refresh_token(data={"sub" : user.username})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/update-avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Оновлення аватара користувача.

    Цей маршрут дозволяє користувачеві завантажити новий аватар.

    Параметри:
        file (UploadFile): Файл аватара для завантаження.
        current_user (UserResponse): Текущий користувач.
        db (AsyncSession): Сесія для роботи з базою даних.

    Повертає:
        UserResponse: Дані користувача з оновленим аватаром.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed."
        )

    try:
        upload_result = upload(
            file.file,
            folder="avatars",
            public_id=current_user.email.split("@")[0],
            overwrite=True,
            resource_type="image"
        )

        avatar_url = upload_result.get("secure_url")
        if not avatar_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image"
            )

        user_repo = UserRepository(db)
        updated_user = await user_repo.update_avatar(current_user.id, avatar_url)

        return updated_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar update failed: {str(e)}"
        )
