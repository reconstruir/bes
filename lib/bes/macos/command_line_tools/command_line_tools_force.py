#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.system.log import logger

class command_line_tools_force(object):

  _log = logger('command_line_tools')
  
  # touching this file forces softwareupdate to list the xcode command line tools
  _FORCE_COMMAND_LINE_TOOLS_FILE = '/tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress'
  
  def __init__(self):
    self._log.log_i('command_line_tools_force: __init__()')
    
  def __enter__(self):
    self._log.log_i('command_line_tools_force: __enter__()')
    file_util.save(self._FORCE_COMMAND_LINE_TOOLS_FILE)
    return self
  
  def __exit__(self, type, value, traceback):
    self._log.log_i('command_line_tools_force: __exit__()')
    file_util.remove(self._FORCE_COMMAND_LINE_TOOLS_FILE)
