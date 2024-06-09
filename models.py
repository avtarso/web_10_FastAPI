from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import date


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    details: Optional[str] = ""

class ResponseContactModel(ContactBase):
    id: int = Field(default=1, ge=0)
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    details: Optional[str] = ""
    
    class Config:
        from_attributes = True 

    