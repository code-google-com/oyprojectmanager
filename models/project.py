import os
import oyAuxiliaryFunctions as oyAux
import database, sequence, tools.cache



########################################################################
class Project(object):
    """Project object to help manage project data
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, projectName, databaseObj = None):
        
        if databaseObj == None:
            self._database = database.Database()
        else:
            self._database = databaseObj
        
        self._name = oyAux.file_name_conditioner( projectName )
        self._path = ''
        self._fullPath = ''
        
        self._initPathVariables()
        
        self._sequenceList = []
        
        self._exists = self.exists()
    
    
    
    #----------------------------------------------------------------------
    def _initPathVariables(self):
        self._path = self._database._projectsFolderFullPath
        self._fullPath = os.path.join( self._path, self._name)
    
    
    
    #----------------------------------------------------------------------
    def create(self):
        """creates the project
        """
        # check if the folder allready exists
        oyAux.createFolder( self._fullPath )
        self._exists = self.exists()
    
    
    
    #----------------------------------------------------------------------
    def createSequence(self, sequenceName, shots ):
        """creates a sequence and returns the sequence object
        """
        newSequence = sequence.Sequence( self, sequenceName )
        newSequence.addShots( shots )
        newSequence.create()
        
        return newSequence
    
    
    
    #----------------------------------------------------------------------
    @tools.cache.CachedMethod
    def getSequenceNames(self):
        """returns the sequence names of that project
        """
        self.updateSequenceList()
        return self._sequenceList
    
    
    
    #----------------------------------------------------------------------
    @tools.cache.CachedMethod
    def getSequences(self):
        """returns the sequences as sequence objects
        
        don't use it offen, because it causes the system to parse all the sequence settings
        for all the sequences under that project
        
        it is now using the caching mechanism use it freely
        """
        
        self.updateSequenceList()
        sequences = [] * 0
        
        for sequenceName in self._sequenceList:
            sequences.append( sequence.Sequence( self, sequenceName) )
        
        return sequences
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self):
        """updates the sequenceList variable
        """
        self._sequenceList = os.listdir( self._fullPath )
        self._sequenceList.sort()
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getDatabase(self):
        """returns the current project database object
        """
        return self._database
    
    
    
    #----------------------------------------------------------------------
    def setDatabase(self, database ):
        """sets the project database object
        """
        
        self._database = database
        
        # reset the path variables
        self._initPathVariables
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """ returns the name of the project
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the project folder exists
        """
        
        return os.path.exists( self._fullPath )
    
    
    
    ##----------------------------------------------------------------------
    #def setProject(self, projectName):
        #"""renews the object to a new project
        #"""
        
        #self = Project( projectName )