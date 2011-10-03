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
from oyProjectManager.models.project import Project


class BackUp(object):
    """Holds information about the backup process.
    
    :param project: The name of the project to be backed up or the
      :class:`~oyProjectManager.models.project.Project` instance showing the 
      project to be backed up. None or empty string will raise TypeError and
      ValueError respectively.
    
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
#      :class:`~oyProjectManager.models.project.Sequence` instances showing 
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
        
        self._project = None
        
        if project is None:
            raise TypeError
        
        if project == "":
            raise ValueError


    def doBackup(self):
        """Does the backup process.
        
        Calls ``rsync`` with the appropriate filters. Creates the output path
        if it doesn't exists.
        """

        pass



    @property
    def project(self):
        """The project to be backed up.
        
        It is an instance of :class:`~oyProjectManager.models.project.Project`.
        """
        return self._project
    
    @project.setter
    def project(self, project_in):
        """setter of the project attribute
        """
        
        if not isinstance(project_in, Project):
            raise TypeError("BackUp.project should be an instance of"
                            "oyProjectManager.models.project.Project instance")
        
        if project_in == "":
            raise ValueError
        
        self._project = project_in

    
#    def sequences(self):
#        """The sequences to be backed up.
#        
#        It is a list of :class:`~oyProjectManager.models.project.Sequence` 
#        instances. If it is set to an empty list or None all the sequences in
#        the project are going to be backed up.
#        """
#
#        pass
    
    
    def num_of_versions(self):
        """the number of versions of latest Nuke files.
        
        It is an integer.
        """
        
        pass
    
    
    def output(self):
        """A string showing the output of the backed up files.
        
        If it is set to None a TypeError will be raised and if it is set to 
        an empty string a ValueError will be raised.
        """
        
        pass
        
        
        
