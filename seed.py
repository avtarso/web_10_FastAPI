"""
This module is used to fill a database with fictitious values for testing 
and learning.

It creates table for contacts and then writes random data to them.
"""

from faker import Faker
import logging

from db import Contact
from functions import get_session
from settings import DATABASE


# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUANTITY = 360


fake = Faker(['uk_UA'])

def fill_contacts(session):
    """Fills the contacts table in the database.

     Args:
         session (Session): SQLAlchemy session.
     """
    logger.info("Filling Contacts")
    for _ in range(QUANTITY):
        contact = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.numerify('+38 (###) ###-##-##'),
            email=fake.email(),
            birthday=fake.passport_dob(),
            details=fake.sentence()
        )
        session.add(contact)


def main():
    """The main function of fake filling the database."""
    with get_session(DATABASE) as session:
        fill_contacts(session)
        session.commit()
        logger.info("Database filled successfully")

if __name__ == '__main__':
    main()
