from typing import List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session, subqueryload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, extract, and_, or_

from src.database.models import Contact
from src.schemas import ContactModel, ContactResponse

from datetime import datetime, timedelta



async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        details=body.details
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactResponse, db: Session) -> ContactResponse | None:
    contact = db.query(Contact).filter(Contact.id == body.id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.details = body.details
        try:
            db.commit()
            db.refresh(contact)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while updating the contact. - {e}"
            )
    return contact


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id)
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_upcoming_birthdays(db: Session, next_days) -> List[Contact]:
    today = datetime.now().date()
    next_week = today + timedelta(days=next_days)

    today_month = today.month
    today_day = today.day
    next_week_month = next_week.month
    next_week_day = next_week.day

    if today_month == next_week_month:
        query = (
            select(Contact)
            .where(
                and_(
                    extract('month', Contact.birthday) == today_month,
                    extract('day', Contact.birthday).between(today_day, next_week_day)
                )
            )
            .order_by(
                extract('month', Contact.birthday),
                extract('day', Contact.birthday)
            )
        )
    else:
        query = (
            select(Contact)
            .where(
                or_(
                    and_(
                        extract('month', Contact.birthday) == today_month,
                        extract('day', Contact.birthday) >= today_day
                    ),
                    and_(
                        extract('month', Contact.birthday) == next_week_month,
                        extract('day', Contact.birthday) <= next_week_day
                    )
                )
            )
            .order_by(
                extract('month', Contact.birthday),
                extract('day', Contact.birthday)
            )
        )

    result = db.execute(query).all()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No contacts with birthdays in the next {next_days} days found.'
        )
    
    contacts = [ContactResponse(
                    id=row.Contact.id,
                    first_name=row.Contact.first_name,
                    last_name=row.Contact.last_name,
                    email=row.Contact.email,
                    phone=row.Contact.phone,
                    birthday=row.Contact.birthday,
                    details=row.Contact.details
                ) for row in result]

    return contacts
