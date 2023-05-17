#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
import sys

from bes.system.check import check
from bes.fs.file_check import file_check
from bes.fs.file_util import file_util

from .json_util import json_util

class json_read_write_mixin:

  def save_json_file(self, filename = None, encoding = 'utf-8'):
    check.check_string(filename, allow_none = True)
    check.check_string(encoding)

    js = self.to_json()
    if filename == None:
      sys.stdout.write(js)
      return
    with open(filename, 'w', encoding = encoding) as f:
      f.write(js)

  def to_json(self):
    o = self.to_json_object()
    return json_util.to_json(o, indent = 2)
      
  @classmethod
  def read_json_file(clazz, filename, encoding = 'utf-8'):
    filename = file_check.check_file(filename)

    with open(filename, 'r', encoding = encoding) as f:
      js = f.read()
      o = json.loads(js)
      return clazz.from_json_object(o)
