# -*- coding: utf-8 -*-



import os, re, time
import oyAuxiliaryFunctions as oyAux
import jinja2





########################################################################
class Asset(object):
    """to work properly it needs a valid project and sequence objects
    
    an Assets folder is something like that:
    
    ProjectsFolder / ProjectName / SequenceName / TypePath / BaseName / assetFileName
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, project, sequence, fileName=None):
        
        self._project = project
        self._sequence = sequence
        
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
        self._dateCreated = None
        self._dateUpdated = None
        self._fileSize = None
        self._fileSizeString = None
        self._fileSizeFormat = "%.2f MB"
        
        # path variables
        self._fileName = None #os.path.splitext(fileName)[0] # remove the extension
        self._path = None
        self._fullPath = None
        
        self._hasFullInfo = False
        self._hasBaseInfo = False
        
        self._dataSeparator = u'_'
        
        self._timeFormat = '%d.%m.%Y %H:%M'
        
        self._exists = False
        self._baseExists = False
        
        if fileName != None:
            self._fileName  = unicode( os.path.splitext(unicode(fileName))[0] ) # remove the extension
            self._extension = unicode( os.path.splitext(unicode(fileName))[1] ).split( os.path.extsep )[-1] # remove the . in extension
            self.guessInfoVariablesFromFileName()
        
        self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    @property
    def infoVariables(self):
        """returns the info variables as a dictionary
        """
        
        infoVars = dict()
        infoVars['baseName'] = self._baseName
        infoVars['subName'] = self._subName
        infoVars['typeName'] = self._type.name
        infoVars['rev'] = self._rev
        infoVars['revString'] = self._revString
        infoVars['ver'] = self._ver
        infoVars['verString'] = self._verString
        infoVars['userInitials'] = self._userInitials
        infoVars['notes'] = self._notes
        infoVars['fileName'] = self._fileName
        
        return infoVars
    
    
    
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
            self._type = self._sequence.getAssetTypeWithName( self._typeName )
        
        # convert revision and version strings to number
        if keys.has_key('revString'):
            self._revString = keys['revString']
            self._rev = self._sequence.convertToRevNumber( self._revString )
        elif keys.has_key('rev'):
            self._rev = int( keys['rev'] )
            self._revString = self._sequence.convertToRevString( self._rev )
        
        if keys.has_key('verString'):
            self._verString = keys['verString']
            self._ver = self._sequence.convertToVerNumber( self._verString )
        elif keys.has_key('ver'):
            self._ver = int( keys['ver'])
            self._verString = self._sequence.convertToVerString( self._ver )
        
        if keys.has_key('userInitials'):
            self._userInitials = keys['userInitials']
        
        if keys.has_key('notes'):
            self._notes = keys['notes']
        
        if keys.has_key('extension'):
            self._extension = keys['extension']
        
        if not self._sequence._noSubNameField:
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
        self._initPathVariables()
        self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    def guessInfoVariablesFromFileName(self):
        """tries to get all the info variables from the file name
        """
        
        # check if there is a valid project
        if self._project == None or self._sequence == None:
            return
        
        parts = self._fileName.split(self._dataSeparator)
        
        if not self._sequence._noSubNameField:
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
                self._notes = self._dataSeparator.join(parts[5:len(parts)])
            else:
                self._notes = ""
        
        # get the type object
        self._type = self._sequence.getAssetTypeWithName(self._typeName)
        
        # sometimes the file name matches the format but it is not neccessarly
        # an asset file if the type is None
        if self._type is None:
            return
        
        try:
            self._rev = self._sequence.convertToRevNumber(self._revString)
            self._ver = self._sequence.convertToVerNumber(self._verString)
        except ValueError:
            # the pattern is not compatible with the current project
            return
        
        self._hasFullInfo = self._hasBaseInfo = True
        
        self._initPathVariables()
        
        #self._updateFileSizes()
        #self._updateFileDates()
    
    
    
    #----------------------------------------------------------------------
    @property
    def fullPath(self):
        """returns the fullPath of the asset
        """
        return self._fullPath
    
    
    
    #----------------------------------------------------------------------
    @property
    def sequence(self):
        """returns the parent sequence
        """
        #from oyProjectManager.models import project
        #assert(isinstance(self._sequence, project.Sequence ) )
        return self._sequence
    
    
    
    #----------------------------------------------------------------------
    @property
    def path(self):
        """retrurns the path of the asset
        """
        
        return self._path
    
    
    
    def extension():
        """the file extension
        """
        doc = "the file extension"
        
        def fget(self):
            """returns the extension
            """
            return self._extension
        
        def fset(self, extension):
            """sets the extension of the asset object
            """
            #assert( isinstance(extension, str))
            # remove any extension seperators from the input extension
            finalExtension = extension.split( os.path.extsep )[-1]
            
            self._extension = finalExtension
            self._initPathVariables()
        
        return locals()
    
    extension = property( **extension() )
    
    
    
    #----------------------------------------------------------------------
    @property
    def fileName(self):
        """gathers the info variables to a fileName
        """
        
        fileName = self.fileNameWithoutExtension
        
        if self._extension is not None and self._extension != '' and fileName is not None:
            fileName = fileName + os.extsep + self._extension
        
        return fileName
    
    
    
    #----------------------------------------------------------------------
    @property
    def fileNameWithoutExtension(self):
        """returns the file name without extension
        """
        
        if not self.isValidAsset:
            return None
        
        parts = [] * 0
        parts.append(self._baseName)
        
        if not self._sequence._noSubNameField:
            parts.append(self._subName)
        
        parts.append(self._type.name)
        parts.append(self._revString)
        parts.append(self._verString)
        parts.append(self._userInitials)
        
        # check if there is a note
        if self._notes != None and self._notes != '':
            parts.append( self._notes )
        
        fileName = self._dataSeparator.join(parts)
        
        return fileName
    
    
    
    #----------------------------------------------------------------------
    @property
    def fileSize(self):
        """returns the fileSize as a float
        """
        return self._fileSize
    
    
    
    #----------------------------------------------------------------------
    @property
    def fileSizeFormated(self):
        """returns the fileSize as a formatted string
        """
        return self._fileSizeString
    
    
    
    #----------------------------------------------------------------------
    @property
    def pathVariables(self):
        """returns the path variables which are
        fullPath
        path
        fileName
        """
        return self.fullPath, self.path, self.fileName
    
    
    
    #----------------------------------------------------------------------
    @property
    def project(self):
        """returns the project of the asset
        """
        return self._project
    
    
    
    #----------------------------------------------------------------------
    def _initPathVariables(self):
        """sets path variables
        needs the info variables to be set before
        """
        
        # if it has just the base info update some of the variables
        if self._hasBaseInfo:
            seqFullPath = self._sequence.fullPath
            
            typePath = self._type.path
            
            assert(isinstance(typePath, (str, unicode)))
            
            # check if it has any jinja2 template variable
            if "{{" in typePath:
                self._path = os.path.join(seqFullPath, typePath)
                
                # and render the jinja2 template
                self._path = jinja2.Template(self._path).render(
                    assetBaseName=self.baseName,
                    assetSubName = self.subName,
                    assetTypeName = self.typeName,
                    assetRevNumber = self.revisionNumber,
                    assetRevString = self.revisionString,
                    assetVerNumber = self.versionNumber,
                    assetVerString = self.versionString,
                    assetUserInitials = self.userInitials,
                    assetExtension = self.extension
                )
            else:
                # fallback to the previous design where there is no
                # jinja2 template support
                self._path = os.path.join(seqFullPath, typePath)
                self._path = os.path.join(self._path, self._baseName )
            
            # if it has full info update the rest of the variables
            if self._hasFullInfo:
                
                self._fileName = self.fileName
                self._fullPath = os.path.join(self._path, self._fileName)
                
                self.updateExistancy()
    
    
    
    #----------------------------------------------------------------------
    @property
    def allVersions(self):
        """returns all versions as a list of asset objects
        """
        # return if we can't even get some little information
        if not self._baseExists and not self._hasBaseInfo:
            return []
        
        # use the Sequence object instead of letting the Asset object to dive in to the
        # file system to get other versions
        
        #import project
        sProj = self._project
        sSeq = self._sequence
        #assert(isinstance(selfseq,project.Sequence))
        
        assetVersionNames = self.allVersionNames
        
        sProjList = [sProj] * len(assetVersionNames)
        sSeqList = [sSeq] * len(assetVersionNames)
        
        return map(Asset, sProjList, sSeqList, assetVersionNames)
    
    
    
    #----------------------------------------------------------------------
    @property
    def allVersionNames(self):
        """returns all version names for that asset as a list of string
        """
        
        if not self._baseExists and not self._hasBaseInfo:
            return []
        
        sSeq = self._sequence
        
        sSeqFAN = sSeq.filterAssetNames
        sSeqGAAFNFT = sSeq.getAllAssetFileNamesForType
        
        typeName = self._typeName
        baseName = self._baseName
        subName = self._subName
        
        if not self._sequence._noSubNameField:
            return sorted([ assetFileName for assetFileName in sSeqFAN( sSeqGAAFNFT( typeName ), baseName=baseName, subName=subName ) ])
        else:
            return sorted([ assetFileName for assetFileName in sSeqFAN( sSeqGAAFNFT( typeName ), baseName=baseName ) ] )
    
    
    
    #----------------------------------------------------------------------
    def _getCritiqueName(self):
        """returns the critique part of the asset name, which is:
        BaseName_SubName_TypeName
        """
        
        if not self._sequence._noSubNameField:
            if self._baseName == None or self._subName == None or self._typeName == None:
                return None
            
            return self._dataSeparator.join( [self._baseName, self._subName, self._typeName ] )
        
        else: # remove this block when the support for old version becomes obsolute
            if self._baseName == None or self._typeName == None:
                return None
            
            return self._dataSeparator.join( [self._baseName, self._typeName ] )
    
    
    
    #----------------------------------------------------------------------
    @property
    def sequenceFullPath(self):
        """returns the parent sequence full path
        """
        #from oyProjectManager.models import project
        #assert(isinstance(self._sequence, project.Sequence))
        return self._sequence.fullPath
    
    
    
    ##----------------------------------------------------------------------
    #def getProjectPath(self):
        #"""returns the parent project path
        
        #beware that it is the project path not the sequence path
        #"""
        #from oyProjectManager.models import project
        #assert(isinstance(self._project, project.Project))
        #return self._project.fullPath
    
    
    
    #----------------------------------------------------------------------
    @property
    def latestVersion(self):
        """returns the lastest version of an asset as an asset object and the number as an integer
        if the asset file doesn't exists yet it returns None, None
        """
        
        if not self._baseExists:
            return None, None
        
        allVersions = self.allVersions
        
        if len(allVersions) == 0:
            return None, None
        
        maxVerNumber = -1
        currentVerNumber = -1
        maxVerAsset = self
        
        for asset in allVersions:
            currentVerNumber = asset.versionNumber
            
            if currentVerNumber > maxVerNumber:
                maxVerNumber = currentVerNumber
                maxVerAsset = asset
        
        return maxVerAsset, maxVerNumber
    
    
    
    #----------------------------------------------------------------------
    @property
    def latestVersion2(self):
        """the second version of the older one, it uses file names instead of
        asset objects.
        
        returns the latest version of an asset as an asset object and the
        number as an integer
        """
        
        if not self._baseExists:
            return None, None
        
        # get all version names
        allVersionNames = self.allVersionNames
        
        # return the last one as an asset
        if len(allVersionNames) > 0:
            assetObj = Asset( self._project, self._sequence, allVersionNames[-1] )
        else:
            return None, None
        
        return assetObj, assetObj.versionNumber
    
    
    
    #----------------------------------------------------------------------
    @property
    def latestRevision(self):
        """returns the latest revision of an asset as an asset object and the number as an integer
        if the asset doesn't exists yet it returns None, None
        """
        
        if not self._baseExists:
            return None, None
        
        allVersions = self.allVersions
        
        if len(allVersions) == 0:
            return None, None
        
        maxRevNumber = -1
        currentRevNumber = -1
        maxRevAsset = self
        
        for asset in allVersions:
            currentRevNumber = asset.revisionNumber
            
            if currentRevNumber > maxRevNumber:
                maxRevNumber = currentRevNumber
                maxRevAsset = asset
        
        return maxRevAsset, maxRevNumber
    
    
    
    #----------------------------------------------------------------------
    @property
    def latestRevision2(self):
        """the second version of the older one, it uses file names instead of
        asset objects.
        
        returns the latest revision of an asset as an asset object and the
        number as an integer
        """
        
        if not self._baseExists:
            return None, None
        
        # get all version names
        allVersionNames = self.allVersionNames
        
        # return the last one as an asset
        assetObj = Asset( self._project, self._sequence, allVersionNames[-1] )
        
        return assetObj, assetObj.revisionNumber
    
    
    
    #----------------------------------------------------------------------
    def isLatestVersion(self):
        """checks if the asset is the latest version in its series
        """
        
        # return False if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestVersionNumber = self.latestVersion2
        
        # return True if it is the last in the list
        if self.versionNumber < latestVersionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def isNewVersion(self):
        """checks if the asset is a new version in its series
        """
        # return True if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestVersionNumber = self.latestVersion2
        
        if self.versionNumber <= latestVersionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def isLatestRevision(self):
        """checks if the asset is the latest revision in its series
        """
        
        # return False if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestRevisionNumber = self.latestRevision2
        
        # return True if it is the last in the list
        if self.revisionNumber < latestRevisionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def isNewRevision(self):
        """checks if the asset is a new revision in its series
        """
        
        # return True if there is no such asset initialized yet
        if not self._baseExists:
            return True
        
        latestAssetObject, latestRevisionNumber = self.latestRevision2
        
        if self.revisionNumber <= latestRevisionNumber:
            return False
        
        return True
    
    
    
    #----------------------------------------------------------------------
    def setVersionToNextAvailable(self):
        """sets the version number to the latest number + 1
        """
        
        latestAsset, latestVersionNumber = self.latestVersion2
        self._ver = latestVersionNumber + 1
        self._verString = self._sequence.convertToVerString( self._ver )
        self._initPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def setRevisionToNextAvailable(self):
        """sets the revision number to the latest number
        """
        
        latestAsset, latestRevisionNumber = self.latestRevision2
        self._rev = latestRevisionNumber
        self._revString = self._sequence.convertToRevString( self._rev )
        self._initPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def increaseVersion(self):
        """increases the version by 1
        """
        self._ver += 1
        self._verString = self._sequence.convertToVerString( self._ver )
        self._initPathVariables()
    
    
    
    #----------------------------------------------------------------------
    def increaseRevision(self):
        """increases the revision by 1
        """
        self._rev += 1
        self._revString = self._sequence.convertToRevString( self._rev )
        self._initPathVariables()
    
    
    
    #----------------------------------------------------------------------
    @property
    def isShotDependent(self):
        """returns True if the asset is shot dependent
        """
        return self.type.isShotDependent
    
    
    
    #----------------------------------------------------------------------
    @property
    def isValidAsset(self):
        """returns True if this file is an Asset False otherwise
        
        being a valid asset doesn't neccessarly mean the asset file exists
        
        """
        # if it has a baseName, subName, typeName, revString, verString and a userInitial string
        # and the parent folder for the asset starts with assets baseName
        # then it is considered as a valid asset
        
        if not self._sequence._noSubNameField:
            # check the fileName
            validFileName = bool(
                self._baseName != '' and self._baseName is not None and
                self._subName != '' and self._subName is not None and
                self._typeName != '' and self._typeName is not None and
                self._revString != '' and self._revString is not None and
                self._verString != '' and self._verString is not None and
                self._userInitials != '' and self._userInitials is not None and
                self._validateRevString() and self._validateVerString())
            
        else: # remove this block when the support for old version becomes obsolute
            # check the fileName
            validFileName = bool(
                self._baseName != '' and self._baseName is not None and
                self._typeName != '' and self._typeName is not None and
                self._revString != '' and self._revString is not None and
                self._verString != '' and self._verString is not None and
                self._userInitials != '' and self._userInitials is not None and
                self._validateRevString() and self._validateVerString())
        
        return validFileName
    
    
    
    #----------------------------------------------------------------------
    def _validateRevString(self):
        """validates if the revision string follows the format
        """
        if self._revString == None or self._revString =='':
            return False
        
        revPrefix = self._sequence._revPrefix
        
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
        
        verPrefix = self._sequence._verPrefix
        
        matchObj = re.match( verPrefix+'[0-9]+', self._verString )
        
        if matchObj == None:
            return False
        else:
            return True
    
    
    
    #----------------------------------------------------------------------
    def _updateFileDates(self):
        """updates the file creation and update dates
        """
        
        # get the file dates
        try:
            self._dateCreated = time.strftime( self._timeFormat, time.localtime( os.path.getctime( self._fullPath ) ) )
            self._dateUpdated = time.strftime( self._timeFormat, time.localtime( os.path.getmtime( self._fullPath ) ) )
        except OSError:
            pass
    
    
    
    #----------------------------------------------------------------------
    def _updateFileSizes(self):
        """updates the file sizes as megabytes
        """
        
        # get the file dates
        try:
            self._fileSize = os.path.getsize( self._fullPath )
            self._fileSizeString = self._fileSizeFormat % ( self._fileSize * 9.5367431640625e-07 )
        except OSError:
            pass
        
    
    
    
    ##----------------------------------------------------------------------
    #def _validateExtension(self):
        #"""check if the extension is in the ignore list in the parent
        #sequence
        #"""
    
    
    
    #----------------------------------------------------------------------
    @property
    def versionNumber(self):
        """returns the version number of the asset
        """
        return self._ver
    
    
    
    #----------------------------------------------------------------------
    @property
    def revisionNumber(self):
        """returns the revsion number of the asset
        """
        return self._rev
    
    
    #----------------------------------------------------------------------
    @property
    def shotNumber(self):
        """returns the shot number of the asset if the asset is shot dependent
        """
        
        if self.isShotDependent:
            return self._sequence.convertToShotNumber( self._baseName )
    
    
    
    #----------------------------------------------------------------------
    @property
    def versionString(self):
        """returns the version string of the asset
        """
        return self._verString
    
    
    
    #----------------------------------------------------------------------
    @property
    def revisionString(self):
        """returns the revision string of the asset
        """
        return self._revString
    
    
    
    #----------------------------------------------------------------------
    @property
    def type(self):
        """returns the asset type as an assetType object
        """
        return self._type
    
    
    #----------------------------------------------------------------------
    @property
    def typeName(self):
        """returns the asset type name
        """
        return self._typeName
    
    
    
    #----------------------------------------------------------------------
    @property
    def dateCreated(self):
        """returns the date that the asset is created
        """
        
    
    #----------------------------------------------------------------------
    @property
    def dateUpdated(self):
        """returns the date that the asset is updated
        """
        return self._dateUpdated
    
    
    
    #----------------------------------------------------------------------
    @property
    def userInitials(self):
        """returns user initials
        """
        return self._userInitials
    
    
    
    #----------------------------------------------------------------------
    @property
    def baseName(self):
        """returns the base name of the asset
        """
        return self._baseName
    
    
    #----------------------------------------------------------------------
    @property
    def subName(self):
        """returns the sub name of the asset
        """
        return self._subName
    
    
    
    #----------------------------------------------------------------------
    @property
    def notes(self):
        """returns 
        """
        return self._notes
    
    
    
    #----------------------------------------------------------------------
    @property
    def output_path(self):
        """returns the output path of the current asset
        """
        
        # render all variables like:
        # assetBaseName
        # assetSubName
        # assetTypeName
        # assetRevNumber
        # assetRevString
        # assetVerNumber
        # assetVerString
        # assetUserInitials
        # assetExtension
        
        return jinja2.Template(self.type.output_path).render(
            assetBaseName=self.baseName,
            assetSubName = self.subName,
            assetTypeName = self.typeName,
            assetRevNumber = self.revisionNumber,
            assetRevString = self.revisionString,
            assetVerNumber = self.versionNumber,
            assetVerString = self.versionString,
            assetUserInitials = self.userInitials,
            assetExtension = self.extension
        )
    
    
    
    #----------------------------------------------------------------------
    @property
    def exists(self):
        """returns True if the asset file exists
        """
        return self._exists
    
    
    
    #----------------------------------------------------------------------
    def updateExistancy(self):
        """updates the self._exists variable
        """
        
        if self._hasBaseInfo:
            if os.path.exists(self._path):
                files = os.listdir( self._path )
                critiquePart = self._getCritiqueName()
                
                # update baseExistancy
                for _file in files:
                    if _file.startswith( critiquePart ):
                        self._baseExists = True
                        break
            
            if self._hasFullInfo:
                self._exists = os.path.exists( self._fullPath )
                
                self._updateFileSizes()
                self._updateFileDates()
        
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
    def __init__(self, name="", path="", shotDependent=False, environments=None, output_path=""):
        self._name = name
        self._path = path
        self._shotDependency = shotDependent
        self._environments = environments
        self._output_path = output_path
    
    
    
    #----------------------------------------------------------------------
    def name():
        """the asset type name
        """
        
        doc = "the asset type name"
        
        def fget(self):
            return self._name
        
        def fset(self, name):
            self._name = name
        
        return locals()
    
    name = property( **name() )
    
    
    
    #----------------------------------------------------------------------
    def path():
        
        doc = "assets types path"
        
        def fget(self):
            return self._path
        
        def fset(self, path):
            self._path = path
        
        return locals()
    
    path = property( **path() )
    
    
    
    #----------------------------------------------------------------------
    def environments():
        
        doc = "the environments that this asset type is available for"
        
        def fget(self):
            return self._environments
        
        def fset(self, environments):
            self._environments = environments
        
        return locals()
    
    environments = property( **environments() )
    
    
    
    #----------------------------------------------------------------------
    def isShotDependent():
        
        doc = "defines if the asset type is shot dependent or not"
        
        def fget(self):
            return self._shotDependency
        
        def fset(self, shotDependency):
            self._shotDependency = shotDependency
        
        return locals()
    
    isShotDependent = property( **isShotDependent() )
    
    
    
    #----------------------------------------------------------------------
    def output_path():
        def fget(self):
            return self._output_path
        
        def fset(self, output_path_in):
            #self._output_path = self._validate_output_path(output_path_in)
            self._output_path = output_path_in
        
        doc = """The output path of this asset type"""
        
        return locals()
    
    output_path = property(**output_path())






