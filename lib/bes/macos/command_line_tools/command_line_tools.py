#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.which import which

from bes.native_package.native_package import native_package

class command_line_tools(object):
  'Class to deal with the command_line_tools executable.'
  
  @classmethod
  def installed(clazz):
    'Return True of command line tools are installed.'

    exe = which.which('xcode-select')
    if not exe:
      return False
    np = native_package()
    return np.owner(exe) != None
