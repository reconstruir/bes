#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check

from bes.properties_file_v2.properties_editor import properties_editor

from .vmware_properties_file_formatter import vmware_properties_file_formatter

class vmware_properties_file(properties_editor):

  def __init__(self, filename, backup = False):
    super(vmware_properties_file, self).__init__(filename,
                                                 formatter = vmware_properties_file_formatter(),
                                                 backup = backup)
