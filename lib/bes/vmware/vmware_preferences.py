#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.system.host import host

from bes.properties_file_v2.properties_editor import properties_editor
from bes.properties_file_v2.properties_file_formatter_java import properties_file_formatter_java

class vmware_preferences(properties_editor):

  DEFAULT_PREFERENCES_FILE = None
  if host.is_macos():
    DEFAULT_PREFERENCES_FILE = path.expanduser('~/Library/Preferences/VMware Fusion/preferences')
  
  def __init__(self, filename = None):
    filename = filename or self.DEFAULT_PREFERENCES_FILE
    super(vmware_preferences, self).__init__(filename, formatter = properties_file_formatter_java())

    
