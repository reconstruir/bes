#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.system.host import host

from bes.properties_file_v2.properties_editor import properties_editor

from .vmware_preferences_formatter import vmware_preferences_formatter
from .vmware_app import vmware_app

class vmware_preferences(properties_editor):

  def __init__(self, filename = None, backup = False):
    filename = filename or self.default_preferences_filename()
    super(vmware_preferences, self).__init__(filename,
                                             formatter = vmware_preferences_formatter(),
                                             backup = backup)

  @classmethod
  def default_preferences_filename(clazz):
    return vmware_app().preferences_filename()
