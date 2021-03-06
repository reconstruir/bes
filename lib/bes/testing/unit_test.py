#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import atexit, codecs, copy, difflib, json, inspect, os, os.path as path
import platform, pprint, re, sys, shutil, subprocess, tempfile, time, unittest
from datetime import datetime

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

  def data(self, filename, platform_specific = False, codec = 'utf-8', xp_new_lines = False):
    data_path = self.data_path(filename, platform_specific = platform_specific)
    with open(data_path, 'rb') as fin:
      data = fin.read()
      if codec:
        data = data.decode(codec)
      if xp_new_lines:
        data = self.xp_new_lines(data)
      return data
    
  def assertEqualIgnoreWhiteSpace(self, s1, s2):
    'Assert s1 equals s2 ignoreing minor white space differences.'
    self.maxDiff = None
    s1_stripped = re.sub(r'\s+', ' ', s1).strip()
    s2_stripped = re.sub(r'\s+', ' ', s2).strip()
    if s1_stripped == s2_stripped:
      return
    self.assertMultiLineEqual( s1, s2 )

  def assert_string_equal_strip(self, s1, s2, xp_new_lines = False):
    self.maxDiff = None

    s1_stripped = s1.strip()
    s2_stripped = s2.strip()

    if xp_new_lines:
      s1_stripped = self.xp_new_lines(s1_stripped)
      s2_stripped = self.xp_new_lines(s2_stripped)
    
    if s1_stripped == s2_stripped:
      return
    
    if xp_new_lines:
      self.assertMultiLineEqual( self.xp_new_lines(s1_stripped), self.xp_new_lines(s2_stripped) )
    else:
      self.assertMultiLineEqual( s1, s2 )

  def assert_dict_equal(self, d1, d2):
    self.assertMultiLineEqual( pprint.pformat(d1, indent = 2), pprint.pformat(d2, indent = 2) )

  def assert_dict_as_text_equal(self, d1, d2):
    self.assertMultiLineEqual( self._dict_to_str(d1), self._dict_to_str(d2) )

  @classmethod
  def _dict_to_str(clazz, d):
    return '\n'.join([ '%s=%s' % x for x in sorted(d.items()) ])

  def assert_binary_file_equal(self, expected, filename):
    self.maxDiff = None
    with open(filename, 'rb') as fin:
      actual = fin.read()
      self.assertEqual( expected, actual )

  def assert_text_file_equal(self, expected, filename, strip = True, codec = 'utf-8',
                             preprocess_func = None, xp_new_lines = False):
    self.maxDiff = None
    with open(filename, 'rb') as fin:
      actual = fin.read().decode(codec)
      if xp_new_lines:
        actual = self.xp_new_lines(actual)
      
      if preprocess_func:
        actual = preprocess_func(actual)
        expected = preprocess_func(expected)
      if strip:
        actual = actual.strip()
        expected = expected.strip()
      self.assertMultiLineEqual( expected, actual )

  def assert_json_file_equal(self, expected, filename):
    self.assert_text_file_equal(expected, filename,
                                strip = True,
                                codec = 'utf-8',
                                preprocess_func = self._json_normalize)

  @classmethod
  def _get_data_dir(clazz): 
    right = getattr(clazz, '__unit_test_data_dir__', None)
    if not right:
      raise RuntimeError('%s does not have a __unit_test_data_dir__ attribute.' % (clazz))
    right = clazz.xp_path(right)
    right = clazz._substitute_test_data_dir(right)
    if path.isabs(right):
      result = path.join(right)
      return result
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
  def file_path(clazz, unit_test_filename, filename, check_executable = True):
    'return an absolute normalized path for a file relative to this unit test.'
    filename = clazz._substitute_test_data_dir(filename)
    if path.isabs(filename):
      return filename
    
    p = path.abspath(path.normpath(path.join(path.dirname(unit_test_filename), filename)))
    if not path.exists(p):
      raise RuntimeError('file not found: %s' % (p))
    if check_executable and not os.access(p, os.X_OK):
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
    pattern = r'${{{}}}'.format(var)
    return s.replace(pattern, replacement)
  
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

  @classmethod
  def xp_path(clazz, s, pathsep = ':', sep = '/'):
    result = s.replace(pathsep, os.pathsep)
    result = result.replace(sep, os.sep)
    return result

  @classmethod
  def xp_path_list(clazz, l, pathsep = ':', sep = '/'):
    if l == None:
      return Noneb
    assert isinstance(l, list)
    return [ clazz.xp_path(n) for n in l ]
  
  @classmethod
  def xp_new_lines(clazz, s, ending = '\n'):
    result = s.replace('\n\r', ending)
    result = result.replace('\r\n', ending)
    return result

  @classmethod
  def p(clazz, s, pathsep = ':', sep = '/'):
    return clazz.xp_path(s, pathsep = pathsep, sep = sep)

  
  _DEFAULT_PREFIX = path.splitext(path.basename(sys.argv[0]))[0] + '-tmp-'

  @classmethod
  def make_temp_file(clazz, content = None, prefix = None, suffix = None, dir = None, mode = 'w+b', perm = None, mtime = None, delete = True):
    'Write content to a temporary file.  Returns the file object.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or ''
    if dir and not path.isdir(dir):
      clazz.mkdir(dir)
    tmp = tempfile.NamedTemporaryFile(prefix = prefix,
                                      suffix = suffix,
                                      dir = dir,
                                      mode = mode,
                                      delete = False)
    if content:
      if not isinstance(content, bytes):
        content = content.encode('utf-8')
      tmp.write(content)
    tmp.flush()
    if perm:
      os.chmod(tmp.name, perm)
    os.fsync(tmp.fileno())
    if clazz.DEBUG:
      print('temp_file: {}'.format(tmp.name))
    else:
      clazz._atexit_delete(tmp.name)
    tmp.close()
    if mtime:
      assert isinstance(mtime, datetime)
      clazz._set_mtime(tmp.name, mtime)
    return tmp.name

  @classmethod
  def make_temp_dir(clazz, prefix = None, suffix = None, dir = None, mtime = None):
    'Make a temporary directory.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or '.dir'
    if dir and not path.isdir(dir):
      clazz.mkdir(dir)
    tmp_dir = tempfile.mkdtemp(prefix = prefix, suffix = suffix, dir = dir)
    assert path.isdir(tmp_dir)
    if clazz.DEBUG:
      print('temp_dir: {}'.format(tmp_dir))
    else:
      clazz._atexit_delete(tmp_dir)
    if mtime:
      assert isinstance(mtime, datetime)
      clazz._set_mtime(tmp_dir, mtime)
    return tmp_dir

  @classmethod
  def make_named_temp_file(clazz, filename, content = None, delete = True, perm = None):
    'Write a named temporary file to an also temporary directory.'
    tmp_dir = clazz.make_temp_dir()
    tmp_file = path.join(tmp_dir, filename)
    if content:
      with open(tmp_file, 'wb') as fout:
        if not isinstance(content, bytes):
          content = content.encode('utf-8')
        fout.write(content)
        fout.flush()
        os.fsync(fout.fileno())
    return tmp_file  
  
  @classmethod
  def _set_mtime(clazz, filename, mtime):
    mktime = time.mktime(mtime.timetuple())
    os.utime(filename, ( mktime, mktime ))
  
  @classmethod
  def _atexit_delete(clazz, filename):
    'Delete filename atexit time.'
    def _delete_file(*args, **kargs):
      filename = args[0]
      clazz.remove(filename)
    atexit.register(_delete_file, [ filename ])
  
  @classmethod
  def mkdir(clazz, p, mode = None):
    if path.isdir(p):
      return
    os.makedirs(p)
    if mode:
      os.chmod(p, mode)

  @classmethod
  def remove(clazz, files):
    if not isinstance(files, list):
      files = [ files ]
    assert isinstance(files, list)
    for f in files:
      try:
        if path.isdir(f):
          shutil.rmtree(f)
        else:
          os.remove(f)
      except Exception as ex:
        pass

  @classmethod
  def resolve_data_dir(clazz, module_file, *parts):
    if not path.isabs(module_file):
      raise RuntimeError('module_file needs to be an absolute path to a python module file.')
    if not parts:
      raise RuntimeError('parts needs to be a non empty list of program parts for path.join()')
    return path.normpath(path.abspath(path.join(path.dirname(module_file), *parts)))

  @classmethod
  def diff_two_files(clazz, filename1, filename2, label1 = 'one', label2 = 'two', n = 1):
    'Return the equivalent off diff -u -n 1 filename1 filename2 suitable for unit tests'
    with open(filename1, 'rb') as fin1:
      content1 = fin1.read().decode('utf-8')
      lines1 = content1.splitlines(True)

      with open(filename2, 'rb') as fin2:
        content2 = fin2.read().decode('utf-8')
        lines2 = content2.splitlines(True)
      
        diff_rv = difflib.unified_diff(lines1, lines2, fromfile = label1, tofile = label2, n = n)
        return ''.join(diff_rv)
