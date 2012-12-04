# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import re
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import synonym, validates

from oyProjectManager import db
from oyProjectManager.models.entity import VersionableBase

# create a logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class Asset(VersionableBase):
    """Manages Assets in a given :class:`~oyProjectManager.models.proejct.Project`
    
    Assets are the data created to finish a
    :class:`~oyProjectManager.models.project.Project`. It can be a Character or a
    Vehicle or anything that participate in to a
    :class:`~oyProjectManager.models.shot.Shot`.
    
    Assets have :class:`~oyProjectManager.models.version.Versions`\ s to hold
    every change made to that asset file.
    
    The name attribute will be copied to the code attribute if the code
    argument is None or an empty string.
    
    :param project: The :class:`~oyProjectManager.models.project.Project`
      instance that this Asset belongs to. It is not possible to initialize an
      Asset without defining its
      :class:`~oyProjectManager.models.project.Project`.
    
    :param name: The name of this asset. It can not be None or an empty string.
      Anything is possible to be used as a name but it is recommended to keep
      it brief. The name attribute will be formatted and the result will be
      copied to the :attr:`~oyProjectManager.models.asset.Asset.code`
      attribute. The name should be unique among all the asset in the current
      :class:`~oyProjectManager.models.project.Project`.
      
      The following rules will apply for the formatting of the name:
        
        * Spaces are allowed.
        * It should start with an upper case letter (A-Z)
        * Only the following characters are allowed (-\_ a-zA-Z0-9)
    
    :param code: The code of this asset. If it is given as None or empty string
      the value will be get from the name attribute.
      
      The following rules will apply for the formatting of the code:
      
        * No spaces are allowed, all the spaces will be replaced with "_"
          (underscore) characters
        * It should start with upper case letter (A-Z)
        * Only the following characters are allowed (a-zA-Z0-9\_)
        * All the "-" (minus) signs are converted to "_" (under score)
      
      If the code becomes an empty string after formatting a ValueError will be
      raised. The code should be unique among all the Assets in the current
      :class:`~oyProjectManager.models.project.Project`.
    
    :param type: The ``type`` of this asset. Can be used to distinguish
      different types of assets like 'Prop', 'Character', 'Vehicle' etc. If
      given as None the default value (default_asset_type_name) from the config
      will be used.
    """

    __tablename__ = "Assets"
    __table_args__  = (
        {"extend_existing":True}
    )
    
    __mapper_args__ = {"polymorphic_identity": "Asset"}
    
    asset_id = Column("id", Integer, ForeignKey("Versionables.id"),
                      primary_key=True)
    
    type = Column(String(256))
    
    def __init__(self, project, name, code=None, type=None):
        self._project = project
        self.name = name
        self.code = code
        self.type = type
    
    def __eq__(self, other):
        """equality operator
        """
        return isinstance(other, Asset) and self.name == other.name and \
            self.project==other.project
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
        """the string representation of the object
        """
        return "<Asset, %s in %s>" % (self.name, self.project.name)
    
    def _validate_code(self, code):
        """validates the given code value
        """
        if code is None:
            code = self.name
        
        if not isinstance(code, (str, unicode)):
            raise TypeError("Asset.code should be an instance of string or "
                            "unicode not %s" % type(code))
        
        if code is "":
            raise ValueError("The Asset.code can not be an empty string")
        
        # strip the code
        code = code.strip()
        # remove unnecessary characters from the string
        code = re.sub("([^a-zA-Z0-9\s_]+)", r"", code)
        # remove all the characters from the beginning which are not alphabetic
        code = re.sub("(^[^a-zA-Z0-9]+)", r"", code)
        # substitute all spaces with "_" characters
        code = re.sub("([\s])+", "_", code)
        
        # check if the code became empty string after validation
        if code is "":
            raise ValueError("Asset.code is not valid after validation")
        
        # convert the first letter to uppercase
        code = code[0].upper() + code[1:]
        
        return code
        
    def _code_getter(self):
        """The nicely formatted version of the
        :attr:`~oyProjectManager.models.asset.Asset.name` attribute
        """
        return self._code
    
    def _code_setter(self, code):
        """Sets the code of this Asset instance
        """
        self._code = self._validate_code(code)

    code = synonym(
        "_code",
        descriptor=property(
            _code_getter,
            _code_setter
        )
    )
    
    def _validate_name(self, name):
        """validates the given name value
        """
        if name is None:
            raise TypeError("")
        
        if not isinstance(name, (str, unicode)):
            raise TypeError("Asset.name should be an instance of string or "
                            "unicode not %s" % type(name))
        
        if name is "":
            raise ValueError("The Asset.name can not be an empty string")
        
        # strip the name
        name = name.strip()
        # remove unnecessary characters from the string
        name = re.sub("([^a-zA-Z0-9\s_-]+)", r"", name)
        # remove all the characters from the beginning which are not alphabetic
        name = re.sub("(^[^a-zA-Z0-9]+)", r"", name)
#        # substitute all spaces with "_" characters
#        name = re.sub("([\s])+", "_", name)
        
        # check if the name became empty string after validation
        if name == "":
            raise ValueError("Asset.name is not valid after validation")
        
        # convert the first letter to uppercase
        name = name[0].upper() + name[1:]
        
        return name
    
    def _name_getter(self):
        """getter for the name attribute
        """
        return self._name
    
    def _name_setter(self, name):
        """setter for the name attribute
        """
        name = self._validate_name(name)
        self._name = name
    
    name = synonym(
        "_name",
        descriptor=property(
            _name_getter,
            _name_setter,
            doc="""The name of this Asset instance, try to be brief."""
        )
    )
    
    def save(self):
        """saves the asset to the related projects database
        """
        if db.session is None:
            db.setup()
        
        if self not in db.session:
            logger.debug("adding %s to the session" % self)
            db.session.add(self)
        
        logger.debug("saving the asset %s" % self)
        db.session.commit()
    
    @validates('type')
    def _validate_type(self, key, type):
        """validates the given type value
        """
        if type is None:
            from oyProjectManager import conf
            type = conf.default_asset_type_name
        
        if not isinstance(type, (str, unicode)):
            raise TypeError('Asset.type should be an instance of string or '
                            'unicode not %s' % type.__class__.__name__)
        
        # strip the code
        type = type.strip()
        # remove unnecessary characters from the string
        type = re.sub("([^a-zA-Z0-9\s_]+)", r"", type)
        # remove all the characters from the beginning which are not alphabetic
        type = re.sub("(^[^a-zA-Z0-9]+)", r"", type)
        # substitute all spaces with "_" characters
        type = re.sub("([\s])+", "_", type)
        
        # check if the code became empty string after validation
        if type is "":
            raise ValueError("Asset.type is not valid after validation")
        
        # convert the first letter to uppercase
        type = type[0].upper() + type[1:]
        return type
