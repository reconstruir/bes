# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_error import git_error

class git_ref_where(object):
  'Enumeration indicating where a ref came from.  local, remote or both'

  WHERES = ( 'local', 'remote', 'both' )
  DEFAULT_WHERE = 'local'
  
  @classmethod
  def where_is_valid(clazz, where):
    return where in clazz.WHERES

  @classmethod
  def check_where(clazz, where):
    if not where:
      return clazz.DEFAULT_WHERE
    if not clazz.where_is_valid(where):
      raise git_error('invalid "where": "{}" - should be one of local remote or both'.format(where))
    return where

  @classmethod
  def determine_where(clazz, local, remote, default_value = 'both'):
    if local is None and remote is None:
      return default_value
    local = bool(local)
    remote = bool(remote)
    if local and remote:
      return 'both'
    elif local:
      return 'local'
    elif remote:
      return 'remote'
    assert False
