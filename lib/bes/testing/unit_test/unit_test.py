#!/usr/bin/env python
#-*- coding:utf-8 -*-

import codecs, inspect, os, os.path as path, platform, re, unittest
from bes.compat import StringIO
from io import BytesIO

from .hexdata import hexdata

class unit_test(unittest.TestCase):
  'Helper for writing unit tests.'
  
  def data_path(self, filename, platform_specific = False): 
    assert filename
    return path.join(self.data_dir(platform_specific = platform_specific), filename)

  def platform_data_path(self, filename): 
    return self.data_path(filename, platform_specific = True)

  def data_dir(self, platform_specific = False): 
    parts = [ self.__class__._get_data_dir() ]
    if platform_specific:
      parts.append(self._HOST)
    return path.join(*parts)

  def platform_data_dir(self): 
    return self.data_dir(platform_specific = True)

  def data(self, filename, platform_specific = False):
    data_path = self.data_path(filename, platform_specific = platform_specific)
    with open(data_path, 'rb') as fin:
      return fin.read()

  def assert_string_equal_ws(self, s1, s2):
    self.maxDiff = None
    s1 = re.sub('\s+', ' ', s1)
    s2 = re.sub('\s+', ' ', s2)
    self.assertEqual( s1, s2 )

  def assert_string_equal_strip(self, s1, s2):
    self.maxDiff = None
    self.assertEqual( s1.strip(), s2.strip() )

  def assert_file_content_equal(self, expected, filename, strip = True):
    self.maxDiff = None
    with open(filename, 'rb') as fin:
      content = fin.read()
      if strip:
        expected = expected.strip()
        content = content.strip()
    self.assertEqual( expected, content )
    
  @classmethod
  def _get_data_dir(clazz): 
    right = getattr(clazz, '__unit_test_data_dir__', None)
    if not right:
      raise RuntimeError('%s does not have a __unit_test_data_dir__ attribute.' % (clazz))
    left = path.dirname(inspect.getfile(clazz))
    return path.abspath(path.normpath(path.join(left, right)))

  def assert_bit_string_equal(self, b1, b2, size):
    bs1 = bin(b1)[2:].zfill(size)
    bs2 = bin(b2)[2:].zfill(size)
    self.assertEqual( bs1, bs2)

  def assert_bytes_equal(self, expected, actual):
    expected = hexdata.bytes_to_string(expected)
    actual = hexdata.bytes_to_string(actual)
    msg = '\nexpected: %s\n  actual: %s\n' % (expected, actual)
    self.assertEqual( expected, actual, msg = msg)

  @classmethod
  def decode_hex(clazz, s):
    return hexdata.string_to_bytes(s)
  
  @staticmethod
  def main(): 
    unittest.main()

  @classmethod
  def file_path(clazz, unit_test_filename, filename):
    'Return an absolute normalized path for a file relative to this unit test.'
    p = path.abspath(path.normpath(path.join(path.dirname(unit_test_filename), filename)))
    if not path.exists(p):
      raise RuntimeError('file not found: %s' % (p))
    if not os.access(p, os.X_OK):
      raise RuntimeError('file not executable: %s' % (p))
    return p

  def _host():
    s = platform.system()
    if s == 'Linux':
      return 'linux'
    elif s == 'Darwin':
      return 'macos'
    else:
      raise RuntimeError('Unknown system: %s' % (s))
    
  _HOST = _host()
