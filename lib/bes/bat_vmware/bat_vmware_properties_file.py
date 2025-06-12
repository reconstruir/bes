#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check

from bes.properties_file_v2.properties_editor import properties_editor

from .bat_bat_vmware_properties_file_formatter import bat_bat_vmware_properties_file_formatter

class bat_vmware_properties_file(properties_editor):

  def __init__(self, filename, backup = False):
    super(bat_vmware_properties_file, self).__init__(filename,
                                                 formatter = bat_bat_vmware_properties_file_formatter(),
                                                 backup = backup)
