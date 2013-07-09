# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from exceptions import TypeError, ValueError
import re
from sqlalchemy import UniqueConstraint, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.orm import reconstructor, relationship, validates
from oyProjectManager.db import Base
from oyProjectManager import db
from oyProjectManager.models.project import Project
from oyProjectManager.models.shot import Shot
from oyProjectManager import utils

# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class Sequence(Base):
    """Sequence object to help manage sequence related data.
    
    By definition a Sequence is a group of
    :class:`~oyProjectManager.models.shot.Shot`\ s.
    
    The class should be initialized with a
    :class:`~oyProjectManager.models.project.Project` instance and a
    sequenceName.
    
    When a Sequence instance is created it is not persisted in the project
    database. To do it the
    :meth:`~oyProjectManager.models.sequence.Sequence.save` should be called.
    
    The structure of the Sequence should be created by calling its
    :meth:`~oyProjectManager.models.sequence.Sequence.create` method after it
    is saved.
    
    Two sequences are considered to be the same if their name and their project
    names are matching.
    
    :param project: The owner
      :class:`~oyProjectManager.models.project.Project`. A Sequence instance
      can not be created without a proper
      :class:`~oyProjectManager.models.project.Project` instance passed to it
      with the ``project`` argument.
    
    :type project: :class:`~oyProjectManager.models.project.Project` or string
    
    :param str name: The name of the sequence. It is heavily formatted. Follows
      the same naming rules with the
      :class:`~oyProjectManager.models.project.Project`.
    """
    
    __tablename__ = "Sequences"
    __table_args__  = (
        UniqueConstraint("code", "project_id"),
        UniqueConstraint("name", "project_id"),
        {"extend_existing":True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    code = Column(String(256))
    description = Column(String)
    
    project_id = Column(Integer, ForeignKey("Projects.id"))
    
    _project = relationship("Project")
    
    shots = relationship(
        "Shot",
        cascade="all, delete-orphan"
    )
    
    def __new__(cls, project=None, name=None, code=None):
        """the overridden __new__ method to manage the creation of Sequence
        instances.
        
        If the Sequence is created before then calling Sequence() for a second
        time, may be in another Python session will return the Sequence
        instance from the database.
        """
        
        if project and name:
            
            project = Sequence._check_project(project)
            
            # condition the name
            name = Sequence._condition_name(name)
            
            # now get it from the database
            seq_db = db.session.query(Sequence).\
                filter_by(name=name).first()
            
            if seq_db is not None:
                logger.debug("found the sequence in the database")
                logger.debug("returning the Sequence instance from the "
                              "database")
                
                seq_db.__skip_init__ = None
                return seq_db
            else:
                logger.debug("the Sequence should be new, there is no such "
                              "Sequence in the database")
        
        # in any other case just return the normal __new__
        logger.debug("returning a normal Sequence instance")
        return super(Sequence, cls).__new__(cls, project, name, code)
    
    def __init__(self, project, name, code=None):
        
        # skip initialization if this is coming from DB
        if hasattr(self, "__skip_init__"):
            return
        
        logger.debug("initializing the Sequence")
        
        self._project = self._check_project(project)
        logger.debug("id(project.session): %s" % id(db.session))
        
#        self.session = self.project.session
#        logger.debug("id(sequence.session): %s" % id(self.session))
        
        self.name = name
        
        if code is None:
            code = name
        
        self.code = code
        
        self._exists = False
    
    @reconstructor
    def __init_on_load__(self):
        """method that will run for database loaded instances
        """
#        self.session = self.project.session
    
#    def create(self):
#        """creates the sequence structure by calling self.save() and then a
#        self.project.create()
#        """
#        self.save()
#        self.project.create()

    def create(self):
        """creates the sequence structure
        """
        
        # create the sequence structure by calling the self.project.create
        self.project.create()
    
    def save(self):
        """persists the sequence in the database
        """
        
        logger.debug("saving self to the database")
        
        # there should be a session
        # because a Sequence can not be created
        # without an already created Project instance
        
        if self not in db.session:
            db.session.add(self)
        
        db.session.commit()
    
    def add_shots(self, shot_range_formula):
        """adds new shots to the sequence
        
        shot_range_formula should be a range in on of the following format:
        #
        #,#
        #-# (not supported anymore)
        #,#-# (not supported anymore)
        #,#-#,# (not supported anymore)
        #-#,# (not supported anymore)
        etc.
        """
        
        ## for now consider the shot_range_formula as a string of range
        ## do the hard work later
        #
        #new_shot_numbers = utils.uncompress_range(shot_range_formula)
        #
        ## convert the list to strings
        #new_shot_numbers = map(str, new_shot_numbers)
        
        new_shot_numbers = shot_range_formula.split(",")
        
        new_shots = []
        for shot_number in new_shot_numbers:
            logger.debug('shot_number: %s' % shot_number)
            
            # if the project.shot_number_prefix is not '' or None
            # the shot_number can not start with the project.shot_number_prefix
            if self.project.shot_number_prefix != '' \
                and self.project.shot_number_prefix is not None:
                if shot_number.startswith(self.project.shot_number_prefix):
                    # remove it
                    shot_number = \
                        shot_number[len(self.project.shot_number_prefix):]
                    
                    # if the shot_number starts with zeros ('0000') remove them
                    shot_number = re.sub(r'^[0]+', '', shot_number)
            
            # create a new shot instance
            new_shots.append(Shot(self, shot_number))
        
        db.session.add_all(new_shots)
        db.session.commit()

    def add_alternative_shot(self, shot_number):
        """adds a new alternative to the given shot
        
        returns the alternative shot number
        """
        # shot_number could be an int convert it to str
        # get the first integer as int in the string
        shot_number = utils.embedded_numbers(str(shot_number))[1]
        
        # get the next available alternative shot number for that shot
        alternative_shot_number = \
            self.get_next_alternate_shot_number(shot_number)
        
        # add that alternative shot to the shot list
        if alternative_shot_number is not None:
            new_alternative_shot = Shot(self, alternative_shot_number)
            db.session.add(new_alternative_shot)
            db.session.commit()
        
        return alternative_shot_number

    def get_next_alternate_shot_number(self, shot_number):
        """returns the next alternate shot_number number for the given shot_number number
        """
        
        # get the shot_number list
        alternate_letters = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'
        
        for letter in alternate_letters:
            #check if the alternate is in the list
            
            new_shot_number = str(shot_number) + letter
            
            shot_from_db = Shot.query().\
                filter(Shot.sequence_id==self.id).\
                filter(Shot.number==new_shot_number).\
                first()
            
            if not shot_from_db:
                return new_shot_number
        
        return None
    
    def __eq__(self, other):
        """The equality operator
        """
        return isinstance(other, Sequence) and other.name == self.name and\
               other.project == self.project

    def __ne__(self, other):
        """The in equality operator
        """
        return not self.__eq__(other)

    @validates("name")
    def _validate_name(self, key, name):
        """validates the given name
        """
        
        name = Project._condition_name(name)
        
        return name
    
    @classmethod
    def _check_project(cls, project):
        """A convenience function which checks the given project argument value
        
        It is a ``classmethod``, so can be called both in ``__new__`` and other
        methods like ``_validate_project``.
        
        Checks the given project for a couple of conditions, like being None or
        not being an Project instance etc.
        """
        
        if project is None:
            raise TypeError("Sequence.project can not be None")
        
        if not isinstance(project, Project):
            raise TypeError("The project should be and instance of "
                            "oyProjectManager.models.project.Project")
        
        return project
    
    @synonym_for("_project")
    @property
    def project(self):
        """a read-only attribute to return the related Project of this Sequence
        instance
        """
        return self._project
    
    @validates("code")
    def _validate_code(self, key, code):
        """validates the given code value
        """
        
        if code is None:
            code = self.name
        
        if not isinstance(code, (str, unicode)):
            raise TypeError("Sequence.code should be an instance of str or "
                            "unicode, not %s" % type(code))
        
        code = Project._condition_code(code)
        
        return code
    
    @classmethod
    def _condition_name(cls, name):
        """Formats the given name value
        
        :param name: The name value to be conditioned 
        :return: str
        """

        if name is None:
            raise TypeError("The Sequence.name can not be None")

        if not isinstance(name, (str, unicode)):
            raise TypeError("Sequence.name should be an instance of string or "
                            "unicode not %s" % type(name))
        
        if name is "":
            raise ValueError("The Sequence.name can not be an empty string")
        
        name = Project._condition_name(name)
