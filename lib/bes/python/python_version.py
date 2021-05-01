#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.version.semantic_version import semantic_version
from bes.property.cached_property import cached_property

from .python_error import python_error

class python_version(object):
  'Class to deal with python versions.'

  def __init__(self, version):
    if check.is_python_version(version):
      version = str(version)
    elif check.is_int(version):
      version = str(version)
    self._ver = semantic_version(version)
    if len(self._ver) not in ( 1, 2, 3 ):
      raise python_error('Invalid python version: "{}"'.format(version))

  def __str__(self):
    return '.'.join([ str(part) for part in self.parts ])

  def __repr__(self):
    return str(self)
  
  def __len__(self):
    return len(self._ver)

  def __eq__(self, other):
    if not check.is_python_version(other):
      other = python_version(other)
    check.check_python_version(other)
    
    if len(self) != len(other):
      raise python_error('Incompatible versions: "{}" vs "{}"'.format(self, other))
    return self._ver == other._ver

  def __ne__(self, other):
    if not check.is_python_version(other):
      other = python_version(other)
    check.check_python_version(other)
    
    if len(self) != len(other):
      raise python_error('Incompatible versions: "{}" vs "{}"'.format(self, other))
    return self._ver != other._ver

  def __lt__(self, other):
    if not check.is_python_version(other):
      other = python_version(other)
    check.check_python_version(other)
    
    if len(self) != len(other):
      raise python_error('Incompatible versions: "{}" vs "{}"'.format(self, other))
    return self._ver < other._ver

  def __le__(self, other):
    if not check.is_python_version(other):
      other = python_version(other)
    check.check_python_version(other)
    
    if len(self) != len(other):
      raise python_error('Incompatible versions: "{}" vs "{}"'.format(self, other))
    return self._ver <= other._ver

  def __gt__(self, other):
    if not check.is_python_version(other):
      other = python_version(other)
    check.check_python_version(other)
    
    if len(self) != len(other):
      raise python_error('Incompatible versions: "{}" vs "{}"'.format(self, other))
    return self._ver > other._ver

  def __ge__(self, other):
    if not check.is_python_version(other):
      other = python_version(other)
    check.check_python_version(other)
    
    if len(self) != len(other):
      raise python_error('Incompatible versions: "{}" vs "{}"'.format(self, other))
    return self._ver >= other._ver
  
  @cached_property
  def parts(self):
    return self._ver.parts
  
  @cached_property
  def major_version(self):
    'Return major'
    return python_version(str(self._ver[0]))

  @cached_property
  def major_version_str(self):
    'Return major'
    return str(self.major_version)
  
  @cached_property
  def version(self):
    'Return major.minor'
    if len(self) < 2:
      raise python_error('Not a possible version: "{}"'.format(str(self)))
    return python_version('{}.{}'.format(self._ver[0], self._ver[1]))

  @cached_property
  def version_str(self):
    'Return major'
    return str(self.version)
  
  @cached_property
  def full_version(self):
    'Return major.minor.revision'
    if len(self) < 3:
      raise python_error('Not a possible full_version: "{}"'.format(str(self)))
    return python_version('{}.{}.{}'.format(self._ver[0], self._ver[1], self._ver[2]))

  @cached_property
  def full_version_str(self):
    'Return major'
    return str(self.full_version)
  
  @cached_property
  def major(self):
    'Return the major part'
    if len(self._ver) < 1:
      return None
    return self._ver[0]

  @cached_property
  def major_str(self):
    'Return the major part'
    return str(self.major)
  
  @cached_property
  def minor(self):
    'Return the minor part'
    if len(self._ver) < 2:
      return None
    return self._ver[1]

  @cached_property
  def minor_str(self):
    'Return the minor part'
    return str(self.minor)
  
  @cached_property
  def revision(self):
    'Return the revision part'
    if len(self._ver) < 3:
      return None
    return self._ver[2]

  @cached_property
  def revision_str(self):
    'Return the revision part'
    return str(self.revision)
  
  def is_version(self):
    'Return True if version is in the form major.minor'
    return len(self._ver) == 2

  def is_full_version(self):
    'Return True if version is in the form major.minor.revision'
    return len(self._ver) == 3

  def is_major_version(self):
    'Return True if version is in the form major'
    return len(self._ver) == 1

  @classmethod
  def check_version(clazz, version):
    'Check version is a x.y version or raise an error if not'
    check.check_string(version)

    try:
      if python_version(version).is_version():
        return version
    except python_error as ex:
      raise

  @classmethod
  def check_full_version(clazz, version):
    'Check version is a x.y.z version or raise an error if not'
    check.check_string(version)

    try:
      if python_version(version).is_full_version():
        return version
    except python_error as ex:
      raise

  @classmethod
  def check_major_version(clazz, version):
    'Check version is a x version or raise an error if not'
    check.check_string(version)

    try:
      if python_version(version).is_major_version():
        return version
    except python_error as ex:
      raise

  def join_parts(self, delimiter):
    'Check version is a x version or raise an error if not'
    check.check_string(delimiter)
    return delimiter.join([ str(p) for p in self.parts ])
    
check.register_class(python_version, include_seq = False)
