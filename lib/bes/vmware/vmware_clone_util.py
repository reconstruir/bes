#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import tempfile

from ..system.check import check
from bes.common.string_util import string_util
from bes.common.time_util import time_util
from bes.fs.file_util import file_util

class vmware_clone_util(object):

  @classmethod
  def _tmp_nickname_part(clazz):
    d = tempfile.mkdtemp(prefix = 'tmp')
    b = path.basename(d)
    file_util.remove(d)
    return string_util.remove_head(b, 'tmp')

  _cloned_vm_names = namedtuple('_cloned_vm_names', 'src_vmx_filename, dst_vmx_filename, dst_vmx_nickname, timestamp')
  def make_cloned_vm_names(clazz, src_vmx_filename, clone_name, where):
    check.check_string(src_vmx_filename)
    check.check_string(clone_name)
    check.check_string(where)
    
    vms_root_dir = path.normpath(path.join(path.dirname(src_vmx_filename), path.pardir))
    src_vmx_nickname = bat_bat_vmware_vmx_file(src_vmx_filename).nickname
    tmp_nickname_part = clazz._tmp_nickname_part()
    if not clone_name:
      clone_name = '{}_clone_{}'.format(src_vmx_nickname, tmp_nickname_part)
    new_vm_root_dir_basename = '{}.vmwarevm'.format(clone_name)
    if not where:
      where = path.join(vms_root_dir, new_vm_root_dir_basename)
    file_util.mkdir(where)
    dst_vmx_basename = '{}.vmx'.format(clone_name)
    dst_vmx_filename = path.join(where, dst_vmx_basename)
    return clazz._cloned_vm_names(src_vmx_filename, dst_vmx_filename, clone_name)
  
  @classmethod
  def timestamp(clazz):
    return time_util.timestamp(delimiter = '', milliseconds = False)

  @classmethod
  def make_dst_vmx_filename(clazz, src_vmx_filename, clone_name, where):
    check.check_string(src_vmx_filename)
    check.check_string(clone_name)
    check.check_string(where, allow_none = True)
    
    vms_root_dir = path.normpath(path.join(path.dirname(src_vmx_filename), path.pardir))
    new_vm_root_dir_basename = '{}.vmwarevm'.format(clone_name)
    if not where:
      where = path.join(vms_root_dir, new_vm_root_dir_basename)
    file_util.mkdir(where)
    dst_vmx_basename = '{}.vmx'.format(clone_name)
    dst_vmx_filename = path.join(where, dst_vmx_basename)
    return dst_vmx_filename
