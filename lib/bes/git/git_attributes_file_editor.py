#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from .git_attributes_item import git_attributes_item
from .git_attributes_item import git_attributes_item_list

from .git_attributes_file_editor_options import git_attributes_file_editor_options
from .git_error import git_error

class git_attributes_file_editor(object):
  '''
  A class to edit a yaml file programatically

  '''
  def __init__(self, filename, options = None):
    check.check_string(filename)
    check.check_git_attributes_file_editor_options(options, allow_none = True)

    self._options = options or git_attributes_file_editor_options()
    self.filename = path.abspath(filename)
    if not path.isfile(self.filename):
      file_util.save(self.filename, content = '')
    self._items = seld._read_file_items(self.filename)
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)
    
    self._doc[key] = value
    result = self._save()
    assert path.isfile(self.filename)
    return result

  def has_value(self, key):
    return key in self._doc

  def get_value(self, key):
    check.check_string(key)
    
    self._check_file_exists()
    self._check_key(key)
    return self._doc[key]

  def get_value_with_default(self, key, default_value):
    check.check_string(key)
    
    self._check_file_exists()
    return self._doc.get(key, default_value)
  
  def remove_value(self, key):
    check.check_string(key)
    
    self._check_file_exists()
    self._check_key(key)
    del self._doc[key]
    return self._save()

  def keys(self):
    self._check_file_exists()
    return [ key for key in self._doc.keys() ]

  def values(self):
    self._check_file_exists()
    return [ value for value in self._doc.values() ]

  def items(self):
    self._check_file_exists()
    return [ item for item in self._doc.items() ]
  
  def _check_file_exists(self):
    if not path.exists(self.filename):
      raise git_error('yaml file not found: {}'.format(self.filename))
    if not path.isfile(self.filename):
      raise git_error('not a file: {}'.format(self.filename))

  def _check_key(self, key):
    if not self.has_value(key):
      raise KeyError('property \"{}\" not found in {}'.format(key, self.filename))

  @cached_property
  def _doc(self):
    doc = {}
    if self.filename:
      self._check_file_exists()
      with open(self.filename, 'r') as f:      
        doc = self._yaml.load(f) or {}
    return doc

  def _save(self):
    if path.exists(self.filename):
      old_checksum = file_util.checksum('sha256', self.filename)
    else:
      old_checksum = None
    tmp_file = temp_file.make_temp_file(suffix = '.yaml')
    with open(tmp_file, 'w') as o:
      self._yaml.dump(self._doc, o)
    new_checksum = file_util.checksum('sha256', tmp_file)
    if old_checksum == new_checksum:
      return False
    if self._options.backup and not file_util.is_empty(self.filename):
      file_util.backup(self.filename)
    file_util.copy(tmp_file, self.filename)
    return True

  @classmethod
  def _read_file_items(clazz, filename):
    content = file_util.read(filename, codec = 'utf-8')
    return git_attributes_item_list.parse(content)
