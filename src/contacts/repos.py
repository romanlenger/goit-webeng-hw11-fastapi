from datetime import date, timedelta

from sqlalchemy import select
from fastapi_cache.decorator import cache

from src.contacts.models import Contact
from src.contacts.schema import ContactCreate
from config.cache import key_builder_repo


class ContactRepository:
    """Репозиторій для взаємодії з моделями контактів у базі даних.

    Використовується для створення, отримання, оновлення, видалення та пошуку контактів.

    Attributes:
        session (AsyncSession): Сесія для роботи з базою даних.
    """

    def __init__(self, session):
        """Ініціалізація репозиторію з сесією.

        Args:
            session (AsyncSession): Сесія для роботи з базою даних.
        """
        self.session = session

    @cache(expire=60, namespace="get_contact_repo", key_builder=key_builder_repo)
    async def get_contact(self, contact_id: int) -> Contact:
        """Отримує контакт за його ID з кешем.

        Використовує кешування для збереження результатів запиту.

        Args:
            contact_id (int): Ідентифікатор контакту.

        Returns:
            Contact | None: Контакт або None, якщо не знайдено.
        """
        query = select(Contact).where(Contact.id==contact_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_contact(self, contact: ContactCreate) -> Contact:
        """Створює новий контакт у базі даних.

        Args:
            contact (ContactCreate): Об'єкт з даними для створення контакту.

        Returns:
            Contact: Створений контакт.
        """
        new_contact = Contact(**contact.model_dump())
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)
        return new_contact

    async def update_contact(self, contact_id: int, contact_data: dict) -> Contact:
        """Оновлює дані контакту.

        Використовує ID для пошуку контакту та оновлює надані дані.

        Args:
            contact_id (int): Ідентифікатор контакту.
            contact_data (dict): Дані для оновлення контакту.

        Returns:
            Contact | None: Оновлений контакт або None, якщо контакт не знайдено.
        """
        query = select(Contact).where(Contact.id == contact_id)
        result = await self.session.execute(query)
        contact = result.scalar_one_or_none()
        if not contact:
            return None
        for key, value in contact_data.items():
            setattr(contact, key, value)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int) -> bool:
        """Видаляє контакт з бази даних.

        Args:
            contact_id (int): Ідентифікатор контакту для видалення.

        Returns:
            bool: True, якщо контакт успішно видалено, інакше False.
        """
        query = select(Contact).where(Contact.id == contact_id)
        result = await self.session.execute(query)
        contact = result.scalar_one_or_none()
        if not contact:
            return False
        await self.session.delete(contact)
        await self.session.commit()
        return True

    async def search_contacts(self, query: str) -> list[Contact]:
        """Шукає контакти за заданим запитом.

        Шукає контакти за іменем, прізвищем або електронною адресою.

        Args:
            query (str): Пошуковий запит.

        Returns:
            list[Contact]: Список контактів, що відповідають запиту.
        """
        stmt = select(Contact).where(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_birthdays(self) -> list[Contact]:
        """Отримує контакти з днями народження, які будуть у найближчий тиждень.

        Використовує поточну дату для пошуку контактів, що мають день народження
        протягом наступних семи днів.

        Returns:
            list[Contact]: Список контактів, у яких день народження найближчим часом.
        """
        today = date.today()
        next_week = today + timedelta(days=7)
        stmt = select(Contact).where(
            (Contact.birthday >= today) &
            (Contact.birthday <= next_week)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
