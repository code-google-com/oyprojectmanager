# -*- coding: utf-8 -*-
"""
Database Module
===============

This is where all the magic happens.

.. versionadded:: 0.2.0
    SQLite3 Database:
    
    To hold the information about all the data created
    :class:`~oyProjectManager.core.models.Project`\ s,
    :class:`~oyProjectManager.core.models.Sequence`\ s,
    :class:`~oyProjectManager.core.models.Shot`\ s,
    :class:`~oyProjectManager.core.models.Asset`\ s and
    :class:`~oyProjectManager.core.models.VersionType`\ s
    , there is a ".metadata.db" file in the repository root. This SQLite3
    database has all the information about everything.
    
    With this new extension it is much faster to query any data needed.

Querying data is very simple and fun. To get any kind of data from the
database, just call the ``db.setup()`` and then use ``db.query`` to get the
data.

For a simple example, lets get all the shots for a Sequence called
"TEST_SEQ" in the "TEST_PROJECT"::

    from oyProjectManager import db
    from oyProjectManager.core.models import Project, Sequence, Shot
    
    # setup the database session
    db.setup()
    
    all_shots = db.query(Shot).join(Sequence).\
        filter(Sequence.project.name="TEST_PROJECT").\
        filter(Shot.sequence.name=="TEST_SEQ").all()

that's it.

"""
import os
import logging

import sqlalchemy
import oyProjectManager
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

database_url = None

# create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def setup(database_url=None):
    """Utility function that helps to connect the system to the given database.
    
    Returns the created session
    
    :param database_url: The database address, default is None. If the
        database_url is skipped or given as None, the default database url
        from the :mod:`oyProjectManager.config` will be used. This is good,
        just call ``db.setup()`` and then use ``db.session`` and ``db.query``
        to get the data.
    
    :returns: sqlalchemy.orm.session
    """
    
    from oyProjectManager import db
    
    # import all the models to let them attach themselves to the Base.mapper
    from oyProjectManager.core.models import *
    
    # create engine
    # TODO: create tests for this
    
    if database_url is None:
        logger.debug("using the default database_url from the config file")
        
        # use the default database
        conf = oyProjectManager.conf
        database_url = conf.database_url
    
    # expand user and env variables if any
    database_url = os.path.expanduser(
        os.path.expandvars(
            os.path.expandvars(
                database_url
            )
        )
    )
    
    db.database_url = database_url
    
    logger.debug("setting up database in %s" % db.database_url)
    
    db.engine = sqlalchemy.create_engine(db.database_url, echo=False)
    
    # create the database
    db.metadata.create_all(db.engine)
    
    # create the Session class
    Session = sqlalchemy.orm.sessionmaker(bind=db.engine)
    
    # create and save session object to db.session
    db.session = Session()
    db.query = db.session.query
    
    # initialize the db
    __init_db__()
    
    # TODO: create a test to check if the returned session is db.session
    return db.session

def __init_db__():
    """initializes the just setup database
    
    It adds:
    
        - Users
        - VersionTypes
        
    to the database.
    """
    
    logger.debug("db is newly created, initializing the db")
    
    from oyProjectManager import db
    
    # get the users from the config
    from oyProjectManager import conf
    
    from oyProjectManager.core.models import User, VersionType
    
    # ------------------------------------------------------
    # create the users
    
    # get all users from db
    users_from_db = db.query(User).all()
    
    for user_data in conf.users_data:
        name = user_data.get("name")
        initials = user_data.get("initials")
        email = user_data.get("email")
        
        user_from_config = User(name, initials, email)
        
        if user_from_config not in users_from_db:
            db.session.add(user_from_config)
    
    # ------------------------------------------------------
    # add the VersionTypes
    version_types_from_db = db.query(VersionType).all()
    
    for version_type in conf.version_types:
        version_type_from_conf = VersionType(**version_type)
        
        if version_type_from_conf not in version_types_from_db:
            db.session.add(version_type_from_conf)
    
    db.session.commit()
    
    logger.debug("finished initialization of the db")
