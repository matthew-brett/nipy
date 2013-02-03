.. _installation:

====================
Download and Install
====================

This page covers the necessary steps to install and run NIPY.  Below is a list
of required dependencies, along with additional software recommendations.

NIPY is currently *beta* quality.

Dependencies
------------

Must Have
^^^^^^^^^

  Python_ 2.5 or later

  NumPy_ 1.2 or later

  SciPy_ 0.7 or later
    Numpy and Scipy are high-level, optimized scientific computing libraries.

  Sympy_ 0.6.6 or later
    Sympy is a symbolic mathematics library for Python.  We use it for
    statistical formalae.


Must Have to Build
^^^^^^^^^^^^^^^^^^

If your OS/distribution does not provide you with binary build of
NIPY, you would need few additional components to be able to build
NIPY directly from sources

  gcc_
    NIPY does contain a few C extensions for optimized
    routines. Therefore, you must have a compiler to build from
    source.  XCode_ (OSX) and MinGW_ (Windows) both include gcc.

  cython_ 0.12.1 or later
    Cython is a language that is a fusion of Python and C.  It allows us
    to write fast code using Python and C syntax, so that it easier to
    read and maintain.


Strong Recommendations
^^^^^^^^^^^^^^^^^^^^^^

  iPython_
    Interactive Python environment.

  Matplotlib_
    2D python plotting library.


Installing from binary packages
-------------------------------

For Debian or Ubuntu
^^^^^^^^^^^^^^^^^^^^

Please use the NeuroDebian_ repository, and install with::

    sudo apt-get install python-nipy

For other Linux systems
^^^^^^^^^^^^^^^^^^^^^^^

Install via distribute_ / setuptools_ and ``easy_install``. From the command
prompt::

    sudo apt-get install python-setuptools
    easy_install nipy

For OSX
^^^^^^^

Install via distribute_ / setuptools_ and ``easy_install``. See the distribute_
page for how to install ``easy_install`` and related tools. Then (from the
command prompt)::

    easy_install nipy

For Windows
^^^^^^^^^^^

Go to `nipy pypi`_ and download the ``.exe`` installer for nipy.  Double click
to install.

Otherwise
^^^^^^^^^

I'm afraid you might need to build from source...

.. _building_source:

Building from source code
-------------------------

Developers should look through the
:ref:`development quickstart <development-quickstart>`
documentation.  There you will find information on building NIPY, the
required software packages and our developer guidelines.

If you are primarily interested in using NIPY, download the source
tarball (e.g. from `nipy github`_) and follow these instructions for building.  The installation
process is similar to other Python packages so it will be familiar if
you have Python experience.

Unpack the source tarball and change into the source directory.  Once in the
source directory, you can build the neuroimaging package using::

    python setup.py build

To install, simply do::

    sudo python setup.py install

.. note::

    As with any Python_ installation, this will install the modules
    in your system Python_ *site-packages* directory (which is why you
    need *sudo*).  Many of us prefer to install development packages in a
    local directory so as to leave the system python alone.  This is
    merely a preference, nothing will go wrong if you install using the
    *sudo* method.  To install in a local directory, use the **--prefix**
    option.  For example, if you created a ``local`` directory in your
    home directory, you would install nipy like this::

        python setup.py install --prefix=$HOME/local

    If you have Python 2.6 or later, you might want to do a `user install
    <http://docs.python.org/2/install/index.html#alternate-installation-the-user-scheme>`_

        python setup.py install --user

Installing useful data files
-----------------------------

See :ref:`data-files` for some instructions on installing data packages.

.. include:: ../links_names.txt
