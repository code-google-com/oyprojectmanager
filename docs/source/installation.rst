.. _installation_toplevel:

How to install oyProjectManager
===============================

Automated install
-----------------

  1. Download and install `Python 2.6`_ (that is because most of the programs
     are still using 2.6)
  2. Download and install `setup tools`_
  3. Run::
     
       easy_install-2.6 oyProjectManager
    
     This will install oyProjectManager to your pythons dist-packages folder
     with all its dependencies.
     
  4. Copy all the packages to a shared folder, which is visible to other
     computers in your studio.
  5. Add the following paths to ``PYTHONPATH`` environment variable to let
     all the applications to see the modules::
       
       path:to/shared/folder/oyProjectManager-0.2.4/
       path:to/shared/folder/SQLAlchemy-0.7.7/lib/
       path:to/shared/folder/Jinja2-2.6/
     
  .. _Python 2.6: http://www.python.org/download/
  .. _setup tools: http://pypi.python.org/pypi/setuptools

As a side note, running the installation code above under one operating system
and using oyProjectManager under other operating systems is working without any
problems. The only side effects should be the lack of C extensions that both
libraries supplying, but this will not affect the speed as may it has been
thought of.

Manual install
--------------

  1. Download `oyProjectManager`_ and extract it and copy the oyProjectManager
     folder to a shared folder which all of your workstations are able to see.
  2. Download `SQLAlchemy`_ and again extract it to a shared folder.
  3. Do the same for `Jinja2`_.
  4. Add these paths to the ``PYTHONPATH`` environment variable to let all the
     applications to see the modules::
     
       /path/to/shared/path/oyProjectManager-0.2.4/
       /path/to/shared/path/SQLAlchemy-0.7.7/lib/
       /path/to/shared/path/Jinja2-2.6/
  
  .. _oyProjectManager: http://pypi.python.org/pypi/oyProjectManager
  .. _SQLAlchemy: http://www.sqlalchemy.org/
  .. _Jinja2: http://jinja.pocoo.org/
  

Configuration
-------------

   oyProjectManager needs two environment variables to be defined, ``REPO``
   and ``OYPROJECTMANAGER_PATH``.
   
   `REPO`: set to a path where you want to save your projects. This is
   typically a mapped drive like ``M:\Projects`` for Windows and or a mount
   like ``/mnt/M/Projects`` in Linux and OSX.
   
   `OYPROJECTMANAGER_PATH`: The path that contains the ``config.py`` file,
   which is the configuration file for the system (I also suggest to use this
   folder to place your SQLite3 database file).

  See `configuring oyProjectManager`_ for the details about ``config.py``.
  
  .. _configuring oyProjectManager: ./configure.html
  
User Interfaces
---------------

  1. If you don't plan to use another interface library and do all that nasty
     coding by your self I also strongly suggest you to install PyQt4 or PySide
     for all to your applications (Maya, Nuke, Houdini etc.) and use the UI
     coming with oyProjectManager. Because installing PyQt4 and PySide is a
     little bit involving, I'm leaving you by your self about how to install
     it. For a quick tip search for MyQt4 for Maya, and you can use
     `this blog`_ post about compiling PyQt4 under Windows.
     
  2. Newer versions of Nuke comes with PySide installed,
     to be able to use PySide instead of PyQt4, add a new environment variable
     to Nuke's startup script (init.py) called `"PREFERRED_QT_MODULE"` and
     assign the value `"PySide"`.
     
  .. _this blog: http://eoyilmaz.blogspot.com/2009/09/how-to-compile-pyqt4-for-windows-x64.html

  3. You should be ready to go, run maya, be sure that maya is able to see the
     directory you have copied the modules in to and run::
     
       from oyProjectManager.environments import mayaEnv
       from oyProjectManager.ui import version_creator
       mEnv = mayaEnv.Maya()
       version_creator.UI(mEnv)
     
     When you run the above script, you should be able to see the
     ``version_creator`` UI. Which as the name suggests creates new versions
     for some assets or shots.
     
     The interface should explain itself. But because you didn't created any
     Project yet you will not be able to create any assets or shots or
     versions.
     
  4. To bring up the project_manager interface use the following code::
     
       from oyProjectManager.ui import project_manager
       project_manager.UI()
    
    This will show up a new interface where you can create and edit Projects,
    Sequences and Shots.
    
    You can also run the ``project_manager`` from the regular Python shell if
    you have successfully installed oyProjectManager, SQLAlchemy and Jinja2 to
    your system installation of Python by using the `automated install`_.
