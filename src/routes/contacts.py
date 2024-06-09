from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts


router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/upcoming_birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(db: Session = Depends(get_db)):
    next_days = 7
    contacts = await repository_contacts.get_upcoming_birthdays(db, next_days)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No contacts with birthdays in the next {next_days} days found.'
        )
    return contacts

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_note(contact_id: int, db: Session = Depends(get_db)):
    note = await repository_contacts.get_contact(contact_id, db)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with contact_id={contact_id} not found'
        )
    return note

@router.post("/", response_model=ContactResponse)
async def create_note(body: ContactModel, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)

@router.put("/", response_model=ContactResponse)
async def update_note(body: ContactResponse, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(body, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with contact_id={contact.id} not found'
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with contact_id={contact_id} not found'
        )
    return contact

