#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, tarfile, tempfile, zipfile
from bes.fs import file_util, temp_file
from collections import namedtuple
from archive_extension import archive_extension

class temp_archive(object):
  'A class to deal with temporary archives mostly for unit tests.'

  Result = namedtuple('Result', [ 'file', 'filename', 'archive' ])

  class Item(object):
    'Description of an item for a temp tarball.'

    def __init__(self, arcname, content = None, filename = None):
      assert content or filename
      if content:
        assert not filename
      if filename:
        assert not content
      self.arcname = arcname
      self.content = content
      self.filename = filename
      if self.filename:
        self.content = file_util.read(self.filename)
      
  @classmethod
  def make_temp_archive(clazz, items, extension, delete = True, prefix = None):
    prefix = prefix or 'tmp_'
    assert archive_extension.is_valid_ext(extension)

    is_zip = archive_extension.is_valid_zip_ext(extension)

    archive_file = tempfile.NamedTemporaryFile(suffix = '.' + extension, prefix = prefix, delete = False)
    archive_mode = archive_extension.write_format(extension)

    if is_zip:
      archive = zipfile.ZipFile(file = archive_file, mode = archive_mode)
    else:
      archive = tarfile.open(fileobj = archive_file, mode = archive_mode)

    for item in items:
      assert item
      assert item.arcname

      tmp_content = temp_file.make_temp_file(item.content)

      if is_zip:
        archive.write(tmp_content, arcname = item.arcname)
      else:
        archive.add(tmp_content, arcname = item.arcname)

      file_util.remove(tmp_content)

    archive.close()
    archive_file.flush()
    archive_file.close()

    if delete:
      temp_file.atexit_delete(archive_file.name)

    return clazz.Result(archive_file, archive_file.name, archive)

  @classmethod
  def make_temp_item_list(clazz, items):
    'Make a list of items from a list of tuples.'

    temp_items = []
    for item in items:
      assert len(item) >= 1
      arcname = item[0]
      content = None
      if len(item) > 1:
        content = item[1]
      
      temp_items.append(clazz.Item(arcname, content = content))
    return temp_items

  @classmethod
  def add_base_dir(clazz, items, base_dir):
    'Return a new item list with base_dir prefixed to all the arcnames.'
    if not base_dir:
      return items
    def _add_base_dir(item, base_dir):
      return clazz.Item(path.join(path.normpath(base_dir), item.arcname), content = item.content)
    return [ _add_base_dir(item, base_dir) for item in items ]

  @classmethod
  def write_temp_items(clazz, items):
    'Write the temp item content to disk.  Return the tmp_dir where the items are written.'

    tmp_dir = temp_file.make_temp_dir()

    for item in items:
      assert item
      assert item.arcname
      file_util.save(path.join(tmp_dir, item.arcname), item.content)

    return tmp_dir
