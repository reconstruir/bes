#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json, os.path as path, hashlib
from collections import namedtuple
from bes.common import json_util, object_util
from .file_util import file_util

class file_checksum(object):

  Item = namedtuple('Item', 'filename,checksum')

  @classmethod
  def checksum(clazz, filename):
    content = file_util.read(filename)
    checksum = hashlib.sha1(content).hexdigest()
    return clazz.Item(filename, checksum)

  @classmethod
  def checksums(clazz, filenames):
    results = []
    filenames = object_util.listify(filenames)
    for filename in filenames:
      results.append(clazz.checksum(filename))
    return results

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
    result = []
    for item in o:
      assert isinstance(item, list)
      assert len(item) == 2
      result.append(clazz.Item(str(item[0]), str(item[1])))
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
