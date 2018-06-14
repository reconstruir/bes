#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system import execute
from bes.fs import file_util, temp_file, tar_util

from .archive import archive
from .archive_extension import archive_extension

class archive_unix_tar(archive):
  'Deal with archives using the unix tar binary.'

  def __init__(self, filename):
    super(archive_unix_tar, self).__init__(filename)

  @classmethod
  #@abstractmethod
  def file_is_valid(clazz, filename):
    'Return True if filename is a valid file supported by this archive format.'
    try:
      tar_util.contents(self.filename)
      return True
    except Exception as ex:
      pass
    return False

  #@abstractmethod
  def _get_members(self):
    return tar_util.contents(self.filename)

  #@abstractmethod
  def has_content(self, filename):
    '''Return True if filename is part of contents.  Note that directories should end in "/" '''
    return filename in self.contents
  
  #@abstractmethod
  def extract_all(self, dest_dir, base_dir = None,
                  strip_common_ancestor = False, strip_head = None):
    dest_dir = self._determine_dest_dir(dest_dir, base_dir)
    cmd = 'tar xf %s -C %s' % (self.filename, dest_dir)
    execute.execute(cmd)
    self._handle_extract_strip_common_ancestor(self.contents, strip_common_ancestor, strip_head, dest_dir)
  
  #@abstractmethod
  def extract(self, dest_dir, base_dir = None,
              strip_common_ancestor = False, strip_head = None,
              include = None, exclude = None):
    dest_dir = self._determine_dest_dir(dest_dir, base_dir)
    filtered_contents = self._filter_for_extract(self.contents, include, exclude)
    if filtered_contents == self.contents:
      self.extract_all(dest_dir, base_dir = base_dir, strip_common_ancestor = strip_common_ancestor,
                       strip_head = strip_head)
      return
    manifest = temp_file.make_temp_file(content = '\n'.join(filtered_contents))
    cmd = 'tar xf %s -C %s -T %s' % (self.filename, dest_dir, manifest)
    execute.execute(cmd)
    self._handle_extract_strip_common_ancestor(filtered_contents, strip_common_ancestor, strip_head, dest_dir)

  #@abstractmethod
  def create(self, root_dir, base_dir = None, extra_items = None,
             include = None, exclude = None):
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    ext = archive_extension.extension_for_filename(self.filename)
    mode = archive_extension.write_format_for_filename(self.filename)
#    print('CACA: ext=%s' % (ext))
#    print('CACA: mode=%s' % (mode))
    tmp_dir = temp_file.make_temp_dir()
    for item in items:
      file_util.copy(item.filename, path.join(tmp_dir, item.arcname))
    manifest_content = '\n'.join([ item.arcname for item in items ])
    manifest = temp_file.make_temp_file(content = manifest_content)
    cmd = 'tar Jcf %s -C %s -T %s' % (self.filename, tmp_dir, manifest)
    execute.execute(cmd)
    file_util.remove(tmp_dir)
