#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from .version_info import version_info

class version_cli(object):
  
  def __init__(self, mod):
    self._info = version_info.version_info_for_module(mod)

  def __str__(self):
    return self._info.version_string(delimiter = ' ')
    
  def version_add_arguments(self, parser):
    parser.add_argument('--version',
                        '-V',
                        action = 'store_true',
                        default = False,
                        help = 'Show version [ False ]')
    
  def version_print_version(self, stream = sys.stdout, delimiter = ' '):
    stream.write(self._info.version_string(delimiter = delimiter))
    stream.write('\n')
    stream.flush()
