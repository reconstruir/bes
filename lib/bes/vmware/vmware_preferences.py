#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.properties_file.properties_file import properties_file

class vmware_preferences(object):

  _log = logger('vmware_preferences')
  
  def __init__(self, filename):
    self._filename = filename
    self.values = properties_file.read(self._filename, style = 'java')
