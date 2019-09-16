#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
#import re
#from collections import namedtuple

from .vfs_path_util import vfs_path_util

class vfs_path(object):

  _SEP = '/'
  
  def __init__(self, path):
    self._path = vfs_path_util.normalize(path)
    
  def __add__(self, other): 
    return vfs_path(self._path + self._SEP + vfs_path_util.lstrip_sep(other._path))

  def __str__(self): 
    return self._path

  def __eq__(self, other): 
    return self._path == other._path

  @property
  def path(self):
    return self._path

  @cached_property
  def abs_path(self):
    return vfs_path_util.ensure_lsep(self._path)
  
  @cached_property
  def rel_path(self):
    return vfs_path_util.lstrip_sep(self._path)
  
  @cached_property
  def parts(self):
    return vfs_path_util.split(self._path)
  
  @cached_property
  def basename(self):
    'Same as path.basename()'
    if self._path in [ '', self._SEP ]:
      return ''
    return self.parts[-1]

  @cached_property
  def dirname(self):
    'Same as path.dirname()'
    if self._path in [ '' ]:
      return ''
    if self._path in [ self._SEP ]:
      return self._SEP
    self._path = vfs_path_util.rstrip_sep(self._path)
    parts = self.parts[0:-1]
    if parts in [ [ '']  ]:
      return '/'
    return vfs_path_util.join(*parts)
