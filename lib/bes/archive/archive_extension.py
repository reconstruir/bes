#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_util import file_util
from bes.system.log import logger

class archive_extension(object):
  'Constants for different archive types.'

  _log = logger('archive_extension')
  
  BZ2 = 'bz2'
  GZ = 'gz'
  TAR = 'tar'
  TAR_BZ2 = 'tar.bz2'
  TAR_GZ = 'tar.gz'
  TGZ = 'tgz'
  ZIP = 'zip'
  DMG = 'dmg'
  XZ = 'xz'

  VALID_ZIP_TYPES = frozenset([ ZIP ])
  VALID_TAR_TYPES = frozenset([ BZ2, GZ, TAR, TAR_BZ2, TAR_GZ, TGZ ])
  VALID_DMG_TYPES = frozenset([ DMG ])
  VALID_XZ_TYPES = frozenset([ XZ ])
  VALID_TYPES = frozenset(list(VALID_ZIP_TYPES) + list(VALID_TAR_TYPES) + list(VALID_DMG_TYPES) + list(VALID_XZ_TYPES))

  # Check order needs to have the compound tar.foo extensions first
  CHECK_ORDER = [ TAR_BZ2, TAR_GZ, BZ2, GZ, TAR, TGZ, ZIP, DMG, XZ ]
  
  WRITE_FORMAT_MAP = {
    BZ2 : 'w:bz2',
    GZ : 'w:gz',
    TAR : 'w',
    TAR_BZ2 : 'w:bz2',
    TAR_GZ : 'w:gz',
    TGZ : 'w:gz',
    ZIP : 'w',
    DMG : 'w',
    XZ : 'w',
  }

  @classmethod
  def is_valid_ext(clazz, extension):
    return extension.lower() in clazz.VALID_TYPES

  @classmethod
  def is_valid_filename(clazz, filename):
    return clazz.extension_for_filename(filename) != None

  @classmethod
  def is_valid_zip_ext(clazz, extension):
    return extension.lower() in clazz.VALID_ZIP_TYPES

  @classmethod
  def is_valid_tar_ext(clazz, extension):
    return extension.lower() in clazz.VALID_TAR_TYPES

  @classmethod
  def is_valid_dmg_ext(clazz, extension):
    return extension.lower() in clazz.VALID_DMG_TYPES

  @classmethod
  def is_valid_xz_ext(clazz, extension):
    return extension.lower() in clazz.VALID_XZ_TYPES

  @classmethod
  def write_format(clazz, extension):
    clazz._log.log_method_d()
    return clazz.WRITE_FORMAT_MAP[extension.lower()]

  @classmethod
  def write_format_for_filename(clazz, filename):
    clazz._log.log_method_d()
    return clazz.write_format(file_util.extension(filename))

  @classmethod
  def is_valid_zip_filename(clazz, filename):
    return clazz.is_valid_zip_ext(file_util.extension(filename))

  @classmethod
  def is_valid_xz_filename(clazz, filename):
    return clazz.is_valid_xz_ext(file_util.extension(filename))

  @classmethod
  def is_valid_dmg_filename(clazz, filename):
    return clazz.is_valid_dmg_ext(file_util.extension(filename))

  @classmethod
  def is_valid_tar_filename(clazz, filename):
    return clazz.is_valid_tar_ext(file_util.extension(filename))

  @classmethod
  def extension_for_filename(clazz, filename):
    filename = filename.lower()
    for ext in clazz.CHECK_ORDER:
      if filename.endswith('.' + ext):
        return ext
    return None
