from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Налаштування додатку.

    Використовує Pydantic для завантаження налаштувань з файлу `.env` та надає доступ
    до налаштувань для роботи з базою даних, поштовим сервером, Redis тощо.

    Атрибути:
        database_url (str): URL для підключення до основної бази даних.
        database_test_url (str): URL для підключення до тестової бази даних.
        secret_key (str): Секретний ключ для шифрування даних.
        mail_password (str): Пароль для поштового сервера (за замовчуванням "test").
        mail_username (str): Ім'я користувача для поштового сервера (за замовчуванням "test").
        mail_from (str): Адреса електронної пошти відправника (за замовчуванням "admin@admin.com").
        mail_port (int): Порт для підключення до поштового сервера (за замовчуванням 1025).
        mail_server (str): Адреса поштового сервера (за замовчуванням "localhost").
        redis_url (str): URL для підключення до Redis (за замовчуванням "redis://localhost:6379/0").

    Конфігурація:
        env_file (str): Шлях до файлу з налаштуваннями середовища (за замовчуванням ".env").
        extra (str): Налаштування для дозволу додаткових невизначених налаштувань в файлі.
    """
    database_url: str
    database_test_url: str
    secret_key: str
    mail_password: str = "test"
    mail_username: str = "test"
    mail_from: str = "admin@admin.com"
    mail_port: int = 1025
    mail_server: str = "localhost"
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

print(settings.database_test_url)