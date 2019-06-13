#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path, tarfile, tempfile, zipfile

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.execute import execute

from .archive_extension import archive_extension

class temp_archive(object):
  'A class to deal with temporary archives mostly for unit tests.'

  class item(namedtuple('item', 'arcname, content, filename')):

    def __new__(clazz, arcname, content = None, filename = None):
      assert content or filename
      if content:
        assert not filename
      if filename:
        assert not content
      if filename:
        content = file_util.read(filename)
      return clazz.__bases__[0].__new__(clazz, arcname, content, filename)

  @classmethod
  def _determine_type(clazz, extension):
    if archive_extension.is_valid_zip_ext(extension):
      return 'zip'
    elif archive_extension.is_valid_tar_ext(extension):
      return 'tar'
    elif archive_extension.is_valid_dmg_ext(extension):
      return 'dmg'
    elif archive_extension.is_valid_xz_ext(extension):
      return 'xz'
    else:
      return None
        
  @classmethod
  def make_temp_archive(clazz, items, extension, delete = True, prefix = None):
    prefix = prefix or 'tmp_'
    assert archive_extension.is_valid_ext(extension)
    ext_type = clazz._determine_type(extension)
    assert ext_type

    temp_archive_filename = temp_file.make_temp_file(suffix = '.' + extension, prefix = prefix, delete = False)
    archive_mode = archive_extension.write_format(extension)

    if ext_type == 'zip':
      clazz._make_temp_archive_zip(items, temp_archive_filename, archive_mode)
    elif ext_type == 'tar':
      clazz._make_temp_archive_tar(items, temp_archive_filename, archive_mode)
    elif ext_type == 'dmg':
      clazz._make_temp_archive_dmg(items, temp_archive_filename, archive_mode)
    elif ext_type == 'xz':
      clazz._make_temp_archive_xz(items, temp_archive_filename, archive_mode)

    if delete:
      temp_file.atexit_delete(temp_archive_filename)

    return temp_archive_filename

  @classmethod
  def _make_temp_archive_zip(clazz, items, filename, mode):
    with open(filename, 'wb') as fp:
      archive = zipfile.ZipFile(file = fp, mode = mode)
      for item in items:
        assert item
        assert item.arcname
        tmp_content = temp_file.make_temp_file(item.content)
        archive.write(tmp_content, arcname = item.arcname)
        file_util.remove(tmp_content)
      archive.close()
      fp.flush()
      fp.close()
      
  @classmethod
  def _make_temp_archive_tar(clazz, items, filename, mode):
    with open(filename, 'wb') as fp:
      archive = tarfile.open(fileobj = fp, mode = mode)
      for item in items:
        assert item
        assert item.arcname
        tmp_content = temp_file.make_temp_file(item.content)
        archive.add(tmp_content, arcname = item.arcname)
        file_util.remove(tmp_content)
      archive.close()
      fp.flush()
      fp.close()
    
  @classmethod
  def _make_temp_archive_dmg(clazz, items, filename, mode):
    tmp_dir = temp_file.make_temp_dir()
    for item in items:
      assert item
      assert item.arcname
      file_util.save(path.join(tmp_dir, item.arcname), content = item.content)
    tmp_dmg = temp_file.make_temp_file()
    cmd = 'hdiutil create -srcfolder %s -ov -format UDZO %s' % (tmp_dir, filename)
    execute.execute(cmd)
    file_util.remove(tmp_dir)
    
  @classmethod
  def _make_temp_archive_xz(clazz, items, filename, mode):
    tmp_dir = temp_file.make_temp_dir()
    for item in items:
      assert item
      assert item.arcname
      file_util.save(path.join(tmp_dir, item.arcname), content = item.content)
    tmp_xz = temp_file.make_temp_file()
    manifest_content = '\n'.join([ item.arcname for item in items ])
    manifest = temp_file.make_temp_file(content = manifest_content)
    cmd = 'tar Jcf %s -C %s -T %s' % (filename, tmp_dir, manifest)
    execute.execute(cmd)
    file_util.remove(tmp_dir)
    
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
      
      temp_items.append(clazz.item(arcname, content = content))
    return temp_items

  @classmethod
  def add_base_dir(clazz, items, base_dir):
    'Return a new item list with base_dir prefixed to all the arcnames.'
    if not base_dir:
      return items
    def _add_base_dir(item, base_dir):
      return clazz.item(path.join(path.normpath(base_dir), item.arcname), content = item.content)
    return [ _add_base_dir(item, base_dir) for item in items ]

  @classmethod
  def write_temp_items(clazz, items):
    'Write the temp item content to disk.  Return the tmp_dir where the items are written.'
    tmp_dir = temp_file.make_temp_dir()
    clazz.write_items(tmp_dir, items)
    return tmp_dir

  @classmethod
  def write_items(clazz, root_dir, items):
    'Write the content to disk.'
    for item in items:
      assert item
      assert item.arcname
      file_util.save(path.join(root_dir, item.arcname), item.content)
