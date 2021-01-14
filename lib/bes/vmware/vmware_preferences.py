#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check

from bes.properties_file_v2.properties_editor import properties_editor
from bes.properties_file_v2.properties_file_formatter_java import properties_file_formatter_java

class vmware_preferences(properties_editor):

  def __init__(self, filename):
    super(vmware_preferences, self).__init__(filename, formatter = properties_file_formatter_java())
