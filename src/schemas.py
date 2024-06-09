from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import date


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=150)
    done: Optional[bool] = None


class NoteModel(NoteBase):
    tags: List[int]


class NoteUpdate(NoteModel):
    done: bool


class NoteStatusUpdate(BaseModel):
    done: bool


class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    details: Optional[str] = ""


class ContactResponse(ContactModel):
    id: int = Field(default=1, ge=0)
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    details: Optional[str] = ""
    
    class Config:
        from_attributes = True 