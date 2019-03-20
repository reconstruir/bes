#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import shutil
import os.path as path
from bes.system import log
from bes.common import check, string_util
from bes.fs import file_util
from bes.git import git_util
from bes.url import url_util

class http_download_cache(object):
  'http url download cache.  Only for static content does not check server for updates.'

  def __init__(self, root_dir):
    self.root_dir = root_dir
    
  def has_url(self, url):
    'Return True if the tarball with address and revision is in the cache.'
    local_cached_path = self._path_for_url(url)
    return path.exists(local_cached_path)

  def get_url(self, url, checksum = None, cookies = None, debug = False, auth = None):
    'Return the local filesystem path to the tarball with address and revision.'
    self.log_d('get_url: url=%s; checksum=%s; cookies=%s' % (url, checksum, cookies))
    local_cached_path = self._path_for_url(url)
    local_cached_path_rel = path.relpath(local_cached_path)
    self.log_d('get_url: local_cached_path=%s' % (local_cached_path_rel))
    if checksum:
      if path.exists(local_cached_path):
        if file_util.checksum('sha256', local_cached_path) == checksum:
          self.log_d('get_url: found in cache with good checksum. using: %s' % (local_cached_path_rel))
          return local_cached_path
        else:
          self.log_w('get_url: found in cache with BAD checksum. removing: %s' % (local_cached_path_rel))
          file_util.remove(local_cached_path)
    else:
      if path.exists(local_cached_path):
        self.log_d('get_url: found in cache. using: %s' % (local_cached_path_rel))
        return local_cached_path
    tmp = self._download_to_tmp_file(url, cookies = cookies, debug = debug, auth = auth)
    self.log_d('get_url: downloaded url to %s' % (tmp))
    if not tmp:
      self.log_d('get_url: failed to download: %s' % (url))
      return None
    if not checksum:
      file_util.rename(tmp, local_cached_path)
      return local_cached_path
    actual_checksum = file_util.checksum('sha256', tmp)
    if actual_checksum == checksum:
      self.log_d('get_url: download succesful and checksum is good.  using: %s' % (local_cached_path_rel))
      file_util.rename(tmp, local_cached_path)
      return local_cached_path
    else:
      self.log_e('get_url: download worked but checksum was WRONG: %s' % (url))
      self.log_e('get_url: expected: %s' % (checksum))
      self.log_e('get_url:   actual: %s' % (actual_checksum))
      return None
    
  def _path_for_url(self, url):
    'Return path for local tarball.'
    return path.join(self.root_dir, git_util.sanitize_address(url))

  @classmethod
  def _download_to_tmp_file(clazz, url, cookies, debug = False, auth = None):
    'Download url to tmp file.'
    return url_util.download_to_temp_file(url, delete = not debug, cookies = cookies, auth = auth)
  
check.register_class(http_download_cache, include_seq = False)
log.add_logging(http_download_cache)
