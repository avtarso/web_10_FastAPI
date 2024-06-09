from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

from db import Base


# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session(database):
    """Creates and returns a database session.

     Args:
         database (str): Database URL.

     Returns:
         sessionmaker: SQLAlchemy session object.
     """
    engine = create_engine(database)
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    return DBSession()

@contextmanager
def get_session(database): 
    """Context manager for creating and closing a database session.

     Args:
         database (str): Database URL.

     Yields:
         Session: SQLAlchemy session.
     """
    session = create_session(database)
    try:
        yield session
    except Exception as e:  # logging
        logger.error("Error in session: %s", e)
        session.rollback()
        raise
    finally:
        session.close()