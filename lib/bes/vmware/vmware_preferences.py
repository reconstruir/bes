#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from ..system.check import check
from bes.system.host import host

from .vmware_app import vmware_app
from .vmware_properties_file import vmware_properties_file

class vmware_preferences(vmware_properties_file):

  def __init__(self, filename = None, backup = False):
    super(vmware_preferences, self).__init__(filename, backup = backup)

  @classmethod
  def default_preferences_filename(clazz):
    return vmware_app.preferences_filename()
