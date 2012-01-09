# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of oyProjectManager and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
"""
The backup script for the system.

It accepts a ``project`` name and an ``output_path`` which is the output of 
the filtered files.

The system creates filter rules to be used with ``rsync`` command and then calls
the ``rsync`` command on the server.

Because the pipeline ends at a Nuke file, all the source files which needs to
be backed up are listed in this nuke (*.nk) file. So the script searches for the
latest versions of nuke files, and if a ``-nv n`` parameters is also passed, 
then the last ``n`` versions will be investigated for source files.

Script will search for, Read, ReadGeo, ReadGeo2, Write, WriteGeo nodes and will
use the path value listed in the ``file`` attribute of those nodes.

If the file path is relative and a project_dir is present in the nuke file 
than the path will be converted to an absolute path.

:arg --project, -p: The name of the project. It should match the exact project 
  name otherwise it will raise a ValueError.

:arg --extra_filter_rules, -ef: a file which is holding extra filter rules 
  Can be skipped.

:arg --number_of_versions, -nv: the number of versions to be used in backup 
  process. Default value is 1.

:arg --output, -o: the output of the backed up files.

Examples::
  
  backup -p ProjectName -o /mnt/M/JOBs_Backup
  # creates a backup_filter file in the path that the script is executed
  
  # No output will raise RuntimeError:
  backup -p ProjectName
  # raises RuntimeError

"""

# TODO: add ability to backup individual sequences
#:arg --sequence, -s: The name of the sequence. It should match the exact 
#  sequence name, and if skipped, all the sequences under the given project 
#  will be filtered and backed up.
from oyProjectManager.core.models import Project


class BackUp(object):
    """Holds information about the backup process.
    
    :param project: The name of the project to be backed up or the
      :class:`~oyProjectManager.core.models.Project` instance showing the 
      project to be backed up. None or empty string will raise TypeError and
      ValueError respectively. If given as string a new
      :class:`~oyProjectManager.core.models.Project` instance will be created
      and hold in the :attr:`~oyProjectManager.utils.backup.BackUp.project`
      attribute.
    
    :param extra_filter_rules: A path of a text file which holds the extra 
      filter rules. Can be skipped.
    
    :param number_of_versions: The number of latest Nuke script version to be
      searched for inputs. Setting the number_of_versions to a negative value
      will result all the versions of the Nuke files to be used. Default value
      is 1.
    
    :param output: The output of the backed up files. If skipped a ValueError
      will be raised
    """
    
#   TODO: add individual sequences
#    :param sequences: A list of strings or
#      :class:`~oyProjectManager.core.models.Sequence` instances showing 
#      the sequences to be backed up. All the sequences should be valid for the
#      given project. If one of the sequences doesn't belong to the given 
#      project, a ValueError will be raised. Can be skipped or can be None then 
#      all the sequences in the project will be used.
    
    

    #----------------------------------------------------------------------
    def __init__(self,
                 project=None,
                 output=None,
                 number_of_versions=None,
                 extra_filter_rules=None):
        
        self._project = self._validate_project(project)
        self._extra_filter_rules = \
            self._validate_extra_filter_rules(extra_filter_rules)
        self._output = self._validate_output(output)
        self._number_of_versions = \
            self._validate_number_of_versions(number_of_versions)
        

    def doBackup(self):
        """Does the backup process.
        
        Calls ``rsync`` with the appropriate filters. Creates the output path
        if it doesn't exists.
        """
        
        print self.project
        print self.project.full_path
        
        # get the last compositing
        for sequence in self.project.sequences():
            print sequence.name
            print sequence.full_path
            comp_Assets = sequence.getAllAssetsForType("COMP")
            print comp_Assets
        
    
    
    def _validate_project(self, project):
        """validates the given project value
        """
        
        if not isinstance(project, Project) and \
           not isinstance(project, str):
            raise TypeError("BackUp.project should be an instance of"
                            "oyProjectManager.core.models.Project instance")
        
        if project == "":
            raise ValueError
        
        if isinstance(project, (str, unicode)):
            project = Project(name=project)
        
        if not project.exists:
            raise RuntimeError("The project doesn't exists, so it can not be "
                               "backup")
        
        return project
    
    def _validate_extra_filter_rules(self, extra_filter_rules):
        """validates the given extra_filter_rules
        """
        
        if extra_filter_rules is None:
            extra_filter_rules = ""
        
        if not isinstance(extra_filter_rules, (str, unicode)):
            raise TypeError("extra_filter_rules should be a string "
                            "showing the path of the extra filter rules")
        
        return extra_filter_rules
    
    def _validate_output(self, output):
        """validates the given output value
        """
        
        if output is None:
            raise TypeError("output argument can not be None")
        
        if output == "":
            raise ValueError("output argument can not be empty string")
        
        if not isinstance(output, (str, unicode)):
            raise TypeError("output argument should be a string")
        
        return output
    
    def _validate_number_of_versions(self, number_of_versions):
        """validates the given number_of_versions value
        """
        
        if number_of_versions is None:
            number_of_versions = 1
        
        if not isinstance(number_of_versions, int):
            raise TypeError("number_of_versions should be an integer")
        
        return number_of_versions
    
    @property
    def project(self):
        """The project to be backed up.
        
        It is an instance of :class:`~oyProjectManager.core.models.Project`.
        """
        return self._project
    
    @project.setter
    def project(self, project):
        """setter of the project attribute
        """
        self._project = self._validate_project(project)
    
    @property
    def extra_filter_rules(self):
        """a string showing the file path of the extra filter rules which is
        going to be used with the rsync
        """
        
        return self._extra_filter_rules
    
    @extra_filter_rules.setter
    def extra_filter_rules(self, extra_filter_rules):
        """setter for the extra_filter_rules
        """
        self._extra_filter_rules = \
            self._validate_extra_filter_rules(extra_filter_rules)
    
    @property
    def num_of_versions(self):
        """the number of versions of latest Nuke files.
        
        It is an integer.
        """
        
        return self._number_of_versions
    
    @num_of_versions.setter
    def num_of_versions(self, num_of_versions):
        """the setter for the number of versions attribute
        """
        self._number_of_versions = \
            self._validate_number_of_versions(num_of_versions)
    
    @property
    def output(self):
        """A string showing the output of the backed up files.
        
        If it is set to None a TypeError will be raised and if it is set to 
        an empty string a ValueError will be raised.
        """
        return self._output
    
    @output.setter
    def output(self, output):
        """the output setter
        """
        self._output = self._validate_output(output)
    
