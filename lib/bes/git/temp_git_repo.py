#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect

from bes.common import check
from bes.fs import temp_file
from .repo import repo as git_repo

class _method_caller(object):

  def __init__(self, target, method_name):
    self.target = target
    self.method_name = method_name

  def __call__(self, *args, **kargs):
    method = getattr(self.target, self.method_name, None)
    assert method is not None
    assert callable(method)
    return method(*args, **kargs)

class temp_git_repo(object):
  '''
  A temp git repo for unit testing that is backed by a fake "remote" repo such
  that all operations mimic the behavior of working with a cloned repo.
  '''
  
  def __init__(self, remote = True, content = None, debug = False):
    self._debug = debug
    if remote:
      self._init_remote(content)
    else:
      self._init_local(content)

  def _init_remote(self, content):
    self._remote_repo = self._make_temp_repo(init_args = [ '--bare', '--shared' ],
                                             debug = self._debug)
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug)
    if self._debug:
      print('temp_git_repo: tmp_dir: %s' % (tmp_dir))
    self._local_repo = git_repo(tmp_dir, address = self._remote_repo.root)
    self._local_repo.clone()
    
    if content:
      self._local_repo.write_temp_content(items = content, commit = True)
      self._local_repo.push('origin', 'master')
    self.root = self._local_repo.root
    self.address = self._remote_repo.root
    self._transplant_methods(self._local_repo)

  def _init_local(self, content):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug)
    if self._debug:
      print('temp_git_repo: tmp_dir: %s' % (tmp_dir))
    self._local_repo = git_repo(tmp_dir, address = None)
    self._local_repo.init()
    if content:
      self._local_repo.write_temp_content(items = content, commit = True)
    self.root = self._local_repo.root
    self.address = None
    self._transplant_methods(self._local_repo)

  def _transplant_methods(self, target):
    method_names = [ attr for attr in dir(target) if inspect.ismethod(getattr(target, attr)) ]
    method_names = [ name for name in method_names if not name.startswith('_') ]
    for method_name in method_names:
      if hasattr(self, method_name):
        raise RuntimeError('{} already has method \"{}\"'.format(self, method_name))
      setattr(self, method_name, _method_caller(target, method_name))
      
  def make_temp_cloned_repo(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self._debug)
    if self._debug:
      print('temp_git_repo: tmp_dir: %s' % (tmp_dir))
    r = git_repo(tmp_dir, address = self._remote_repo.root)
    r.clone()
    return r
      
  @classmethod
  def _make_temp_repo(clazz, init_args = None, content = None, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print('temp_git_repo: tmp_dir: %s' % (tmp_dir))
    r = git_repo(tmp_dir, address = None)
    init_args = init_args or []
    r.init(*init_args)
    if content:
      check.check_string_seq(content)
      r.write_temp_content(content, commit = True)
    return r
