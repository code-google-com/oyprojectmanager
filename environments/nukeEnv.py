import os
import nuke
import oyAuxiliaryFunctions as oyAux
from oyProjectManager.dataModels import assetModel, projectModel, abstractClasses



__version__ = "9.12.26"






########################################################################
class NukeEnvironment(abstractClasses.Environment):
    """the nuke environment class
    """
    
    
    
    #----------------------------------------------------------------------
    def save(self):
        """"the save action for nuke environment
        
        uses Nukes own python binding
        """
        
        # set the extension to 'nk'
        self._asset.setExtension( 'nk' )
        nuke.scriptSaveAs( self._asset.getFullPath() )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def export(self):
        """the export action for nuke environment
        """
        
        # set the extension to 'nk'
        self._asset.setExtension('nk')
        
        nuke.nodeCopy( self._asset.getFullPath() )
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def open_(self, force=False):
        """the open action for nuke environment
        """
        nuke.scriptOpen( self._asset.getFullPath() )
        return True
    
    
    
    #----------------------------------------------------------------------
    def import_(self):
        """the import action for nuke environment
        """
        nuke.nodePaste( self._asset.getFullPath() )
        return True
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """gets the file name from nuke
        """
        fullPath = path = fileName = None
        fullPath = nuke.toNode("root").name()
        
        if fullPath != None and fullPath != '':
            # for winodws replace the path seperator
            if os.name == 'nt':
                fullPath = fullPath.replace('/','\\')
            
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
        else:
            
            # use the last file from the recent file list
            fullPath = nuke.recentFile(1)
            
            # for winodws replace the path seperator
            if os.name == 'nt':
                fullPath = fullPath.replace('/','\\')
            
            fileName = os.path.basename( fullPath )
            path = os.path.dirname( fullPath )
            
        return fileName, path
    
    
    
    
    ##----------------------------------------------------------------------
    #def setRootName():
        #"""sets the root name variable
        #"""
        
        #rootNode = nuke.toNode("root")
        
        ## get the name and replace \ with / characters
        
        #rootName = rootNode.name()
        
        #myDict = dict()
        #myDict[u'\\'] = u'/'
        
        #rootName = rootName.prelace('\\','/') 
        
        #rootNode.setName( rootName )
        
        #return rootName