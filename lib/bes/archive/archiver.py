#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from ..system.check import check
from bes.common.object_util import object_util
from bes.fs.file_cache import file_cache
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.host import host

from .archive_base import archive_base
from .archive_dmg import archive_dmg
from .archive_extension import archive_extension
from .archive_tar import archive_tar
from .archive_xz import archive_xz
from .archive_zip import archive_zip
from .archive_operation_base import archive_operation_base
from .archive_operation_add_file import archive_operation_add_file
from .archive_operation_remove_files import archive_operation_remove_files
from .archive_operation_replace_file import archive_operation_replace_file

class archiver(object):
  'Class to deal with archives.'

  item = archive_base.item
  
  @classmethod
  def is_valid(clazz, filename):
    if not path.exists(filename):
      return False
    if not path.isfile(filename):
      return False
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      return False
    return archive_class.file_is_valid(filename)
  
  @classmethod
  def members(clazz, filename):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).members

  @classmethod
  def file_members(clazz, filename):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).file_members

  @classmethod
  def dir_members(clazz, filename):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).dir_members

  @classmethod
  def has_member(clazz, filename, member):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).has_member(member)

  @classmethod
  def extract_all(clazz, filename, dest_dir, base_dir = None,
                  strip_common_ancestor = False, strip_head = None):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    archive = archive_class(filename)
    archive.extract_all(dest_dir,
                        base_dir = base_dir,
                        strip_common_ancestor = strip_common_ancestor,
                        strip_head = strip_head)
    
  @classmethod
  def extract_all_temp_dir(clazz, filename, base_dir = None,
                           strip_common_ancestor = False, strip_head = None, delete = True):
    tmp_dir = temp_file.make_temp_dir(delete = delete)
    clazz.extract_all(filename, tmp_dir, base_dir = base_dir,
                      strip_common_ancestor = strip_common_ancestor, strip_head = strip_head)
    return tmp_dir

  @classmethod
  def extract(clazz, filename, dest_dir, base_dir = None,
              strip_common_ancestor = False, strip_head = None,
              include = None, exclude = None):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    archive = archive_class(filename)
    return archive.extract(dest_dir,
                           base_dir = base_dir,
                           strip_common_ancestor = strip_common_ancestor,
                           strip_head = strip_head,
                           include = include,
                           exclude = exclude)

  @classmethod
  def extract_member_to_string(clazz, archive, member, codec = None):
    archive_class = clazz._determine_type(archive)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (archive))
    return archive_class(archive).extract_member_to_string(member, codec = codec)

  @classmethod
  def extract_member_to_string_cached(clazz, archive, member, cache_dir = None):
    from .archive_member_cache_item import archive_member_cache_item
    item = archive_member_cache_item(archive, member)
    return file_cache.cached_item(item, cache_dir)
  
  @classmethod
  def extract_member_to_file(clazz, archive, member, filename):
    archive_class = clazz._determine_type(archive)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (archive))
    archive_class(archive).extract_member_to_file(member, filename)

  @classmethod
  def extract_member_to_temp_file(clazz, archive, member, delete = True):
    tmp_filename = temp_file.make_temp_file(suffix = '-' + path.basename(member), delete = delete, non_existent = True)
    clazz.extract_member_to_file(archive, member, tmp_filename)
    return tmp_filename

  @classmethod
  def member_checksum(clazz, archive, member):
    tmp_file = clazz.extract_member_to_temp_file(archive, member)
    chk = file_util.checksum('sha256', tmp_file)
    file_util.remove(tmp_file)
    return chk
    
  @classmethod
  def create(clazz, filename, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None,
             extension = None):
    if extension:
      archive_class = clazz._determine_type_for_ext(extension)
    else:
      archive_class = clazz._determine_type_for_create(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    archive_class(filename).create(root_dir,
                                   base_dir = base_dir,
                                   extra_items = extra_items,
                                   include = include,
                                   exclude = exclude,
                                   extension = extension)

  @classmethod
  def recreate(clazz, archive, output_archive, base_dir):
    'Recreate the archive with the new a base_dir.  output_archive can be same as archive.'
    tmp_archive = clazz.recreate_temp_file(archive, base_dir)
    file_util.rename(tmp_archive, output_archive)
    
  @classmethod
  def recreate_temp_file(clazz, archive, base_dir, delete = True):
    'Recreate the archive to a temp file.'
    tmp_dir = temp_file.make_temp_dir(delete = True)
    clazz.extract_all(archive, tmp_dir)
    return clazz.create_temp_file(archive_extension.extension_for_filename(archive), tmp_dir, base_dir = base_dir)
    
  @classmethod
  def create_temp_file(clazz, extension, root_dir, base_dir = None,
                       extra_items = None,
                       include = None, exclude = None, delete = True):
    if not archive_extension.is_valid_ext(extension):
      raise ValueError('invalid extension: {}'.format(extension))
    tmp_archive = temp_file.make_temp_file(suffix = '.' + extension, delete = delete, non_existent = True)
    archiver.create(tmp_archive, root_dir, base_dir = base_dir,
                    extra_items = extra_items,
                    include = include, exclude = exclude)
    return tmp_archive

  @classmethod
  def common_base(clazz, filename):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).common_base()

  @classmethod
  def _determine_type(clazz, filename):
    possible = [ archive_tar, archive_zip, archive_xz ] 
    if host.is_macos():
      possible.append(archive_dmg)
    for p in possible:
      if p.file_is_valid(filename):
        return p
    return None

  @classmethod
  def _determine_type_for_create(clazz, filename):
    if archive_extension.is_valid_tar_filename(filename):
      return archive_tar
    elif archive_extension.is_valid_zip_filename(filename):
      return archive_zip
    elif archive_extension.is_valid_xz_filename(filename):
      return archive_xz
    elif archive_extension.is_valid_dmg_filename(filename):
      return archive_dmg
    return None

  @classmethod
  def _determine_type_for_ext(clazz, ext):
    if archive_extension.is_valid_tar_ext(ext):
      return archive_tar
    elif archive_extension.is_valid_zip_ext(ext):
      return archive_zip
    elif archive_extension.is_valid_xz_ext(ext):
      return archive_xz
    elif archive_extension.is_valid_dmg_ext(ext):
      return archive_dmg
    return None

  @classmethod
  def common_files(clazz, archives):
    'Return a list of files common to 2 or more archives.' 
    sets = [ set(clazz.members(a)) for a in archives ]
    return list(set.intersection(*sets))

  @classmethod
  def find_archives(clazz, where, relative = True):
    'Return valid archives found recursively in where.' 
    files = file_find.find(where, relative = relative, file_type = file_find.FILE)
    if relative:
      files = [ f for f in files if archiver.is_valid(path.join(where, f)) ]
    else:
      files = [ f for f in files if archiver.is_valid(f) ]
    return files

  @classmethod
  def format_name(clazz, filename):
    'Return the name of the archive format.  zip, tar, dmg, xz or unix_tar.'
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      return None
    return archive_class.name(filename)

  operation_base = archive_operation_base
  operation_add_file = archive_operation_add_file
  operation_remove_files = archive_operation_remove_files
  operation_replace_file = archive_operation_replace_file
  @classmethod
  def transform(clazz, archive, operations):
    'Transform an archive with one or more operations.'
    check.check_string(archive)
    operations = object_util.listify(operations)
    check.check_archive_operation_seq(operations)
    tmp_dir = clazz.extract_all_temp_dir(archive)
    for operation in operations:
      if not check.is_archive_operation(operation):
        raise TypeError('Operation should be a subclass of archive_operation_base: {}'.format(operation))
      operation.execute(tmp_dir)
    tmp_new_archive = clazz.create_temp_file(archive_extension.extension_for_filename(archive), tmp_dir)
    file_util.remove(archive)
    file_util.rename(tmp_new_archive, archive)

  @classmethod
  def is_empty(clazz, filename):
    return len(clazz.members(filename)) == 0
