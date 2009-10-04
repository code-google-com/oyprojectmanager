import oyAuxiliaryFunctions as oyAux


########################################################################
class RangeConverter(object):
    """a class for manipulating shot lists
    """
    
    
    
    #----------------------------------------------------------------------
    @staticmethod
    def convertRangeToList(_range):
        """a shotRange is a string that contains numeric data with "," and "-"
        characters
        
        1-4 expands to 1,2,3,4
        10-5 expands to 5,6,7,8,9,10
        1,4-7 expands to 1,4,5,6,7
        1,4-7,11-4 expands to 1,4,5,6,7,8,9,10,11
        """
        
        shotList = [] * 0
        number = 0
        
        assert(isinstance(_range, str))
        
        # first split for ","
        groups = _range.split(",")
        
        for group in groups:
            # try to split for "-"
            ranges = group.split("-")
            
            if len(ranges) > 1:
                if ranges[0] != '' and ranges[1] != '':
                    minRange = min( int(ranges[0]), int(ranges[1]))
                    maxRange = max( int(ranges[0]), int(ranges[1]))
                    
                    for number in range(minRange, maxRange+1):
                        if number not in shotList:
                            shotList.append( number )
            else:
                number = int(ranges[0])
                if number not in shotList:
                    shotList.append( int(ranges[0]) )
        
        shotList.sort()
        shotList = oyAux.concatenateLists( shotList )
        
        return shotList