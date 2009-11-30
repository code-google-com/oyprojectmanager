import os, re
import oyAuxiliaryFunctions as oyAux



__version__ = "9.11.17"



########################################################################
class Asset(object):
    """to work properly it needs a valid project and sequence objects
    
    an Assets folder is something like that:
    
    ProjectsFolder / ProjectName / SequenceName / TypePath / BaseName / assetFileName
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, prj, seq, fileName=None):
        
        self._parentProject = prj
        self._parentSequence = seq
        
        # asset metadata
        # info variables
        
        # baseName could represent a shot string
        self._baseName = None
        self._subName = None
        self._type = None
        self._typeName = None
        self._rev = None
        self._revString = None
        self._ver = None
        self._verString = None
        self._userInitials = None
        self._notes = None
        self._extension = u''
        
        # path variables
        self._fileName = None #os.path.splitext(fileName)[0] # remove the extension
        self._path = None
        self._fullPath = None
        
        self._hasFullInfo = False
        self._hasBaseInfo = False
        
        self._dataSeparator = u'_'
        
        if fileName != None:
            self._fileName  = unicode( os.path.splitext(unicode(fileName))[0] ) # remove the extension
            self._extension = unicode( os.path.splitext(unicode(fileName))[1] ).split( os.path.extsep )[-1] # remove the . in extension
            self.guessInfoVariablesFromFileName()
        
        self._exists = False
        self._baseExists = False
        
        self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def setInfoVariables(self, **keys):
        """ sets the info variables with a dictionary
        
        the minimum valid info variables are:
        
        baseName
        subName
        typeName
        
        and the rest are:
        rev or revString
        ver or verString
        userInitials
        notes (optional)
        extension (optional for most of the methods)
        """
        #assert(isinstance(keys,dict))
        
        if keys.has_key('baseName'):
            self._baseName = keys['baseName']
        
        if keys.has_key('subName'):
            self._subName = keys['subName']
        
        if keys.has_key('typeName'):
            self._typeName = keys['typeName']
            self._type = self._parentSequence.getAssetTypeWithName( self._typeName )
        
        # convert revision and version strings to number
        if keys.has_key('revString'):
            self._revString = keys['revString']
            self._rev = self._parentSequence.convertToRevNumber( self._revString )
        elif keys.has_key('rev'):
            self._rev = int( keys['rev'] )
            self._revString = self._parentSequence.convertToRevString( self._rev )
        
        if keys.has_key('verString'):
            self._verString = keys['verString']
            self._ver = self._parentSequence.convertToVerNumber( self._verString )
        elif keys.has_key('ver'):
            self._ver = int( keys['ver'])
            self._verString = self._parentSequence.convertToVerString( self._ver )
        
        if keys.has_key('userInitials'):
            self._userInitials = keys['userInitials']
        
        if keys.has_key('notes'):
            self._notes = keys['notes']
        
        if keys.has_key('extension'):
            self._extension = keys['extension']
        
        if not self._parentSequence._noSubNameField:
            if self._baseName != None and self._subName != None and self._type != None and \
               self._baseName != '' and self._subName != '' and self._type != '':
                self._hasBaseInfo = True
                if self._rev != None and self._ver != None and self._userInitials != None and \
                   self._rev != '' and self._ver != '' and self._userInitials != '':
                    self._hasFullInfo = True
        else:  # remove this block when the support for old version becomes obsolute
            if self._baseName != None and self._type != None and \
               self._baseName != '' and self._type != '':
                self._hasBaseInfo = True
                if self._rev != None and self._ver != None and self._userInitials != None and \
                   self._rev != '' and self._ver != '' and self._userInitials != '':
                    self._hasFullInfo = True
        
        # get path variables
        self.setPathVariables()
        self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def getInfoVariables(self):
        """returns the info variables as a dictionary
        """
        
        infoVars = dict()
        infoVars['baseName'] = self._baseName
        infoVars['subName'] = self._subName
        infoVars['typeName'] = self._type.getName()
        infoVars['rev'] = self._rev
        infoVars['revString'] = self._revString
        infoVars['ver'] = self._ver
        infoVars['verString'] = self._verString
        infoVars['userInitials'] = self._userInitials
        infoVars['notes'] = self._notes
        infoVars['fileName'] = self._fileName
        
        return infoVars
    
    
    
    #----------------------------------------------------------------------
    def guessInfoVariablesFromFileName(self):
        """tries to get all the info variables from the file name
        """
        
        # check if there is a valid project
        if self._parentProject == None or self._parentSequence == None:
            return
        
        parts = self._fileName.split( self._dataSeparator )
        
        if not self._parentSequence._noSubNameField:
            if len(parts) < 5:
                return
            
            try:
                
                self._baseName     = parts[0]
                self._subName      = parts[1]
                self._typeName     = parts[2]
                self._revString    = parts[3]
                self._verString    = parts[4]
                self._userInitials = parts[5]
            except IndexError:
                # the given file name is not valid
                self._fileName = ''
                return
            
            if len(parts) > 6: # there should be a notes part
                self._notes = self._dataSeparator.join( parts[6:len(parts)] )
            else:
                self._notes = ""
        
        else: # remove this block when the support for old version becomes obsolute
            if len(parts) < 4:
                return
            
            self._baseName     = parts[0]
            self._typeName     = parts[1]
            self._revString    = parts[2]
            self._verString    = parts[3]
            self._userInitials = parts[4]
            
            if len(parts) > 5: # there should be a notes part
                self._notes = self._dataSeparator.join( parts[5:len(parts)] )
            else:
                self._notes = ""
        
        # get the type object
        self._type = self._parentSequence.getAssetTypeWithName( self._typeName )
        
        try:
            self._rev = self._parentSequence.convertToRevNumber( self._revString )
            self._ver = self._parentSequence.convertToVerNumber( self._verString )
        except ValueError:
            # the pattern is not compatible with the current project
            return
        
        self._hasFullInfo = self._hasBaseInfo = True
        
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def setPathVariables(self):
        """sets path variables
        needs the info variables to be set before
        """
        
        # if it has just the base info update some of the variables
        if self._hasBaseInfo:
            seqFullPath = self._parentSequence.getFullPath()
            
            typeFolder = self._type.getPath()
            #try:
                #typeFolder = self._type.getPath()
            #except AttributeError:
                #justCnt = 20
                #print "fileName".ljust( justCnt ), ": ", self._fileName
                #print "baseName".ljust( justCnt ), ": ", self._baseName
                #print "subName".ljust( justCnt ), ": ", self._subName
                #print "typeName".ljust( justCnt ), ": ", self._typeName
                #print "revString".ljust( justCnt ), ": ", self._revString
                #print "verString".ljust( justCnt ), ": ", self._verString
                #print "userInitials".ljust( justCnt ), ": ", self._userInitials
                #print "parent sequence".ljust( justCnt ), ": ", self._parentSequence.getName()
                #print "parent project".ljust( justCnt ), ": ", self._parentProject.getName()
                #raise
            
            self._path = os.path.join( seqFullPath, typeFolder)
            self._path = os.path.join( self._path, self._baseName )
            
            # if it has full info update the rest of the variables
            if self._hasFullInfo:
                
                self._fileName = self.getFileName()
                self._fullPath = os.path.join( self._path, self._fileName )
                
                self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def setExtension(self, extension):
        """sets the extension of the asset object
        """
        
        #assert(isinstance(extension,str))
        
        # remove any extension separetors at from the input extension
        finalExtension = extension.split( os.path.extsep )[-1]
        
        self._extension = finalExtension
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def getFullPath(self):
        """returns the fullPath of the asset
        """
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    def getParentSequence(self):
        """returns the parent sequence
        """
        #from oyProjectManager.dataModels import projectModel
        #assert(isinstance(self._parentSequence, projectModel.Sequence ) )
        return self._parentSequence
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """retrurns the path of the asset
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def getExtension(self):
        """returns the extension
        """
        return self._extension
    
    
    
    #----------------------------------------------------------------------
    def getFileName(self):
        """gathers the info variables to a fileName
        """
        
        #if not self.isValidAsset():
            #return None
        
        #parts = [] * 0
        #parts.append( self._baseName )
        
        #if not self._parentSequence._noSubNameField:
            #parts.append( self._subName )
        
        #parts.append( self._type.getName() )
        #parts.append( self._revString )
        #parts.append( self._verString )
        #parts.append( self._userInitials )
        
        ## check if there is a note
        #if self._notes != None and self._notes != '':
            #parts.append( self._notes )
        
        #fileName = self._dataSeparator.join(parts)
        
        fileName = self.getFileNameWithoutExtension()
        
        if self._extension != None and self._extension != '':
            fileName = fileName + os.extsep + self._extension
        
        return fileName
    
    
    
    #----------------------------------------------------------------------
    def getFileNameWithoutExtension(self):
        """returns the file name without extension
        """
        
        if not self.isValidAsset():
            return None
        
        parts = [] * 0
        parts.append( self._baseName )
        
        if not self._parentSequence._noSubNameField:
            parts.append( self._subName )
        
        parts.append( self._type.getName() )
        parts.append( self._revString )
        parts.append( self._verString )
        parts.append( self._userInitials )
        
        # check if there is a note
        if self._notes != None and self._notes != '':
            parts.append( self._notes )
        
        fileName = self._dataSeparator.join(parts)
        
        return fileName
    
    
    
    #----------------------------------------------------------------------
    def getPathVariables(self):
        """returns the path variables which are
        fullPath
        path
        fileName
        """
        return self.getFullPath(), self.getPath(), self.getFileName()
    
    
    
    #----------------------------------------------------------------------
    def getAllVersions(self):
        """returns all versions as a list of asset objects
        """
        # return if we can't even get some little information
        if not self._baseExists and not self._hasBaseInfo:
            return []
        
        # use the Sequence object instead of letting the Asset object to dive in to the
        # file system to get other versions
        
        #import projectModel
        sProj = self._parentProject
        sSeq = self._parentSequence
        #assert(isinstance(selfseq,projectModel.Sequence))
        
        assetVersionNames = self.getAllVersionNames()
        
        sProjList = [sProj] * len(assetVersionNames)
        sSeqList = [sSeq] * len(assetVersionNames)
        
        return map(Asset, sProjList, sSeqList, assetVersionNames)
    
    
    
    #----------------------------------------------------------------------
    def getAllVersionNames(self):
        """returns all version names for that asset as a list of string
        """
        
        if not self._baseExists and not self._hasBaseInfo:
            return []
        
        sSeq = self._parentSequence
        
        sSeqFAN = sSeq.filterAssetNames
        sSeqGAAFNFT = sSeq.getAllAssetFileNamesForType
        
        typeName = self._typeName
        baseName = self._baseName
        subName = self._subName
        
        if not self._parentSequence._noSubNameField:
            return sorted([ assetFileName for assetFileName in sSeqFAN( sSeqGAAFNFT( typeName ), baseName=baseName, subName=subName ) ])
        else:
            return sorted([ assetFileName for assetFileName in sSeqFAN( sSeqGAAFNFT( typeName ), baseName=baseName ) ] )
    
    
    
    #----------------------------------------------------------------------
    def _getCritiqueName(self):
        """returns the critique part of the asset name, which is:
        BaseName_SubName_TypeName
        """
        
        if not self._parentSequence._noSubNameField:
            if self._baseName == None or self._subName == None or self._typeName == None:
                return None
            
            return self._dataSeparator.join( [self._baseName, self._subName, self._typeName ] )
        
        else: # remove this block when the support for old version becomes obsolute
            if self._baseName == None or self._typeName == None:
                return None
            
            return self._dataSeparator.join( [self._baseName, self._typeName ] )
    
    
    
    #----------------------------------------------------------------------
    def getSequenceFullPath(self):
        """returns the parent sequence full path
        """
        #from oyProjectManager.dataModels import projectModel
        #assert(isinstance(self._parentSequence, projectModel.Sequence))
        return self._parentSequence.getFullPath()
    
    
    
    ##----------------------------------------------------------------------
    #def getProjectPath(self):
        #"""returns the parent project path
        
        #beware that it is the project path not the sequence path
        #"""
        #from oyProjectManager.dataModels import projectModel
        #assert(isinstance(self._parentProject, projectModel.Project))
        #return self._parentProject.getFullPath()
    
    
    
    #----------------------------------------------------------------------
    def getLatestVersion(self):
        """returns the lastest version of an asset as an asset object and the number as an integer
        if the asset file doesn't exists yet it returns None, None
        """
        
        if not self._baseExists:
            return None, None
        
        allVersions = self.getAllVersions()
        
        if len(allVersions) == 0:
            return None, None
        
        maxVerNumber = -1
        currentVerNumber = -1
        maxVerAsset = self
        
        for asset in allVersions:
            currentVerNumber = asset.getVersionNumber()
            
            if currentVerNumber > maxVerNumber:
                maxVerNumber = currentVerNumber
                maxVerAsset = asset
        
        return maxVerAsset, maxVerNumber
    
    
    
    #----------------------------------------------------------------------
    def getLatestVersion2(self):
        """the second version of the older one, it uses file names instead of
        asset objects.
        
        returns the latest version of an asset as an asset object and the
        number as an integer
        """
        
        if not self._baseExists:
            return None, None
        
        # get all version names
        allVersionNames = self.getAllVersionNames()
        
        # return the last one as an asset
        if len(allVersionNames) > 0:
            assetObj = Asset( self._parentProject, self._parentSequence, allVersionNames[-1] )
        else:
            return None, None
        
        return assetObj, assetObj.getVersionNumber()
    
    
    
    #----------------------------------------------------------------------
    def getLatestRevision(self):
        """returns the latest revision of an asset as an asset object and the number as an integer
        if the asset doesn't exists yet it returns None, None
        """
        
        if not self._baseExists:
            return None, None
        
        allVersions = self.getAllVersions()
        
        if len(allVersions) == 0:
            return None, None
        
        maxRevNumber = -1
        currentRevNumber = -1
        maxRevAsset = self
        
        for asset in allVersions:
            currentRevNumber = asset.getRevisionNumber()
            
            if currentRevNumber > maxRevNumber:
                maxRevNumber = currentRevNumber
                maxRevAsset = asset
        
        return maxRevAsset, maxRevNumber
    
    
    
    #----------------------------------------------------------------------
    def getLatestRevision2(self):
        """the second version of the older one, it uses file names instead of
        asset objects.
        
        returns the latest revision of an asset as an asset object and the
        number as an integer
        """
        
        if not self._baseExists:
            return None, None
        
        # get all version names
        allVersionNames = self.getAllVersionNames()
        
        # return the last one as an asset
        assetObj = Asset( self._parentProject, self._parentSequence, allVersionNames[-1] )
        
        return assetObj, assetObj.getRevisionNumber()
    
    
    
    #----------------------------------------------------------------------
    def isLatestVersion(self):
        """checks if the asset is the latest version in its series
        """
        
        # return False if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestVersionNumber = self.getLatestVersion2()
        
        # return True if it is the last in the list
        if self.getVersionNumber() < latestVersionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def isNewVersion(self):
        """checks if the asset is a new version in its series
        """
        # return True if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestVersionNumber = self.getLatestVersion2()
        
        if self.getVersionNumber() <= latestVersionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def isLatestRevision(self):
        """checks if the asset is the latest revision in its series
        """
        
        # return False if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestRevisionNumber = self.getLatestRevision2()
        
        # return True if it is the last in the list
        if self.getRevisionNumber() < latestRevisionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def isNewRevision(self):
        """checks if the asset is a new revision in its series
        """
        
        # return True if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestRevisionNumber = self.getLatestRevision2()
        
        if self.getRevisionNumber() <= latestRevisionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def setVersionToNextAvailable(self):
        """sets the version number to the latest number + 1
        """
        
        latestAsset, latestVersionNumber = self.getLatestVersion2()
        self._ver = latestVersionNumber + 1
        self._verString = self._parentSequence.convertToVerString( self._ver )
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def setRevisionToNextAvailable(self):
        """sets the revision number to the latest number
        """
        
        latestAsset, latestRevisionNumber = self.getLatestRevision2()
        self._rev = latestRevisionNumber
        self._revString = self._parentSequence.convertToRevString( self._rev )
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def increaseVersion(self):
        """increases the version by 1
        """
        self._ver += 1
        self._verString = self._parentSequence.convertToVerString( self._ver )
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def increaseRevision(self):
        """increases the revision by 1
        """
        self._rev += 1
        self._revString = self._parentSequence.convertToRevString( self._rev )
        self.setPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def isShotDependent(self):
        """returns True if the asset is shot dependent
        """
        return self._type.isShotDependent()
    
    
    
    #----------------------------------------------------------------------
    def isValidAsset(self):
        """returns True if this file is an Asset False otherwise
        """
        # if it has a baseName, subName, typeName, revString, verString and a userInitial string
        # and the parent folder for the asset starts with assets baseName
        # then it is considered as a valid asset
        
        if not self._parentSequence._noSubNameField:
            # check the fileName
            validFileName = bool(self._baseName != '' and self._subName != '' and self._typeName != '' and self._revString != '' and \
               self._verString != '' and self._userInitials != '' and self._validateRevString() and \
               self._validateVerString())
            
        else: # remove this block when the support for old version becomes obsolute
            # check the fileName
            validFileName = bool(self._baseName != '' and self._typeName != '' and self._revString != '' and \
               self._verString != '' and self._userInitials != '' and self._validateRevString() and \
               self._validateVerString())
        
        return validFileName
    
    
    
    #----------------------------------------------------------------------
    def _validateRevString(self):
        """validates if the revision string follows the format
        """
        if self._revString == None or self._revString =='':
            return False
        
        revPrefix = self._parentSequence._revPrefix
        
        matchObj = re.match( revPrefix+'[0-9]+', self._revString )
        
        if matchObj == None:
            return False
        else:
            return True
    
    
    
    #----------------------------------------------------------------------
    def _validateVerString(self):
        """validates if the version string follows the format
        """
        if self._verString == None or self._verString == '':
            return False
        
        verPrefix = self._parentSequence._verPrefix
        
        matchObj = re.match( verPrefix+'[0-9]+', self._verString )
        
        if matchObj == None:
            return False
        else:
            return True
    
    
    
    ##----------------------------------------------------------------------
    #def _validateExtension(self):
        #"""check if the extension is in the ignore list in the parent
        #sequence
        #"""
    
    
    
    #----------------------------------------------------------------------
    def getVersionNumber(self):
        """returns the version number of the asset
        """
        return self._ver
    
    
    
    #----------------------------------------------------------------------
    def getRevisionNumber(self):
        """returns the revsion number of the asset
        """
        return self._rev
    
    
    #----------------------------------------------------------------------
    def getShotNumber(self):
        """returns the shot number of the asset if the asset is shot dependent
        """
        
        if self.isShotDependent():
            return self._parentSequence.convertToShotNumber( self._baseName )
    
    
    
    #----------------------------------------------------------------------
    def getVersionString(self):
        """returns the version string of the asset
        """
        return self._verString
    
    
    
    #----------------------------------------------------------------------
    def getRevisionString(self):
        """returns the revision string of the asset
        """
        return self._revString
    
    
    
    #----------------------------------------------------------------------
    def getType(self):
        """returns the asset type as an assetType object
        """
        return self._type
    
    
    
    #----------------------------------------------------------------------
    def getTypeName(self):
        """returns asset type
        """
        return self._type.getName()
    
    
    
    #----------------------------------------------------------------------
    def getUserInitials(self):
        """returns user initials
        """
        return self._userInitials
    
    
    
    #----------------------------------------------------------------------
    def getBaseName(self):
        """returns the base name of the asset
        """
        return self._baseName
    
    
    #----------------------------------------------------------------------
    def getSubName(self):
        """returns the sub name of the asset
        """
        return self._subName
    
    
    
    #----------------------------------------------------------------------
    def getNotes(self):
        """returns 
        """
        return self._notes
    
    
    
    #----------------------------------------------------------------------
    def exists(self):
        """returns True if the asset file exists
        """
        return self._exists
    
    
    
    #----------------------------------------------------------------------
    def updateExistancy(self):
        """updates the self._exists variable
        """
        if self._hasBaseInfo:
            if os.path.exists( self._path ):
                files = os.listdir( self._path )
                critiquePart = self._getCritiqueName()
                
                # update baseExistancy
                for _file in files:
                    if _file.startswith( critiquePart ):
                        self._baseExists = True
                        return
            
            if self._hasFullInfo:
                self._exists = os.path.exists( self._fullPath )
            
        else:
            self._exists = False
            self._baseExists = False
    
    
    
    ##----------------------------------------------------------------------
    #def publishAsset(self):
        #"""publishes the asset by adding its name to the _publishInfo.xml
        #"""
        #pass
    
    
    
    ##----------------------------------------------------------------------
    #def isPublished(self):
        #"""checks if the current asset is a published asset
        #"""
        #pass
    






