#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs import file_util

class archive_extension(object):
  'Constants for different archive types.'

  BZ2 = 'bz2'
  GZ = 'gz'
  TAR = 'tar'
  TAR_BZ2 = 'tar.bz2'
  TAR_GZ = 'tar.gz'
  TGZ = 'tgz'
  ZIP = 'zip'

  VALID_ZIP_TYPES = frozenset([ ZIP ])
  VALID_TAR_TYPES = frozenset([ BZ2, GZ, TAR, TAR_BZ2, TAR_GZ, TGZ ])
  VALID_TYPES = frozenset(list(VALID_ZIP_TYPES) + list(VALID_TAR_TYPES))

  WRITE_FORMAT_MAP = {
    BZ2 : 'w:bz2',
    GZ : 'w:gz',
    TAR : 'w',
    TAR_BZ2 : 'w:bz2',
    TAR_GZ : 'w:gz',
    TGZ : 'w:gz',
    ZIP : 'w',
  }

  @classmethod
  def is_valid_ext(clazz, extension):
    return extension.lower() in clazz.VALID_TYPES

  @classmethod
  def is_valid_zip_ext(clazz, extension):
    return extension.lower() in clazz.VALID_ZIP_TYPES

  @classmethod
  def is_valid_tar_ext(clazz, extension):
    return extension.lower() in clazz.VALID_TAR_TYPES

  @classmethod
  def write_format(clazz, extension):
    return clazz.WRITE_FORMAT_MAP[extension.lower()]

  @classmethod
  def write_format_for_filename(clazz, filename):
    return clazz.write_format(file_util.extension(filename))

  @classmethod
  def is_valid_filename(clazz, filename):
    return clazz.is_valid_zip_filename(filename) or clazz.clazz.is_valid_tar_ext(filename)

  @classmethod
  def is_valid_zip_filename(clazz, filename):
    return clazz.is_valid_zip_ext(file_util.extension(filename))

  @classmethod
  def is_valid_tar_filename(clazz, filename):
    return clazz.is_valid_tar_ext(file_util.extension(filename))
