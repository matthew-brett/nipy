from __future__ import division, print_function, absolute_import

import sys
import subprocess

import numpy as np


@np.deprecate_with_doc('This function will be removed soon')
def pkg_commit_hash(pkg_path):
    ''' Get short form of commit hash given directory `pkg_path`

    Nipy used to get information about which commit the package came from, from
    a file called ``COMMIT_INFO.txt`` in the nipy package directory.  We now
    use ``versioneer`` to provide this information in the package version, so
    this routine now often gives uninformative answers.  We will remove it
    soon.

    If it does return an informative answer, it is from the output of git if we
    are in a git repository.

    Otherwise, we return a not-found placeholder tuple

    Parameters
    -------------
    pkg_path : str
       directory containing package

    Returns
    ---------
    hash_from : str
       Where we got the hash from - description
    hash_str : str
       short form of hash
    '''
    # maybe we are in a repository
    proc = subprocess.Popen('git rev-parse --short HEAD',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=pkg_path, shell=True)
    repo_commit, _ = proc.communicate()
    if repo_commit:
        return 'repository', repo_commit.strip()
    return '(none found)', '<not found>'


def get_pkg_info(pkg_path):
    ''' Return dict describing the context of this package

    Parameters
    ------------
    pkg_path : str
       path containing __init__.py for package

    Returns
    ----------
    context : dict
       with named parameters of interest
    '''
    src, hsh = pkg_commit_hash(pkg_path)
    import numpy
    import nipy
    return dict(
        pkg_path=pkg_path,
        commit_source=src,
        commit_hash=hsh,
        sys_version=sys.version,
        sys_executable=sys.executable,
        sys_platform=sys.platform,
        np_version=numpy.__version__,
        nipy_version=nipy.__version__)
