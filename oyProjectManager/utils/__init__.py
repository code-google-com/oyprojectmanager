#coding:utf-8



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
    
    In particular: the empty string, if p1 == p2;
                   p2, if p1 and p2 have no comon prefix.
    """
    
    # replace any trailing slashes at the end
    p1 = re.sub(r"[" + sep + "]+$", "" , p1)
    
    common, (u1, u2) = common_prefix(p1.split(sep), p2.split(sep))
    if not common:
        return p2 # leave path absolute if nothing at all in common
    
    return sep.join([pardir]*len(u1) + u2 )