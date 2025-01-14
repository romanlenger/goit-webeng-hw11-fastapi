from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from src.contacts.repos import ContactRepository
from src.contacts.schema import ContactResponse, ContactCreate, ContactUpdate
from src.auth.utils import get_current_user

router = APIRouter()
MAX_CONTACTS_PER_USER = 100


@router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Створити новий контакт для поточного користувача.

    Цей ендпоінт дозволяє користувачам створювати контакт. Перед створенням перевіряється,
    чи не досяг користувач максимального ліміту контактів (100). Якщо ліміт не перевищено, 
    контакт створюється і зберігається в базі даних.

    Аргументи:
        contact (ContactCreate): Дані для створення контакту.
        db (AsyncSession): Залежність для сесії бази даних.
        current_user (dict): Поточний аутентифікований користувач.

    Викидає:
        HTTPException: Якщо користувач досяг ліміту контактів.
    
    Повертає:
        ContactResponse: Створений контакт.
    """
    contact_repo = ContactRepository(db)
    user_contacts_count = await db.execute(
        "SELECT COUNT(*) FROM contacts WHERE user_id = :user_id",
        {"user_id": current_user["id"]}
    )
    count = user_contacts_count.scalar()
    
    if count >= MAX_CONTACTS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Досягнуто ліміт контактів. Ви можете мати лише {MAX_CONTACTS_PER_USER} контактів."
        )
    return await contact_repo.create_contact(contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Отримати контакт за його ID.

    Цей ендпоінт дозволяє користувачам отримати деталі конкретного контакту за його ID.
    Якщо контакт не знайдено, викидається помилка 404.

    Аргументи:
        contact_id (int): ID контакту для отримання.
        db (AsyncSession): Залежність для сесії бази даних.

    Викидає:
        HTTPException: Якщо контакт не знайдено.
    
    Повертає:
        ContactResponse: Деталі запитуваного контакту.
    """
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="КОНТАКТ НЕ ЗНАЙДЕНО")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)):
    """
    Оновити існуючий контакт.

    Цей ендпоінт дозволяє користувачам оновити існуючий контакт, надаючи ID контакту 
    та нові дані. Якщо контакт не знайдено, викидається помилка 404.

    Аргументи:
        contact_id (int): ID контакту для оновлення.
        contact (ContactUpdate): Дані для оновлення контакту.
        db (AsyncSession): Залежність для сесії бази даних.

    Викидає:
        HTTPException: Якщо контакт не знайдено.
    
    Повертає:
        ContactResponse: Оновлений контакт.
    """
    contact_repo = ContactRepository(db)
    updated_contact = await contact_repo.update_contact(contact_id, contact.dict(exclude_unset=True))
    if not updated_contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="КОНТАКТ НЕ ЗНАЙДЕНО")
    return updated_contact


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Видалити контакт за його ID.

    Цей ендпоінт дозволяє користувачам видалити контакт з системи за його ID.
    Якщо контакт не знайдено, викидається помилка 404.

    Аргументи:
        contact_id (int): ID контакту для видалення.
        db (AsyncSession): Залежність для сесії бази даних.

    Викидає:
        HTTPException: Якщо контакт не знайдено.
    
    Повертає:
        dict: Підтвердження успішного видалення.
    """
    contact_repo = ContactRepository(db)
    deleted = await contact_repo.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="КОНТАКТ НЕ ЗНАЙДЕНО")
    return {"detail": "Контакт видалено успішно!"}


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
    """
    Пошук контактів за запитом.

    Цей ендпоінт дозволяє користувачам шукати контакти за рядком запиту.
    Повертається список контактів, які відповідають критеріям пошуку.

    Аргументи:
        query (str): Рядок запиту для пошуку.
        db (AsyncSession): Залежність для сесії бази даних.

    Повертає:
        list[ContactResponse]: Список контактів, що відповідають запиту.
    """
    contact_repo = ContactRepository(db)
    return await contact_repo.search_contacts(query)


@router.get("/birthdays/", response_model=list[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    Отримати контакти з найближчими днями народження.

    Цей ендпоінт повертає список контактів, у яких найближчим часом день народження.

    Аргументи:
        db (AsyncSession): Залежність для сесії бази даних.

    Повертає:
        list[ContactResponse]: Список контактів з найближчими днями народження.
    """
    contact_repo = ContactRepository(db)
    return await contact_repo.get_upcoming_birthdays()
