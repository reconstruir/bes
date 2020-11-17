#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass, os.path as path, subprocess

#from bes.common.json_util import json_util
from bes.system.host import host

from .software_updater_item import software_updater_item

class software_updater(object):
  'Class to deal with the macos softwareupdate program.'

  @classmethod
  def _parse_list_output(clazz, text):
    'Parse the output of softwareupdate --list.'
    return []
