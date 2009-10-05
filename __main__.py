import sys, getopt



#----------------------------------------------------------------------
def main(argv=None):
    """The main procedure
    """
    if argv is None:
        argv = sys.argv
    
    # parse command line options
    try:
        shortopts = "h,f:,p:,u,v,e:"
        longopts = ["help","fileName=","path=","userInterface","version","environment="]
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    environment = None
    userInterface = False
    fileName = None
    path = None
   
    # process options
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            from oyProjectManager import __doc__
            print __doc__
            sys.exit(0)
        
        if opt in ("-e", "--environment"):
            environment = arg
            
        if opt in ("-u", "--userInterface"):
            userInterface = True
        
        if opt in ("-v", "--version"):
            from oyProjectManager import __version__
            print __version__
            sys.exit(0)
        
        if opt in ("-f", "--fileName"):
            fileName = apt
        
        if opt in ("-p", "--path"):
            path = apt
    
    if userInterface:
        from ui import mainWindow
        return mainWindow.UI(environment, fileName, path)





if __name__ == "__main__":
    main()