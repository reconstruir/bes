#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json, os.path as path, hashlib
from collections import namedtuple
from bes.common import check, json_util, object_util, type_checked_list
from .file_check import file_check
from .file_util import file_util

class new_file_checksum(namedtuple('new_file_checksum', 'filename,checksum')):

  def __new__(clazz, filename, checksum):
    check.check_string(filename)
    check.check_string(checksum)
    return clazz.__bases__[0].__new__(clazz, filename, checksum)

  @classmethod
  def from_file(clazz, filename, root_dir = None):
    if root_dir:
      filepath = path.join(root_dir, filename)
    else:
      filepath = filename
    file_check.check_file(filepath)
    content = file_util.read(filepath)
    checksum = hashlib.sha1(content).hexdigest()
    return clazz(filename, checksum)

class file_checksum_list(type_checked_list):

  def __init__(self, values = None):
    super(file_checksum_list, self).__init__(new_file_checksum, values = values)

  def to_json(self):
    return json.dumps(self._values, indent = 2)
    
  @classmethod
  def from_json(clazz, text):
    o = json.loads(text)
    check.check_list(o)
    result = clazz()
    for item in o:
      check.check_list(item, check.STRING_TYPES)
      assert len(item) == 2
      result.append(new_file_checksum(item[0], item[1]))
    return result
    
  @classmethod
  def from_files(clazz, filenames, root_dir = None):
    filenames = object_util.listify(filenames)
    result = clazz()
    for filename in filenames:
      result.append(new_file_checksum.from_file(filename, root_dir = root_dir))
    return result
  
checksum_item = namedtuple('checksum_item', 'filename,checksum')

class file_checksum(object):

  @classmethod
  def checksum(clazz, filename, root_dir = None):
    if root_dir:
      f = path.join(root_dir, filename)
    else:
      f = filename
    content = file_util.read(f)
    checksum = hashlib.sha1(content).hexdigest()
    return checksum_item(filename, checksum)

  @classmethod
  def checksums(clazz, filenames, root_dir = None):
    result = checksum_item_list()
    filenames = object_util.listify(filenames)
    for filename in filenames:
      result.append(clazz.checksum(filename))
    return result

  @classmethod
  def save_checksums(clazz, filename, checksums):
    content = json_util.to_json(checksums, indent = 2)
    file_util.save(filename, content = content)

  @classmethod
  def load_checksums(clazz, filename):
    try:
      content = file_util.read(filename)
    except IOError as ex:
      return None
    o = json.loads(content)
    assert isinstance(o, list)
    result = checksum_item_list()
    for item in o:
      assert isinstance(item, list)
      assert len(item) == 2
      result.append(checksum_item(str(item[0]), str(item[1])))
    return result

  @classmethod
  def verify(clazz, checksums):
    checksums = object_util.listify(checksums)
    for checksum in checksums:
      if checksum != clazz.checksum(checksum.filename):
        return False
    return True

  @classmethod
  def filenames(clazz, checksums):
    return [ checksum.filename for checksum in checksums ]
