# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import validates
from oyProjectManager.db.declarative import Base


def make_plural(name):
    """Returns the plural version of the given name argument.
    
    Originally developed for Stalker
    """
    plural_name = name + "s"

    if name[-1] == "y":
        plural_name = name[:-1] + "ies"
    elif name[-2:] == "ch":
        plural_name = name + "es"
    elif name[-1] == "f":
        plural_name = name[:-1] + "ves"
    elif name[-1] == "s":
        plural_name = name + "es"

    return plural_name


def create_secondary_table(
        primary_cls_name,
        secondary_cls_name,
        primary_cls_table_name,
        secondary_cls_table_name,
        secondary_table_name=None
):
    """creates any secondary table
    """

    plural_secondary_cls_name = make_plural(secondary_cls_name)

    # use the given class_name and the class_table
    if not secondary_table_name:
        secondary_table_name = \
            primary_cls_name + "_" + plural_secondary_cls_name

    # check if the table is already defined
    if secondary_table_name not in Base.metadata:
        secondary_table = Table(
            secondary_table_name, Base.metadata,
            Column(
                primary_cls_name.lower() + "_id",
                Integer,
                ForeignKey(primary_cls_table_name + ".id"),
                primary_key=True,
            ),

            Column(
                secondary_cls_name.lower() + "_id",
                Integer,
                ForeignKey(secondary_cls_table_name + ".id"),
                primary_key=True,
            )
        )
    else:
        secondary_table = Base.metadata.tables[secondary_table_name]

    return secondary_table


class IOMixin(object):
    """Adds the ability to be able to hold relations to :class:`~oyProjectManager.models.link.FileLink` instances.

    IOMixin adds the ability of being related to
    :class:`~oyProjectManager.models.link.FileLink` instances as ``inputs`` and
    ``outputs``. It is different than a
    :class:`~oyProjectManager.models.version.Version` holding a
    :class:`~oyProjectManager.models.link.FileLink` for the source file link
    and different again from a Version holding a reference to another Version
    instances.

    Inputs are external files used to create the outputs of the mixed in class.
    It can be and EDL file for a Project or Sequence or can be a texture file
    for an Asset Version or can be a image file sequence for a Shot Version
    which is a composition scene may be.

    :param inputs: A list of :class:`~oyProjectManager.models.link.FileLink`
      instances holding the inputs (texture, image sequence, video, text etc.)
      those are considered as inputs to this mixed in class.

    :type inputs: a list of :class:`~oyProjectManager.models.link.FileLink`
      instances.

    :param outputs: A list of :class:`~oyProjectManager.models.link.FileLink`
      instances holding the outputs of this mixed in class. Outputs can be a
      sequence of images lets say for a Shot Version.

    :type inputs: a list of :class:`~oyProjectManager.models.link.FileLink`
      instances.
    """

    def __init__(self, inputs=None, outputs=None):
        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []
        self.inputs = inputs
        self.outputs = outputs

    @declared_attr
    def inputs(cls):
        secondary_table = create_secondary_table(
            cls.__name__, 'FileLink', cls.__tablename__, 'FileLinks',
            cls.__name__ + '_Inputs'
        )
        # return the relationship
        return relationship('FileLink', secondary=secondary_table)

    @validates('inputs')
    def _validate_inputs(self, key, input_):
        """validates the given input value
        """
        from oyProjectManager.models.link import FileLink

        if not isinstance(input_, FileLink):
            raise TypeError('%s.inputs should be all FileLink instances not, '
                            '%s' % (self.__class__.__name__,
                                    input_.__class__.__name__ ))
        return input_

    @declared_attr
    def outputs(cls):
        secondary_table = create_secondary_table(
            cls.__name__, 'FileLink', cls.__tablename__, 'FileLinks',
            cls.__name__ + '_Outputs'
        )
        # return the relationship
        return relationship('FileLink', secondary=secondary_table)

    @validates('outputs')
    def _validate_outputs(self, key, output):
        """validates the given output value
        """
        from oyProjectManager.models.link import FileLink

        if not isinstance(output, FileLink):
            raise TypeError('%s.outputs should be all FileLink instances not, '
                            '%s' % (self.__class__.__name__,
                                    output.__class__.__name__ ))
        return output


#class ReferenceMixin(object):
#    """Adds the ability to hold references to the mixed in class.
#    
#    References are :class:`~oyProjectManager.models.link.FileLink` instances.
#    Any class mixed in with the ReferenceMixin will be able to hold external
#    information.
#    
#    :param list references: A list of
#      :class:`~oyProjectManager.models.link.FileLink` instances. It can be a
#      Link which is a file sequence or can be a web page address.
#    """
#    pass
    
