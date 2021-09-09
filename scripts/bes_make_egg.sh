#!/usr/bin/env python

import argparse
import os
import os.path as path
import platform
import sys
import tarfile
import tempfile
import zipfile
import subprocess

from bes.archive.archiver import archiver
from bes.fs.temp_file import temp_file
from bes.fs.tar_util import tar_util
from bes.fs.file_util import file_util
from bes.system.log import logger
from bes.system.execute import execute
from bes.system.os_env import os_env

from bes.vmware.vmware_options_cli_args import vmware_options_cli_args

class bes_make_egg(object):

  _log = logger('bes_make_egg')

  def __init__(self):
    pass

  def main(self):
    p = argparse.ArgumentParser()
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('--version', action = 'store', default = None,
                   help = 'The version tag to make an egg from [ False ]')
    p.add_argument('--output', '-o', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'The output filename or directory [ ]')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode (do not remove temporary files) [ False ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose mode [ False ]')
    args = p.parse_args()

    print('args={}'.format(args))
    return 0
    
  @classmethod
  def run(clazz):
    raise SystemExit(bes_make_egg().main())

if __name__ == '__main__':
  bes_make_egg.run()
