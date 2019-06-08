#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, copy, json, inspect, os, os.path as path, platform, pprint, re, sys, subprocess, tempfile, unittest
from bes.compat import StringIO
from io import BytesIO

from .hexdata import hexdata

class unit_test(unittest.TestCase):
  'Helper for writing unit tests.'

  def __init__(self, *args, **kargs):
    self.maxDiff = None
    super(unit_test, self).__init__(*args, **kargs)

  def _is_true(x):
    return x.lower() in [ 't', 'true', 'y', 'yes', '1' ]
    
  DEBUG = _is_true(os.environ.get('DEBUG', ''))
  BES_VERBOSE = _is_true(os.environ.get('BES_VERBOSE', ''))
  BES_DONET = _is_true(os.environ.get('BES_DONET', ''))
  
  _temp_dir = os.environ.get('BES_TEMP_DIR', None)
  if _temp_dir:
    if not path.isdir(_temp_dir):
      os.makedirs(_temp_dir)
    tempfile.tempdir = _temp_dir
  del _temp_dir
  
  def data_path(self, filename, platform_specific = False): 
    assert filename
    return path.join(self.data_dir(platform_specific = platform_specific), filename)

  def platform_data_path(self, filename): 
    return self.data_path(filename, platform_specific = True)

  def data_dir(self, platform_specific = False, where = None): 
    parts = [ self._get_data_dir() ]
    if platform_specific:
      parts.append(self._HOST)
    result = path.join(*parts)
    if where:
      return path.join(result, where)
    else:
      return result

  def platform_data_dir(self): 
    return self.data_dir(platform_specific = True)

  def data(self, filename, platform_specific = False):
    data_path = self.data_path(filename, platform_specific = platform_specific)
    with open(data_path, 'rb') as fin:
      return fin.read()

  def assertEqualIgnoreWhiteSpace(self, s1, s2):
    'Assert s1 equals s2 ignoreing minor white space differences.'
    self.maxDiff = None
    s1 = re.sub('\s+', ' ', s1).strip()
    s2 = re.sub('\s+', ' ', s2).strip()
    self.assertMultiLineEqual( s1, s2 )

  def assert_string_equal_strip(self, s1, s2):
    self.maxDiff = None
    self.assertEqual( s1.strip(), s2.strip() )

  def assert_dict_equal(self, d1, d2):
    self.assertMultiLineEqual( pprint.pformat(d1, indent = 2), pprint.pformat(d2, indent = 2) )

  def assert_dict_as_text_equal(self, d1, d2):
    self.assertMultiLineEqual( self._dict_to_str(d1), self._dict_to_str(d2) )

  @classmethod
  def _dict_to_str(clazz, d):
    return '\n'.join([ '%s=%s' % x for x in sorted(d.items()) ])

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
    right = clazz._substitute_test_data_dir(right)
    if path.isabs(right):
      return right
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
  def _json_normalize(clazz, s):
    return json.dumps(json.loads(s), indent = 2)
    
  def assert_json_equal(self, expected, actual):
    self.assertMultiLineEqual(self._json_normalize(expected),
                              self._json_normalize(actual))
                               

  @classmethod
  def decode_hex(clazz, s):
    return hexdata.string_to_bytes(s)
  
  @staticmethod
  def main(*args, **kargs):
    if unit_test.BES_VERBOSE:
      kargs = copy.deepcopy(kargs)
      kargs['verbosity'] = 2
    unittest.main(*args, **kargs)

  @classmethod
  def file_path(clazz, unit_test_filename, filename):
    'return an absolute normalized path for a file relative to this unit test.'
    filename = clazz._substitute_test_data_dir(filename)
    if path.isabs(filename):
      return filename
    
    p = path.abspath(path.normpath(path.join(path.dirname(unit_test_filename), filename)))
    if not path.exists(p):
      raise RuntimeError('file not found: %s' % (p))
    if not os.access(p, os.X_OK):
      raise RuntimeError('file not executable: %s' % (p))
    return p

  @classmethod
  def raise_skip(clazz, message):
    raise unittest.SkipTest(message)
  
  def _host():
    s = platform.system()
    if s == 'Linux':
      return 'linux'
    elif s == 'Darwin':
      return 'macos'
    elif s == 'Windows':
      return 'windows'
    else:
      raise RuntimeError('Unknown system: %s' % (s))
  _HOST = _host()

  @classmethod
  def _var_replace(clazz, s, var, replacement):
    return re.sub('\$\{%s\}' % (var), replacement, s)
      
  @classmethod
  def _substitute_test_data_dir(clazz, s):
    if not '$' in s:
      return s
    test_data_dir = os.environ.get('BES_TEST_DATA_DIR', None)
    if not test_data_dir:
      if path.isdir('tests/test_data'):
        test_data_dir = path.abspath('tests/test_data')
    if not test_data_dir:
      raise RuntimeError('BES_TEST_DATA_DIR not defined in environment and tests/test_data not found.')
    return clazz._var_replace(s, 'BES_TEST_DATA_DIR', test_data_dir)
      
  @classmethod
  def spew(clazz, s):
    sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()

  @classmethod
  def debug_spew_filename(clazz, label, f):
    if not clazz.DEBUG:
      return
    clazz.spew('%s: %s' % (label, f))
    
  @classmethod
  def dump(clazz, filename, text):
    with open(filename, 'w') as fout:
      fout.write(text)
      fout.close()

  @classmethod
  def spew_console(clazz, s):
    c = clazz._console()
    c.write(s)
    c.write('\n')
    c.flush()

  @classmethod
  def _console(clazz):
    if not hasattr(clazz, '_console_fp'):
      tty = subprocess.check_output('tty').strip()
      setattr(clazz, '_console_fp', open(tty, 'w'))
    return getattr(clazz, '_console_fp')
