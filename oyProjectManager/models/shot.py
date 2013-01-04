# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from exceptions import TypeError, ValueError
import re
from sqlalchemy import UniqueConstraint, Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.orm import relationship, validates
from oyProjectManager import db
from oyProjectManager.models.entity import VersionableBase


# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Shot(VersionableBase):
    """The class that enables the system to manage shot data.
    
    .. note::
      
       There is a design flaw, which I've recognized at the day I'll release
       version 0.2.0. The ``_code`` of the Shot is not stored in the database,
       whereas the ``_code`` of a the Asset is. So one can not query Shot's by
       using the ``_code`` attribute, but it is easy to get the same effect by
       using the ``number`` attribute. So you need to create you queries with
       ``number`` instead of ``_code``.
       
       I hope I'll fix it in a later version.
      
    The total of the handle attributes should not be bigger then duration-1, in
    which results no frame for the real shot.
    
    :param sequence: The :class:`~oyProjectManager.models.sequence.Sequence`
      instance that this Shot should belong to. The Sequence may not be created
      yet. Skipping it or passing None will raise TypeError, and anything
      other than a :class:`~oyProjectManager.models.sequence.Sequence` will
      raise a TypeError.
    
    :param number: A string or integer holding the number of this shot. Can not
      be None or can not be skipped, a TypeError will be raised either way. It
      will be used to create the
      :attr:`~oyProjectManager.models.shot.Shot.code` attribute.
    
    :param start_frame: The start frame of this shot. Should be an integer, any
      other type will raise TypeError. The default value is 1 and skipping it
      will result the start_frame to be set to 1.
    
    :param end_frame: The end frame of this shot. Should be an integer, any
      other type will raise TypeError. The default value is 1 and skipping it
      will result the end_frame to be set to 1.
    
    :param description: A string holding the short description of this shot.
      Can be skipped.
    
    """
    
    __tablename__ = "Shots"
    __table_args__  = (
        UniqueConstraint("sequence_id", "number"),
        {"extend_existing":True}
    )
    __mapper_args__ = {"polymorphic_identity": "Shot"}
    
    shot_id =  Column("id", Integer, ForeignKey("Versionables.id") ,primary_key=True)
    
    number = Column(String)
    
    start_frame = Column(Integer, default=1)
    end_frame = Column(Integer, default=1)
    
    # TODO: create tests for handles
    handle_at_start = Column(Integer, default=0)
    handle_at_end = Column(Integer, default=0)
    
    sequence_id = Column(Integer, ForeignKey("Sequences.id"))
    _sequence = relationship(
        "Sequence",
        primaryjoin="Shots.c.sequence_id==Sequences.c.id"
    )
    
    def __init__(self,
                 sequence,
                 number,
                 start_frame=1,
                 end_frame=1,
                 description=''):
        
        self._sequence = self._validate_sequence(sequence)
        # update the project attribute
        self._project = self._sequence.project
        
        self.number = number
        
        self.description = description

        self._duration = 1
        self.start_frame = start_frame
        self.end_frame = end_frame
        
        self.handle_at_start = 0
        self.handle_at_end = 0
        
        #self._cutSummary = ''
    
    def __eq__(self, other):
        """the equality operator
        """
        return isinstance(other, Shot) and other.number == self.number and \
            other.sequence == self.sequence
    
    def __ne__(self, other):
        """the inequality operator
        """
        
        return not self.__eq__(other)
    
    def __str__(self):
        """returns the string representation of the object
        """
        return self.code
    
    def __repr__(self):
        """returns the representation of the class
        """
        return "< oyProjectManager.models.shot.Shot object: " + self.code + ">"

    def _validate_sequence(self, sequence):
        """validates the given sequence value
        """
        
        from oyProjectManager.models.sequence import Sequence

        if sequence is None:
            raise TypeError("Shot.sequence can not be None")

        if not isinstance(sequence, Sequence):
            raise TypeError("Shot.sequence should be an instance of "
                            "oyProjectManager.models.sequence.Sequence")

        return sequence

    @validates("description")
    def _validate_description(self, key, description):
        """validates the given description value
        """

        if description is None:
            description = ""

        if not isinstance(description, (str, unicode)):
            raise TypeError("Shot.description should be an instance of str "
                            "or unicode")

        return description

    @validates("start_frame")
    def _validate_start_frame(self, key, start_frame):
        """validates the given start_frame value
        """

        if start_frame is None:
            start_frame = 1

        if not isinstance(start_frame, int):
            raise TypeError("Shot.start_frame should be an instance of "
                            "integer")

        if self.end_frame is not None:
            self._update_duration(start_frame, self.end_frame)

        return start_frame

    @validates("end_frame")
    def _validate_end_frame(self, key, end_frame):
        """validates the given end_frame value
        """

        if end_frame is None:
            end_frame = 1

        if not isinstance(end_frame, int):
            raise TypeError("Shot.end_frame should be an instance of "
                            "integer")

        if self.end_frame is not None:
            self._update_duration(self.start_frame, end_frame)

        return end_frame

    def _update_duration(self, start_frame, end_frame):
        """updates the duration
        """
        self._duration = end_frame - start_frame + 1

    @synonym_for("_sequence")
    @property
    def sequence(self):
        """The sequence of the current Shot instance.
        :returns: :class:`~oyProjectManager.models.sequence.Sequence`
        """
        return self._sequence


    @property
    def duration(self):
        """the duration
        """
        self._update_duration(self.start_frame, self.end_frame)
        return self._duration


    @validates("number")
    def _validates_number(self, key, number):
        """validates the given number value
        """
        
        if not isinstance(number, (int, str, unicode)):
            raise TypeError("Shot.number should be and instance of integer, "
                            "string or unicode")
        
        # first convert it to a string
        number = str(number)
        
        # then format it
        # remove anything which is not a number or letter
        number = re.sub(r"[^0-9a-zA-Z\-_\ ]+", "", number)
        number = re.sub(r"[\ ]+", "_", number)
        
        number = number.upper()
        
        if number == "":
            raise ValueError("Shot.number is not in good format, please "
                             "supply something like 1, 2, 3A, 10B")
        
        # now check if the number is present for the current Sequence
        shot_instance = db.session.query(Shot).\
            filter(Shot.number==number).\
            filter(Shot.sequence_id==self.sequence.id).\
            first()
        
        if shot_instance is not None:
            raise ValueError("Shot.number already exists for the given "
                             "sequence please give a unique shot code")
        
        return number

    def save(self):
        """commits the shot to the database
        """
        logger.debug("saving shot to the database")
        if self not in db.session:
            db.session.add(self)
        
        db.session.commit()

    @synonym_for("_code")
    @property
    def code(self):
        """Returns the code of this shot by composing the
         :attr:`~oyProjectManager.models.shot.Shot.number` with the
        :attr:`~oyProjectManager.models.project.Project.shot_prefix` attribute
        of the :class:`~oyProjectManager.models.project.Project` ::
          
          >> shot.number
            "1"
          >> shot.code
            "SH001"
          >> shot.number
            "12A"
          >> shot.code
            "SH012A"
        """
        
        # TODO: there is a weird situation here need to fix it later by
        #       introducing a new variable to the Project
        if "-" in self.number or "_" in self.number:
            return self.project.shot_number_prefix + self.number
        else:
            number = re.sub(r"[A-Z]+", "", self.number)
            alter = re.sub(r"[0-9]+", "", self.number)
            
            return self.project.shot_number_prefix +\
               number.zfill(self.project.shot_number_padding) + alter
    
    @validates("handle_at_start")
    def _validate_handles_at_start(self, key, handle_at_start):
        """validates the given handle_at_start value
        """
        
        if not isinstance(handle_at_start, int):
            raise TypeError("Shot.handle_at_start should be an instance of "
            "integer not %s" % type(handle_at_start))
        
        if handle_at_start < 0:
            raise ValueError("Shot.handle_at_start can not be a negative "
                             "value")
        
        # the total count of the handles can not be bigger than duration-1
        if self.handle_at_end is not None:
            if handle_at_start + self.handle_at_end > self.duration - 1:
                raise ValueError("Shot.handle_at_start + Shot.handle_at_end "
                                 "can not be bigger than Shot.duration - 1")

        return handle_at_start
    
    @validates("handle_at_end")
    def _validate_handle_at_end(self, key, handle_at_end):
        """validates the given handle_at_end value
        """
        
        if not isinstance(handle_at_end, int):
            raise TypeError("Shot.handle_at_end should be an instance of "
            "integer not %s" % type(handle_at_end))
        
        if handle_at_end < 0:
            raise ValueError("Shot.handle_at_end can not be a negative "
                             "value")
        
        # the total count of the handles can not be bigger than duration-1
        if self.handle_at_start is not None:
            if self.handle_at_start + handle_at_end > self.duration - 1:
                raise ValueError("Shot.handle_at_start + Shot.handle_at_end "
                                 "can not be bigger than Shot.duration - 1")

        return handle_at_end
