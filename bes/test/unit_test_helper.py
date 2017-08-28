#!/usr/bin/env python
#-*- coding:utf-8 -*-

import inspect, os.path as path, re, unittest
from StringIO import StringIO
from bes.system import host

class unit_test_helper(unittest.TestCase):
  'Helper for writing unit tests.'
  
  def data_path(self, filename, platform_specific = False): 
    assert filename
    return path.join(self.data_dir(platform_specific = platform_specific), filename)

  def data_dir(self, platform_specific = False): 
    parts = [ self.__class__._get_data_dir() ]
    if platform_specific:
      parts.append(host.SYSTEM)
    return path.join(*parts)

  def data(self, filename, platform_specific = False):
    data_path = self.data_path(filename, platform_specific = platform_specific)
    with open(data_path, 'r') as fin:
      return fin.read()

  def assert_string_equal_no_whitespace(self, json1, json2):
    self.maxDiff = None
    json1 = re.sub('\s+', ' ', json1)
    json2 = re.sub('\s+', ' ', json2)
    self.assertEqual( json1, json2 )

  @classmethod
  def _get_data_dir(clazz): 
    right = getattr(clazz, '__unit_test_data_dir__', None)
    if not right:
      raise RuntimeError('%s does not have a __unit_test_data_dir__ attribute.' % (clazz))
    left = path.dirname(inspect.getfile(clazz))
    return path.join(left, right)

  def assert_bit_string_equal(self, b1, b2, size):
    bs1 = bin(b1)[2:].zfill(size)
    bs2 = bin(b2)[2:].zfill(size)
    self.assertEqual( bs1, bs2)

  def assert_bytes_equal(self, expected, actual):
    expected = self.bytes_to_string(expected)
    actual = self.bytes_to_string(actual)
    msg = '\nexpected: %s\n  actual: %s\n' % (expected, actual)
    self.assertEqual( expected, actual, msg = msg)

  @classmethod
  def bytes_to_string(clazz, b):
    s = b.encode('hex')
    assert (len(s) % 2) == 0
    buf = StringIO()
    for i in range(0, len(s), 2):
      if i != 0:
        buf.write(' ')
      buf.write(s[i])
      buf.write(s[i + 1])
    return buf.getvalue()

  @classmethod
  def decode_hex(clazz, s):
    buf = StringIO()
    for c in s:
      if not c.isspace():
        buf.write(c)
    return buf.getvalue().decode('hex')
  
  @staticmethod
  def main(): 
    unittest.main()
