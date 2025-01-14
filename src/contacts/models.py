from sqlalchemy import String, Integer, ForeignKey, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import Base


class Contact(Base):
    """Модель контактів для зберігання інформації про користувачів.

    Attributes:
        id (int): Унікальний ідентифікатор контакту.
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        phone_number (str): Номер телефону контакту.
        email (str): Електронна адреса контакту.
        birthday (Date): Дата народження контакту.
        age (int): Вік контакту.
        additional_info (str, optional): Додаткова інформація про контакт.
        owner_id (int): Ідентифікатор власника контакту (користувача).
        owner (User): Об'єкт власника контакту (відношення до таблиці користувачів).
    """
    __tablename__ = 'contact'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    first_name: Mapped[str] = mapped_column(String, index=True)
    last_name: Mapped[int] = mapped_column(String, index=True)
    phone_number: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    birthday: Mapped[Date] = mapped_column(Date)
    age: Mapped[int] = mapped_column(Integer, index=True)
    additional_info: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    owner: Mapped["User"] = relationship("User", back_populates="contacts")