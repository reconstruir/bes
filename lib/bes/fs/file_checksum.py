#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path, hashlib
from collections import namedtuple
from ..system.check import check
from bes.common.json_util import json_util
from bes.common.object_util import object_util
from bes.common.type_checked_list import type_checked_list
from bes.compat.StringIO import StringIO
from .file_check import file_check
from .file_util import file_util
from .file_checksum_getter_raw import file_checksum_getter_raw

class file_checksum(namedtuple('file_checksum', 'filename, checksum')):

  _DEFAULT_GETTER = file_checksum_getter_raw()
  
  def __new__(clazz, filename, checksum):
    check.check_string(filename)
    check.check_string(checksum)
    return clazz.__bases__[0].__new__(clazz, filename, checksum)

  @classmethod
  def from_file(clazz, filename, root_dir = None, function_name = None, getter = None):
    check.check_file_checksum_getter(getter, allow_none = True)
    function_name = function_name or 'sha256'
    getter = getter or clazz._DEFAULT_GETTER
    if root_dir:
      filepath = path.join(root_dir, filename)
    else:
      filepath = filename
    if path.islink(filepath):
      checksum = ''
    else:
      file_check.check_file(filepath)
      checksum = getter.checksum(function_name, filepath)
    return clazz(filename, checksum)

  def to_list(self):
    return [ self.filename, self.checksum ]
  
class file_checksum_list(type_checked_list):

  __value_type__ = file_checksum
  
  def __init__(self, values = None):
    super(file_checksum_list, self).__init__(values = values)

  @classmethod
  def cast_value(clazz, entry):
    if isinstance(entry, ( tuple, list )):
      return file_checksum(*entry)
    return entry
    
  def to_json(self):
    return json_util.to_json(self._values, indent = 2)
    
  def to_simple_list(self):
    return [ x.to_list() for x in self ]
    
  @classmethod
  def from_json(clazz, text):
    o = json.loads(text)
    check.check_list(o)
    return clazz.from_simple_list(o)
    
  @classmethod
  def from_simple_list(clazz, l):
    check.check_list(l)
    result = clazz()
    for item in l:
      check.check_list(item, check.STRING_TYPES)
      assert len(item) == 2
      result.append(file_checksum(item[0], item[1]))
    return result
    
  @classmethod
  def from_files(clazz, filenames, root_dir = None, function_name = None, getter = None):
    filenames = object_util.listify(filenames)
    result = clazz()
    for filename in filenames:
      result.append(file_checksum.from_file(filename,
                                            root_dir = root_dir,
                                            function_name = function_name,
                                            getter = getter))
    return result

  def save_checksums_file(self, filename):
    file_util.save(filename, content = self.to_json(), codec = 'utf8')

  @classmethod
  def load_checksums_file(clazz, filename):
    try:
      content = file_util.read(filename)
    except IOError as ex:
      return None
    return clazz.from_json(content)
  
  def filenames(self):
    return [ c.filename for c in self ]

  def reload(self, root_dir = None, function_name = None, getter = None):
    new_values = []
    for value in self:
      new_values.append(file_checksum.from_file(value.filename,
                                                root_dir = root_dir,
                                                function_name = function_name,
                                                getter = getter))
    self._values = new_values
  
  def verify(self, root_dir = None, getter = None):
    current = self[:]
    current.reload(root_dir = root_dir, getter = getter)
    return self == current

  def has_filename(self, filename):
    current = self[:]
    current.reload(root_dir = root_dir)
    return self == current

  def has_filename(self, filename):
    current = self[:]
    current.reload(root_dir = root_dir)
    return self == current

  def checksum(self):
    'Return a checksum of the files and file checksums themselves.'
    buf = StringIO()
    for value in self:
      buf.write(value.filename)
      buf.write(value.checksum)
    return hashlib.sha256(buf.getvalue().encode('utf-8')).hexdigest()

  def to_dict(self):
    'Return a dictionary of filenames to checksums.'
    result = {}
    for value in self:
      result[value.filename] = value.checksum
    return result

check.register_class(file_checksum, include_seq = False)
check.register_class(file_checksum_list, include_seq = False)
