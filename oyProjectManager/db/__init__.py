#-*- coding: utf-8 -*-

import sqlalchemy
from oyProjectManager.db.declarative import Base

# SQLAlchemy database engine
engine = None
secondary_engine = None

# SQLAlchemy session manager
session = None
query = None

# SQLAlchemy metadata
metadata = Base.metadata

# a couple of helper attributes
__mappers__ = []


db_file = None
db_address = None

def setup(database=None):
    """Utility function that helps to connect the system to the given database.
    
    Returns the created session
    
    :param database: The database address, default is None.
    
    :returns: sqlalchemy.orm.session
    """
    
    from oyProjectManager import db
    
    # create engine
    # TODO: create tests for this
    
    db.db_file = database
    db.db_address = "sqlite:///" + db.db_file
    
    db.engine = sqlalchemy.create_engine(db.db_address, echo=False)
    
    # create the database
    db.metadata.create_all(db.engine)
    
    # create the Session class
    Session = sqlalchemy.orm.sessionmaker(bind=db.engine)
    
    # create and save session object to db.session
    db.session = Session()
    db.query = db.session.query
    
    # TODO: create a test to check if the returned session is db.session
    return db.session
