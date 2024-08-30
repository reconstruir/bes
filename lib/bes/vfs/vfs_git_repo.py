#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple

from ..system.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.file_mime import file_mime
from bes.system.log import logger
from bes.factory.factory_field import factory_field
from bes.git.git_clone_manager import git_clone_manager
from bes.git.git_error import git_error

from .vfs_base import vfs_base
from .vfs_error import vfs_error
from .vfs_file_info import vfs_file_info
from .vfs_file_info import vfs_file_info_list
from .vfs_file_info_options import vfs_file_info_options
from .vfs_local import vfs_local

class vfs_git_repo(vfs_base):
  'Masquerade a git repo as a filesystem.  All operations are committed automatically.'

  log = logger('vfs_git_repo')
  
  def __init__(self, config_source, address, config_dir, use_lfs):
    check.check_string(config_source)
    check.check_string(address)
    check.check_string(config_dir)

    self._config_source = config_source
    self._address = address
    self._config_dir = config_dir
    self._use_lfs = use_lfs
    clone_manager_dir = path.join(self._config_dir, 'clone')
    self._clone_manager = git_clone_manager(clone_manager_dir)

  def __str__(self):
    return 'vfs_git_repo(address={})'.format(self._address)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('address', False, check.is_string),
      factory_field('config_dir', False, check.is_string),
      factory_field('use_lfs', False, factory_field.is_bool),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, config_source, **values):
    'Create an fs instance.'
    return vfs_git_repo(config_source, values['git_address'], values['git_config_dir'], values['git_use_lfs'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name of this fs.'
    return 'vfs_git_repo'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive, options):
    'List entries in a directory.'
    check.check_string(remote_dir)
    check.check_bool(recursive)
    check.check_vfs_file_info_options(options, allow_none = True)

    options = options or vfs_file_info_options()
    
    self.log.log_d('list_dir(remote_dir={}, recursive={} options={}'.format(remote_dir, recursive, options))
    proxy = self._make_proxy()
    rv = proxy.fs.list_dir(remote_dir, recursive, options)
    self._post_operation(proxy)
    return rv
  
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    proxy = self._make_proxy()
    rv = proxy.fs.has_file(remote_filename)
    self._post_operation(proxy)
    return rv
  
  #@abstractmethod
  def file_info(self, remote_filename, options):
    'Get info for a single file.'
    check.check_string(remote_filename)
    check.check_vfs_file_info_options(options, allow_none = True)

    options = options or vfs_file_info_options()

    proxy = self._make_proxy()
    rv = proxy.fs.file_info(remote_filename, options)
    self._post_operation(proxy)
    return rv
  
  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    proxy = self._make_proxy()
    proxy.repo.remove(filename)
    comment = 'remove {}'.format(filename)
    proxy.repo.commit(comment, filename)
    proxy.repo.push()
    self._post_operation(proxy)
  
  #@abstractmethod
  def upload_file(self, local_filename, remote_filename):
    'Upload local_filename to remote_filename.'
    proxy = self._make_proxy()
    proxy.fs.upload_file(local_filename, remote_filename)
    proxy.repo.add(remote_filename)
    if self._use_lfs:
      if not file_mime.content_is_text(local_filename):
        pattern = '*.{}'.format(file_util.extension(remote_filename))
        proxy.repo.lfs_track(remote_filename)
    comment = 'add {}'.format(remote_filename)
    proxy.repo.commit(comment, remote_filename)
    print('good')
    #proxy.repo.push()
    self._post_operation(proxy)

  #@abstractmethod
  def download_to_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    proxy = self._make_proxy()
    rv = proxy.fs.download_to_file(remote_filename, local_filename)
    self._post_operation(proxy)
    return rv
    
  #@abstractmethod
  def download_to_bytes(self, remote_filename):
    'Download filename to bytes.'
    proxy = self._make_proxy()
    rv = proxy.fs.download_to_bytes(remote_filename)
    self._post_operation(proxy)
    return rv
    
  #@abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    proxy = self._make_proxy()
    proxy.fs.set_file_attributes(remote_filename, attributes)
    self._post_operation(proxy)
    
  class _proxy(namedtuple('_proxy', 'repo, fs')):

    def __new__(clazz, repo, fs):
      return clazz.__bases__[0].__new__(clazz, repo, fs)
    
  def _make_proxy(self):
    repo = self._clone_manager.update(self._address)
    fs = vfs_local('<proxy>', repo.root)
    return self._proxy(repo, fs)
    
  #@abstractmethod
  def _post_operation(self, proxy):
    'Update the .bes_vfs git droppings after any operation.'
    status = proxy.repo.status('.')
    self._post_operation_update_dot_bes_vfs_dir(proxy, status)
    self._post_operation_push(proxy, status)

  def _post_operation_update_dot_bes_vfs_dir(self, proxy, status):
    rv = False
    for st in status:
      if st.filename.startswith('.bes_vfs'):
        proxy.repo.add(st.filename)
        proxy.repo.commit('update .bes_vfs db dir', st.filename)
        rv = True
    return rv

  def _post_operation_push(self, proxy, status):
    try:
      if proxy.repo.has_unpushed_commits():
        proxy.repo.push()
    except git_error as ex:
      if 'unknown commit' in str(ex).lower():
        return
      raise

  #@abstractmethod
  def mkdir(self, remote_dir):
    'Create a remote dir.  Returns the fs specific directory id if appropiate or None'
    raise vfs_error('mkdir not supported for vfs_artifactory')
