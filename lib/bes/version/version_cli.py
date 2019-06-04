#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.python.code import code

from .version_info import version_info

class version_cli(object):
  
  def __init__(self, mod):
    self.info = version_info.version_info_for_module(mod)

  def __str__(self):
    return self.info.version_string(delimiter = ' ')
    
  def version_add_arguments(self, parser):
    parser.add_argument('--version',
                        '-V',
                        action = 'store_true',
                        default = False,
                        help = 'Show version [ False ]')

  @classmethod
  def arg_sub_parser_add_arguments(clazz, parser):
    parser.add_argument('-a', '--all',
                        action = 'store_true',
                        default = False,
                        dest = 'print_all')
    parser.add_argument('-b', '--brief',
                        action = 'store_true',
                        default = False)
    
  def version_print_version(self, stream = sys.stdout, delimiter = ' ', brief = False):
    stream.write(self.info.version_string(delimiter = delimiter, brief = brief))
    stream.write('\n')
    stream.flush()

  @classmethod
  def print_everything(clazz, component, dependencies = None,
                       stream = sys.stdout, delimiter = ' ',
                       brief = False, print_all = False):
    check.check_string(component)
    check.check_string_seq(dependencies, allow_none = True)
    dependencies = dependencies or []
    component_module = __import__(component)
    component_version = version_cli(component_module)
    component_version.version_print_version(stream = stream, delimiter = delimiter, brief = brief)
    if print_all:
      for dep in dependencies:
        mod = __import__(dep)
        ver = version_cli(mod)
        stream.write('  %s: ' % (dep))
        version_cli(mod).version_print_version(stream = stream, delimiter = delimiter, brief = brief)
    return 0
    
