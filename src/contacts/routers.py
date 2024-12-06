from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from src.contacts.repos import ContactRepository
from src.contacts.schema import ContactResponse, ContactCreate, ContactUpdate

router = APIRouter()


@router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    return await contact_repo.create_contact(contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CONTACT NOT FOUND")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    updated_contact = await contact_repo.update_contact(contact_id, contact.dict(exclude_unset=True))
    if not updated_contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CONTACT NOT FOUND")
    return updated_contact


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    deleted = await contact_repo.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CONTACT NOT FOUND")
    return {"detail": "Контакт видалено успішно!"}


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    return await contact_repo.search_contacts(query)


@router.get("/birthdays/", response_model=list[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contact_repo = ContactRepository(db)
    return await contact_repo.get_upcoming_birthdays()