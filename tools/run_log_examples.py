#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
from __future__ import print_function, with_statement

DESCRIP = 'Run and log examples'
EPILOG = \
""" Run examples in directory

Typical usage is:

run_log_examples.py nipy/examples --log-path=~/tmp/eg_logs
"""

import sys
import os
from os.path import abspath, expanduser, join as pjoin
from subprocess import Popen

from nipy.externals.argparse import (ArgumentParser,
                                     RawDescriptionHelpFormatter)


PYTHON=sys.executable
NEED_SHELL = True

class ProcLogger(object):
    def __init__(self, log_path, working_path):
        self.log_path = log_path
        self.working_path = working_path
        self._names = []

    def cmd_str_maker(self, cmd, args):
        return " ".join([cmd] + list(args))

    def __call__(self, cmd_name, cmd, args=(), cwd=None):
        # Mqke log files
        if cmd_name in self._names:
            raise ValueError('Command name {0} not unique'.format(cmd_name))
        if cwd is None:
            cwd = self.working_path
        cmd_out_path = pjoin(self.log_path, cmd_name)
        stdout_log = open(cmd_out_path + '.stdout', 'wt')
        stderr_log = open(cmd_out_path + '.stderr', 'wt')
        try:
            # Start subprocess
            cmd_str = self.cmd_str_maker(cmd, args)
            proc = Popen(cmd_str,
                        cwd = cwd,
                        stdout = stdout_log,
                        stderr = stderr_log,
                        shell = NEED_SHELL)
            # Execute
            retcode = proc.wait()
        finally:
            stdout_log.close()
            stderr_log.close()
        return retcode


class PyProcLogger(ProcLogger):
    def cmd_str_maker(self, cmd, args):
        """ Execute python script `cmd`

        Reject any `args` because we're using ``exec`` to execute the script.

        Prepend some matplotlib setup to suppress figures
        """
        if len(args) != 0:
            raise ValueError("Cannot use args with {8}".format(self.__class__))
        return("""{0} -c "import matplotlib as mpl; mpl.use('agg'); """
               """exec(open('{1}', 'rt').read())" """.format(PYTHON, cmd))


def main():
    parser = ArgumentParser(description=DESCRIP,
                            epilog=EPILOG,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('examples_path', type=str,
                        help='directory containing examples')
    parser.add_argument('--log-path', type=str, required=True,
                        help='path for output logs')
    args = parser.parse_args()
    # Proc runner
    eg_path = abspath(expanduser(args.examples_path))
    log_path = abspath(expanduser(args.log_path))
    proc_logger = PyProcLogger(log_path=log_path,
                               working_path=eg_path)
    fails = 0
    with open(pjoin(log_path, 'summary.txt'), 'wt') as f:
        for dirpath, dirnames, filenames in os.walk(eg_path):
            for fname in filenames:
                if fname.endswith(".py"):
                    full_fname = pjoin(dirpath, fname)
                    print(fname, end=': ')
                    sys.stdout.flush()
                    code = proc_logger(fname, full_fname, cwd=dirpath)
                    fail = code != 0
                    fail_txt = "FAIL" if fail else "OK"
                    print(fail_txt)
                    f.write('{0}: {1}\n'.format(fname, fail_txt))
                    if fails < 255:
                        fails += fail
    exit(fails)


if __name__ == '__main__':
    main()
