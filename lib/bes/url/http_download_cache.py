#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import shutil
import os.path as path
from bes.system.log import logger
from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.compressed_file import compressed_file
from bes.git.git_address_util import git_address_util
from bes.url.url_util import url_util

class http_download_cache(object):
  'http url download cache.  Only for static content does not check server for updates.'

  log = logger('http_download_cache')
  
  def __init__(self, root_dir, compressed = False):
    '''
    Create an http cache rooted at root_dir
    If compressed is True, it will transparently compress the content locally
    and uncompress when get_url() is called.
    '''
    self.root_dir = root_dir
    self.compressed = compressed
    self.download_count = 0
    
  def has_url(self, url):
    'Return True if the tarball with address and revision is in the cache.'
    local_cached_path = self._local_path_for_url(url)
    return path.exists(local_cached_path)

  def get_url(self, url, checksum = None, cookies = None, debug = False, auth = None, uncompress = True):
    'Return the local filesystem path to the tarball with address and revision.'
    self.log.log_d('get_url: url=%s; checksum=%s; cookies=%s' % (url, checksum, cookies))
    local_cached_path = self._local_path_for_url(url)
    local_cached_path_rel = path.relpath(local_cached_path)
    self.log.log_d('get_url: local_cached_path=%s' % (local_cached_path_rel))
    if checksum:
      if path.exists(local_cached_path):
        if self._local_checksum(local_cached_path) == checksum:
          self.log.log_d('get_url: found in cache with good checksum. using: %s' % (local_cached_path_rel))
          result = self._uncompress_if_needed(local_cached_path, uncompress)
          self.log.log_d('get_url: 1 result={}'.format(result))
          return result
        else:
          self.log.log_w('get_url: found in cache with BAD checksum. removing: %s' % (local_cached_path_rel))
          file_util.remove(local_cached_path)
    else:
      if path.exists(local_cached_path):
        self.log.log_d('get_url: found in cache. using: %s' % (local_cached_path_rel))
        result = self._uncompress_if_needed(local_cached_path, uncompress)
        self.log.log_d('get_url: 2 result={}'.format(result))
        return result
    tmp = self._download_to_tmp_file(url, cookies = cookies, debug = debug, auth = auth)
    self.download_count += 1
    self.log.log_d('get_url: downloaded url to %s' % (tmp))
    if not tmp:
      self.log.log_d('get_url: failed to download: %s' % (url))
      self.log.log_d('get_url: 3 result={}'.format(None))
      return None
    if not checksum:
      if self.compressed:
        compressed_file.compress(tmp, local_cached_path)
        if uncompress:
          result = tmp
        else:
          result = local_cached_path
        self.log.log_d('get_url: 4 result={}'.format(result))
        return result
      else:
        file_util.rename(tmp, local_cached_path)
        self.log.log_d('get_url: 5 result={}'.format(local_cached_path))
        return local_cached_path
    actual_checksum = file_util.checksum('sha256', tmp)
    if actual_checksum == checksum:
      self.log.log_d('get_url: download succesful and checksum is good.  using: %s' % (local_cached_path_rel))
      if self.compressed:
        compressed_file.compress(tmp, local_cached_path)
        if uncompress:
          result = tmp
        else:
          result = local_cached_path
        self.log.log_d('get_url: 6 result={}'.format(result))
        return result
      else:
        file_util.rename(tmp, local_cached_path)
        self.log.log_d('get_url: 7 result={}'.format(local_cached_path))
        return local_cached_path
    else:
      self.log.log_e('get_url: download worked but checksum was WRONG: {}'.format(url))
      self.log.log_e('get_url:  cookies: %s' % (cookies))
      self.log.log_e('get_url: expected: %s' % (checksum))
      self.log.log_e('get_url:   actual: %s' % (actual_checksum))
      #self.log.log_e('content:\n{}\n'.format(file_util.read(tmp, codec = 'utf8')))
      self.log.log_d('get_url: 8 result={}'.format(None))
      return None
    
  def _local_path_for_url(self, url):
    'Return path for local tarball.'
    sanitized_fragment = git_address_util.sanitize_for_local_path(url)
    local_path = path.join(self.root_dir, sanitized_fragment)
    if self.compressed:
      local_path = local_path + '.gz'
    return local_path

  @classmethod
  def _download_to_tmp_file(clazz, url, cookies, debug = False, auth = None):
    'Download url to tmp file.'
    return url_util.download_to_temp_file(url, delete = not debug, cookies = cookies, auth = auth)

  def _local_checksum(self, filename):
    if self.compressed:
      tmp_uncompressed_file = temp_file.make_temp_file()
      compressed_file.uncompress(filename, tmp_uncompressed_file)
      result = file_util.checksum('sha256', tmp_uncompressed_file)
      file_util.remove(tmp_uncompressed_file)
    else:
      result = file_util.checksum('sha256', filename)

  def _uncompress_if_needed(self, filename, uncompress):
    if self.compressed:
      if uncompress:
        tmp_uncompressed_file = temp_file.make_temp_file()
        compressed_file.uncompress(filename, tmp_uncompressed_file)
        result = tmp_uncompressed_file
      else:
        result = filename
    else:
      result = filename
    return result

  def find_all_files(self, relative = True):
    'Return all files in the cache.'
    return file_find.find(self.root_dir, relative = relative)
      
check.register_class(http_download_cache, include_seq = False)
