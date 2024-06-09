from fastapi import FastAPI, Path, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, select, extract, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from models import ContactBase, ResponseContactModel
from db import Contact, get_db


app = FastAPI()


@app.get("/healthchecker/")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/contact/")
def root():
    return {"message": "Welcome to Homework 11 - FastAPI! Read /redoc or /docs fo help"}


@app.get("/contact/upcoming_birthdays", response_model=list[ResponseContactModel])
async def upcoming_birthdays(db: Session = Depends(get_db)):
    next_days = 7
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
    
    contacts = [ResponseContactModel(
                    id=row.Contact.id,
                    first_name=row.Contact.first_name,
                    last_name=row.Contact.last_name,
                    email=row.Contact.email,
                    phone=row.Contact.phone,
                    birthday=row.Contact.birthday,
                    details=row.Contact.details
                ) for row in result]

    return contacts
    

@app.get("/contact/findall", response_model=list[ResponseContactModel])
async def findall(skip: int = 0, limit: int = Query(default=10, le=200, ge=10), db: Session = Depends(get_db)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@app.get("/contact/view/{contact_id}", response_model=ResponseContactModel)
async def view_contact(contact_id: int = Path(description="The ID of the contact to get", gt=0), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with contact_id={contact_id} not found')
    return contact


@app.get("/contact/find/{string}", response_model=list[ResponseContactModel])
async def find_contact(string: str = Path(description="The string to find in contact filds", min_length=5), db: Session = Depends(get_db)):
    try:
        search_query = "%{}%".format(string)

        contacts = db.query(Contact).filter(
            or_(
                Contact.first_name.ilike(search_query),
                Contact.last_name.ilike(search_query),
                Contact.email.ilike(search_query),
                Contact.phone.ilike(search_query),
                Contact.details.ilike(search_query)
            )
        ).all()

        if contacts:
            return contacts
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with "{string}" not found')

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contact/create/", response_model=ResponseContactModel)
async def create_contact(contact: ContactBase, db: Session = Depends(get_db)):
    new_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birthday=contact.birthday,
        details=contact.details
        )
    try:
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return new_contact


@app.put("/contact/edit/", response_model=ResponseContactModel)
async def edit_contact(new_contact: ResponseContactModel, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == new_contact.id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contact with contact_id={new_contact.id} not found'
        )
    contact.first_name = new_contact.first_name
    contact.last_name = new_contact.last_name
    contact.email = new_contact.email
    contact.phone = new_contact.phone
    contact.birthday = new_contact.birthday
    contact.details = new_contact.details
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


@app.delete("/contact/delete/{contact_id}", response_model=ResponseContactModel)
async def delete_contact(contact_id: int = Path(description="The ID of the contact to delete", gt=0), db: Session = Depends(get_db)):
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id)
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
        return contact
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact with contact_id={contact_id} not found')

