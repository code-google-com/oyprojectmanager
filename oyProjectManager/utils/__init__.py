# -*- coding: utf-8 -*-



import os, itertools, re



#----------------------------------------------------------------------
def all_equal(elements):
    """return True if all the elements are qual, otherwise False.
    """
    first_element = elements[0]
    
    for other_element in elements[1:]:
        if other_element != first_element: return False
    
    return True



#----------------------------------------------------------------------
def common_prefix(*sequences):
    """return a list of common elements at the start of all sequences, then a
    list of lists that are the unique tails of ecach sequence.
    """
    
    # if there are no sequecnes at all, we're done
    if not sequences: return[], []
    # loop in parallel on the sequences
    common = []
    for elements in itertools.izip(*sequences):
        # unless all elements are equal, bail out of the loop
        if not all_equal(elements): break
        
        # got one more common element, append it and keep looping
        common.append(elements[0])
    
    # return the common prefix and unique tails
    return common, [sequence[len(common):] for sequence in sequences]



#----------------------------------------------------------------------
def relpath(p1, p2, sep=os.path.sep, pardir=os.path.pardir):
    """return a relative path from p1 equivalent to path p2.
    
    In particular:
    
        the empty string, if p1 == p2;
        p2, if p1 and p2 have no comon prefix.
    
    """
    
    # replace any trailing slashes at the end
    p1 = re.sub(r"[/]+$", "" , p1)
    p1 = re.sub(r"[\\]+$", "",  p1)
    
    common, (u1, u2) = common_prefix(p1.split(sep), p2.split(sep))
    if not common:
        return p2 # leave path absolute if nothing at all in common
    
    return sep.join([pardir]*len(u1) + u2 )



#----------------------------------------------------------------------
def mkdir(path):
    """Creates a directory in the given path
    """
    
    try:
        os.makedirs(path)
    except OSError:
        pass



#----------------------------------------------------------------------
def sort_string_numbers(str_list):
    """sorts strings with embedded numbers
    """
    
    def embedded_numbers(s):
        re_digits = re.compile(r'(\d+)')
        pieces = re_digits.split(str(s))
        pieces[1::2] = map(int, pieces[1::2])
        return pieces
    
    return sorted(str_list, key=embedded_numbers)



#----------------------------------------------------------------------
def unique(s):
    """ Return a list of elements in s in arbitrary order, but without
    duplicates.
    """
    
    # Try using a set first, because it's the gastest and will usally work
    try:
        return list(set(s))
    except TypeError:
        pass # Move on to the next method
    
    # Since you can't hash all elements, try sorting, to bring equal items
    # together and then weed them out in a single pass
    t = list(s)
    try:
        t.sort()
    except TypeError:
        del t # Move on to the next method
    else:
        # the sort worked, so we are fine
        # do weeding
        return [x for i, x in enumerate(t) if not i or x != t[i-1]]
    # Brute force is all that's left
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    
    return u



#----------------------------------------------------------------------
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
    
    assert(isinstance(_range, (str, unicode) ) )
    
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
                shotList.append(number)
    
    shotList.sort()
    
    return shotList



#----------------------------------------------------------------------
def matchRange(_range):
    """validates the range string
    """
    
    assert(isinstance(_range, (str, unicode)))
    
    pattern = re.compile('[0-9\-,]+')
    matchObj = re.match( pattern, _range )
    
    if matchObj:
        _range = matchObj.group()
    else:
        _range = ''
    
    return _range