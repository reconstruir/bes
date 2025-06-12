#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from ..system.check import check
from bes.system.host import host

from .bat_vmware_app import bat_vmware_app
from .bat_vmware_properties_file import bat_vmware_properties_file

class bat_vmware_preferences(bat_vmware_properties_file):

  def __init__(self, filename = None, backup = False):
    super(bat_vmware_preferences, self).__init__(filename, backup = backup)

  @classmethod
  def default_preferences_filename(clazz):
    return bat_vmware_app.preferences_filename()
