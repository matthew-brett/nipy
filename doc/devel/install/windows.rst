================================
 Development install on windows
================================

The easy way - a super-package
------------------------------

The easiest way to get the dependencies is to install PythonXY_ or the
`Enthought Tool Suite`_ .  This gives you MinGW_, Python_, Numpy_,
Scipy_, ipython_ and matplotlib_ (and much more).  

The hard way - by components
----------------------------

If instead you want to do it by component, try the instructions below.

Requirements:

* Download and install MinGW_
* Download and install the windows binary for Python_
* Download and install the Numpy_ and Scipy_ binaries
* Download and install Sympy_

Options:

* Download and install ipython_, being careful to follow the windows
  installation instructions
* Download and install matplotlib_

Alternatively, if you are very brave, you may want to install numpy / scipy from
source - see our maybe out of date :ref:`windows_scipy_build` for details.

Getting and installing NIPY
---------------------------

You will next need to get the NIPY code via version control:

* Download and install the windows binary for git_
* Go to the windows menu, find the ``git`` menu, and run ``git`` in a
  windows terminal.

You should now be able to follow the instructions in
:ref:`trunk_download`, but with the following modifications:

Build install in windows
------------------------

Here we assume that you do *not* have the Microsoft visual C tools, you
did not use the ETS_ package (which sets the compiler for you) and *are*
using a version of  MinGW_ to compile NIPY.

Installing MinGW
^^^^^^^^^^^^^^^^

To compile nipy, you will need MinGW with gcc-3.  By default, MinGW comes with
gcc-4.  The following procedure comes from `this mail
<http://mingw-users.1079350.n2.nabble.com/How-do-I-install-mingw-gcc-3-4-5-td5604746.html>`_

* Make a directory ``c:\MingGW``
* Download the latest ``mingw-get-inst`` from
  http://sourceforge.net/projects/mingw/files/Installer/mingw-get-inst
* Unpack the downloaded archive into ``c:\MinGW``
* ``cd c:\MinGW\bin``
* ``mingw-get install gcc-v3-c++``
* Make sure ``c:\MinGW\bin`` is on your path somehow.

Install Cython
^^^^^^^^^^^^^^

If you don't have Cython, install via a binary installer at
http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython



Running the build install
^^^^^^^^^^^^^^^^^^^^^^^^^

First, for the ``python setup.py`` steps, you will need to add the
``--compiler=mingw32`` flag, like this::

   python setup.py build --compiler=mingw32 install

Note that, with this setup you cannot do inplace (developer) installs
(like ``python setup.py build_ext --inplace``) because of a six-legged
python packaging feature that does not allow the compiler options (here
``--compiler=mingw32``) to be passed from the ``build_ext`` command.

If you want to be able to do that, add these lines to your ``distutils.cfg`` file ::

  [build]
  compiler=mingw32

  [config]
  compiler = mingw32

See http://docs.python.org/install/#inst-config-files for details on
this file.  After you've done this, you can run the standard ``python
setup.py build_ext --inplace`` command.

The command line from Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default windows XP command line ``cmd`` is very basic.  You might
consider using the Cygwin_ bash shell, or you may want to use the
ipython_ shell to work in.  For system commands use the ``!`` escape,
like this, from the ipython prompt::

   !python setup.py build --compiler=mingw32


.. include:: ../../links_names.txt