########################################################################
class SuperAsset(object):
    '''this is a new class, which actually should be named as "Asset". But
    because the name is reserved by the previous designs Asset class, it is
    named as SuperAsset.
    
    In the previous design, the Asset objects were only pointing to and giving
    information about one file, which later on seemed very wrong. Because, the
    file that the Asset object is tied to is just one of the versions of the
    same asset. So it was breaking the generality of the whole design.
    
    The new SuperAsset class will deal with the assets in a more convienient
    way. This class now deals with assets, not the individual versions of the
    asset file.
    
    The new class deals with the information below:
    - All the versions as version list
    - The published asset information
    - User comments about the asset
    
    To initialize the class we do not need anything other than the asset
    folders full path. So for an asset lying down in:
    
    M:/JOBs/ETI_TOPKEK/_CHARACTER_SETUP_/_RIG_/Kopil
    
    folder, knowing the full path is enough to have the informations
    below:
    
    - the Project name and therefore the project object ( by using the
      repository object )
    - the Sequence name and therefore the sequence object ( by using the
      repository object )
    - the asset base name
    - listining the folder contents and having all the subNames ( if
      available )
    '''
    
    
    
    #----------------------------------------------------------------------
    #def __init__(self, project, sequence, typeName, baseName ): #, subName):
    def __init__(self):
        
        self._project = None
        self._sequence = None
        
        self._baseName = ''
        self._subName = ''
        self._typeName = ''
        self._type = None
        
        self._dataSeparator = u'_'
        
        #self._info = dict()
        
        # path variables
        self._path = ''
        self._fullPath = ''
    
    
    
    ##----------------------------------------------------------------------
    #def findAllVersions(self):
        #""" finds all the asset versions of the super asset
        #"""
        #import models.project as project
        #assert( isinstance(self._sequence, project.Sequence) )
        
        ## search the path for the baseName + subName
        
        #searchPath = self._path
        #pattern = self._baseName + '*'
        
        
    
    
    
