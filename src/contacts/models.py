from sqlalchemy import String, Integer, ForeignKey, Date, Float
from sqlalchemy.orm import Mapped, mapped_column

from config.db import Base


class Contact(Base):
    __tablename__ = 'contact'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    first_name: Mapped[str] = mapped_column(String, index=True)
    last_name: Mapped[int] = mapped_column(String, index=True)
    phone_number: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    birthday: Mapped[Date] = mapped_column(Date)
    age: Mapped[int] = mapped_column(Integer, index=True)
    additional_info: Mapped[str | None] = mapped_column(String, nullable=True)