#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.property.cached_property import cached_property

from .vmware_error import vmware_error

class vmware_vmx_file(object):
  'Class do deal with vmware vmx files'

  def __init__(self, filename):
    self.filename = filename

  @cached_property
  def nickname(self):
    'Return the nickname for a the vmx file'
    i = self.filename.rfind('/')
    if i < 0:
      return None
    vmx = self.filename[i + 1:]
    return string_util.remove_tail(vmx, '.vmx')

  @classmethod
  def is_vmx_file(clazz, filename):
    'Return True if filename is a vmx file'
    if not path.exists(filename):
      return False
    if not path.isfile(filename):
      raise vmware_error('Directory found instead of file: "{}"'.format(filename))
    if not file_mime.is_text(filename):
      return False
    content = file_util.read(filename, codec = 'utf-8')
    if not '.encoding = ' in content:
      return False
    if not 'config.version = ' in content:
      return False
    return True

  @classmethod
  def check_vmx_file(clazz, filename):
    'Raise an exception if filename is not a vmware vmx file.'
    check.check_string(filename)

    if not clazz.is_vmx_file(filename):
      raise vmware_error('Not a vmware vmx file: "{}"'.format(filename))
    return filename
