#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util

class vmware_vmx(object):
  'Class do deal with vmware vmx files'
  
  @classmethod
  def vmx_filename_nickname(clazz, vmx_filename):
    'Return the nickname for a vmx file'
    i = vmx_filename.rfind('/')
    if i < 0:
      return None
    vmx = vmx_filename[i + 1:]
    return string_util.remove_tail(vmx, '.vmx')
