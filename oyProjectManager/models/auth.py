# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from exceptions import TypeError
import re
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship, validates
from oyProjectManager.db import Base
from oyProjectManager import db

# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class User(Base):
    """Manages users
    
    The user class is the representation of the users in the system.
    
    Because there is no central database in the current implementation of
    oyProjectManager, a user is stored in the
    :class:`~oyProjectManager.models.project.Project`\ 's database only if the
    user has created some data. So creating a user and querying the
    :class:`~oyProjectManager.models.project.Project`\ s that this user has
    worked has no direct way.
    
    :param name: The name of the user.
    
    :param initials: Initials of the user. If skipped the initials will be
      extracted from the :attr:`~oyProjectManager.models.auth.User.name`
      attribute.
    
    :param email: The email address of the user.
    """

    __tablename__ = "Users"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String)
    initials = Column(String)
    email = Column(String)
    
    active = Column(Boolean, default=True)
    
    versions_created = relationship("Version")
    
    def __init__(self, name, initials=None, email=None, active=True):
        self.name = name
        self.initials = initials
        self.email = email
        self.active = active
    
    def __eq__(self, other):
        """the equality operator
        """
        return isinstance(other, User) and self.name == other.name
    
    def __str__(self):
        """The string representation of this User instance
        """
        return self.name
    
    def __repr__(self):
        """The representation of this User
        """
        return "<User: %s>" % self.name
    
    def save(self):
        """saves this User instance to the database
        """
        
        if db.session is not None:
            if self not in db.session:
                db.session.add(self)
            
            db.session.commit()


class Client(Base):
    """Represents the Client
    
    :param str name: The name of the client. It is a string can not be empty
    
    :param str generic_info: it is a string holding generic information about
      the client.
    """
    
    __tablename__ = "Clients"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String(256), unique=True)
    code = Column(String(256), unique=True)
    generic_info = Column(String)
    
    def __init__(self, name, code=None, generic_info=""):
        self.name = name
        self.code = code
        self.generic_info = generic_info
    
    def __repr__(self):
        return "<Client : %s (%s)>" % (self.name, self.code)
    
    @validates('name')
    def _validate_name(self, key, name):
        """validates the given name value
        """
        if name is None or not isinstance(name, (str, unicode)):
            raise TypeError('Client.name should be a string or unicode, not '
                            '%s' % name.__class__.__name__)
        return name
    
    @validates('code')
    def _validate_code(self, key, code):
        """validates the given code value
        """
        if code is None:
            code = re.sub(r"[^A-Z]", "", self.name.title())
            # make it real unique
            import uuid
            code = code + "_" + uuid.uuid4().get_hex()[:4]
        
        if not isinstance(code, (str, unicode)):
            raise TypeError('Client.code should be a string or unicode, not '
                            '%s' % code.__class__.__name__)
        
        # remove spaces
        code = code.replace(" ", "")
        
        return code
    
    def save(self):
        """saves the instance to database
        """
        if db.session is not None:
            if self not in db.session:
                db.session.add(self)
            db.session.commit()