########################################################################
class AssetType(object):
    """Holds data like:\n
    - the asset type name
    - relative path of that type
    - the shot dependency of that AssetType
    - the environments (list) that the asset is available to
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, name='', path='', shotDependent=False, playblastFolder='', environments=None):
        self._name = name
        self._path = path
        self._shotDependency = shotDependent
        self._playblastFolder = playblastFolder
        self._environments = environments
    
    
    
    #----------------------------------------------------------------------
    def getName(self):
        """return AssetType name
        """
        return self._name
    
    
    
    #----------------------------------------------------------------------
    def getPath(self):
        """returns AssetType path
        """
        return self._path
    
    
    
    #----------------------------------------------------------------------
    def isShotDependent(self):
        """returns True or False depending on to the shot dependency
        """
        return self._shotDependency
    
    
    
    #----------------------------------------------------------------------
    def getPlayblastFolder(self):
        """returns playblast folder of that asset type
        """
        return self._playblastFolder
    
    
    
    #----------------------------------------------------------------------
    def getEnvironments(self):
        """returns the environments that this type is available to as a list of string
        """
        return self._environments
    
    
    
    #----------------------------------------------------------------------
    def setName(self, name):
        """sets asset type name
        """
        self._name = name
    
    
    
    #----------------------------------------------------------------------
    def setPath(self, path):
        """sets asset type path
        """
        self._path = path
    
    
    
    #----------------------------------------------------------------------
    def setShotDependency(self, shotDependency):
        """sets shot dependency of that asset type
        """
        self._shotDependency = shotDependency
    
    
    
    #----------------------------------------------------------------------
    def setEnvironment(self, environments):
        """sets the environment that this asset type is available to
        """
        self._environments = environments