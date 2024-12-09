from datetime import date, timedelta

from sqlalchemy import select
from fastapi_cache.decorator import cache

from src.contacts.models import Contact
from src.contacts.schema import ContactCreate
from config.cache import key_builder_repo


class ContactRepository:
    def __init__(self, session):
        self.session = session

    @cache(expire=60, namespace="get_contact_repo", key_builder=key_builder_repo)
    async def get_contact(self, contact_id: int) -> Contact:
        query = select(Contact).where(Contact.id==contact_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_contact(self, contact: ContactCreate) -> Contact:
        new_contact = Contact(**contact.model_dump())
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)
        return new_contact
    
    async def update_contact(self, contact_id: int, contact_data: dict) -> Contact:
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
        query = select(Contact).where(Contact.id == contact_id)
        result = await self.session.execute(query)
        contact = result.scalar_one_or_none()
        if not contact:
            return False
        await self.session.delete(contact)
        await self.session.commit()
        return True
    
    async def search_contacts(self, query: str) -> list[Contact]:
        stmt = select(Contact).where(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_upcoming_birthdays(self) -> list[Contact]:
        today = date.today()
        next_week = today + timedelta(days=7)
        stmt = select(Contact).where(
            (Contact.birthday >= today) &
            (Contact.birthday <= next_week)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()