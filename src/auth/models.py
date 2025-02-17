

from sqlalchemy import String, Integer, ForeignKey, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.db import Base
from src.contacts.models import Contact





class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class User(Base):
    """Модель користувача для зберігання інформації про користувачів.

    Attributes:
        email (str): Електронна адреса користувача.
        username (str): Ім'я користувача.
        hashed_password (str): Хешований пароль.
        role_id (int): Ідентифікатор ролі користувача.
        is_active (bool): Стан активності користувача.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="owner")
    