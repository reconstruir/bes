#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util

from .vmware_error import vmware_error

class vmware_vmx_file(object):
  'Class do deal with vmware vmx files'
  
  @classmethod
  def nickname(clazz, vmx_filename):
    'Return the nickname for a vmx file'
    i = vmx_filename.rfind('/')
    if i < 0:
      return None
    vmx = vmx_filename[i + 1:]
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
