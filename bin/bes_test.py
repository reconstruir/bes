#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

# A script to run python unit tests.  Does not use any bes code to avoid
# chicken-and-egg issues.
import argparse, ast, fnmatch, math, os, os.path as path, platform, random, re, subprocess, sys
import glob, shutil, tempfile
from collections import namedtuple

# TODO:
#  - figure out how to stop on first failure within one module
#  - https://stackoverflow.com/questions/6813837/stop-testsuite-if-a-testcase-find-an-error

#class bes_test_command_line(object):
#
#  def __init__(self):
#    pass

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('files', action = 'store', nargs = '*', help = 'Files or directories to rename')
  parser.add_argument('--unit',
                      '-u',
                      action = 'store_true',
                      default = False,
                      help = 'Just run unit tests [ False ]')
  parser.add_argument('--dry-run',
                      '-n',
                      action = 'store_true',
                      default = False,
                      help = 'Only print what files will get tests [ False ]')
  parser.add_argument('--verbose',
                      '-v',
                      action = 'store_true',
                      default = False,
                      help = 'Verbose debug spew [ False ]')
  parser.add_argument('--stop',
                      '-s',
                      action = 'store_true',
                      default = False,
                      help = 'Stop right after the first failure. [ False ]')
  parser.add_argument('--randomize',
                      '-r',
                      action = 'store_true',
                      default = False,
                      help = 'Randomize the order in which unit tests run. [ False ]')
  parser.add_argument('--python',
                      '-p',
                      action = 'store',
                      default = 'python',
                      help = 'Python executable to use [ python ]')
  parser.add_argument('--git',
                      '-g',
                      action = 'store_true',
                      default = False,
                      help = 'Use git status to figure out what has changed to test [ False ]')
  parser.add_argument('--dump',
                      '-d',
                      action = 'store_true',
                      default = False,
                      help = 'Dump the list of unit tests [ False ]')
  parser.add_argument('--egg',
                      action = 'store_true',
                      default = False,
                      help = 'Make an egg of the package and run the tests against that instead the live files. [ False ]')
  args = parser.parse_args()

  files, filters = _separate_files_and_filters(args.files)
  print "files: ", files

  files = _resolve_files(files)
  print "resolved files: ", files
  
  if args.git:
    assert False
    git_roots = git.roots_for_many_files(files)
    git_modified = []
    for root in git_roots:
      git_modified.extend(_git_modified_python_files(root))
    sgit = set(git_modified)
    sfiles = set(files)
    inter = sgit & sfiles
    print "files: ", files
    print "git_modified: ", git_modified
    print "inter: ", inter
    assert False
    
#  files = _determine_tests_for_files(files)
#  print "determined files: ", files
#  assert False
  files = sorted(_unique_list(files))

  if args.randomize:
    random.shuffle(files)

  available_unit_tests = _available_unit_tests(files)

  if args.dump:
    _dump_available_unit_tests(available_unit_tests)
    return 0
  
  patterns = _make_filters_patterns(filters)

  filename_patterns = [ p.filename for p in patterns if p.filename ]
  if filename_patterns:
    files = _match_filenames(files, filename_patterns)

  files = [ path.abspath(f) for f in files ] 

  filtered_files = _filter_files(files, available_unit_tests, patterns)

  num_passed = 0
  num_failed = 0
  num_executed = 0
  num_tests = len(filtered_files)
  failed_tests = []

  cwd = os.getcwd()

  # Remove current dir from sys.path to avoid side effects
  if cwd in sys.path:
    sys.path.remove(cwd)
  
  if args.egg:
    setup_dot_py = path.join(cwd, 'setup.py')
    if not path.isfile(setup_dot_py):
      raise RuntimeError('No setup.py found in %s to make the egg.' % (cwd))
    egg = egg_util.make(setup_dot_py)
    environ_util.pythonpath_remove(cwd)
    environ_util.pythonpath_prepend(egg)
    
  os.chdir('/tmp')
  for i, f in enumerate(filtered_files):
    success = _python_call(args.python, f.filename, f.tests, args.dry_run, args.verbose,
                           args.stop, i + 1, len(filtered_files), cwd)
    num_executed += 1
    if success:
      num_passed += 1
    else:
      num_failed += 1
      failed_tests.append(f)

    if args.stop and not success:
      break
  if args.dry_run:
    return 0
  num_skipped = num_tests - num_executed
  summary_parts = []
  if num_failed > 0:
    summary_parts.append('%d of %d FAILED' % (num_failed, num_tests))
  summary_parts.append('%d of %d passed' % (num_passed, num_tests))
  if num_skipped > 0:
    summary_parts.append('%d of %d skipped' % (num_skipped, num_tests))

  summary = '; '.join(summary_parts)
  print 'bes_test.py: %s' % (summary)
  if failed_tests:
    for f in failed_tests:
      print 'bes_test.py: FAILED: %s' % (file_util.remove_head(f.filename, cwd))
  
  if num_failed > 0:
    return 1
  return 0

def _resolve_files(files):
  result = []
  for f in files:
    if path.isfile(f):
      result.append(path.abspath(path.normpath(f)))
    elif path.isdir(f):
      result += file_finder.find_tests(f)
  result = _unique_list(result)
  more_tests = []
  for r in result:
    more_tests.extend(_tests_for_file(r))
  result.extend(more_tests)
  result = [ r for r in result if _file_has_tests(r) ]
  result = [ path.normpath(r) for r in result ]
  return sorted(result)

def _determine_tests_for_files(files):
  result = []
  for filename in files:
    result.extend(_tests_for_file(filename))
  result = [ r for r in result if _file_has_tests(r) ]
  result = [ path.normpath(r) for r in result ]
  return sorted(result)

file_and_tests = namedtuple('file_and_tests', 'filename,tests')
def _filter_files(files, available, patterns):
  if not patterns:
    return [ file_and_tests(filename, None) for filename in files ]
  result = []
  for filename in files:
    assert filename in available
    available_for_filename = available[filename]
    matching_tests = _matching_tests(available_for_filename, patterns)
    if matching_tests:
      result.append(file_and_tests(filename, matching_tests))
  return result
    
def _tests_for_file(filename):
  basename = path.basename(filename)
  dirname = path.dirname(filename)
  name = path.splitext(basename)[0]
  test_filename = 'test_%s.py' % (name)
  test_full_path = path.join(dirname, 'tests', test_filename)
  if path.exists(test_full_path):
    return [ test_full_path ]
  return []

def _file_has_tests(filename):
  'FIXME ust ast for this.'
  content = file_util.read(filename)
  if content.find('unittest.TestCase') >= 0:
    return True
  if content.find('unit_test_helper') >= 0:
    return True
  return False

unit_test_desc = namedtuple('unit_test_desc', 'filename,fixture,function')
def _available_unit_tests(filenames):
  available = {}
  for filename in filenames:
    available[filename] = []
              
  for filename in filenames:
    code = file_util.read(filename)
    tree = ast.parse(code)
    for node in tree.body:
      if isinstance(node, ast.ClassDef):
        for statement in node.body:
          if isinstance(statement, ast.FunctionDef):
            available[filename].append(unit_test_desc(filename, node.name, statement.name))
  return available

def _dump_available_unit_tests(available):
  for filename in sorted(available.keys()):
    for _, fixture, function in available[filename]:
      print '%s:%s.%s' % (filename, fixture, function)

def _filepath_normalize(filepath):
  f = path.abspath(path.normpath(filepath))
  if path.exists(f):
    return f
  return None

def _filepaths_normalize(files):
  return [ _filepath_normalize(f) for f in files ]

def _which(exe):
  cmd = [ 'which', exe ]
  try:
    return subprocess.check_output(cmd, shell = False).strip()
  except:
    return None

def _matching_tests(available, patterns):
  result = []
  for test in available:
    for pattern in patterns:
      fixture_matches = True
      if pattern.fixture:
        fixture_matches = fnmatch.fnmatch(test.fixture.lower(), pattern.fixture.lower())
      function_matches = True
      if pattern.function:
        function_matches = fnmatch.fnmatch(test.function.lower(), pattern.function.lower())
      if fixture_matches and function_matches:
        result.append(test)
  return result

def _python_call(python, filename, tests, dry_run, verbose,
                 stop_on_failure, index, total, cwd):
  remove_head = file_util.remove_head(filename, cwd)
  cmd = [ python, '-B', filename ]

  if tests:
    cmd.extend([ '%s.%s' % (test.fixture, test.function) for test in tests ])
  
  try:
#    if stop:
#      cmd.append('--stop')
    if total > 1:
      count_blurb = ' ' + _make_count_blurb(index, total)
    else:
      count_blurb = ''

    if dry_run:
      label = 'dry-run'
    else:
      label = 'testing'

    print('bes_test.py:%7s:%s %s' % (label, count_blurb, remove_head))

    if dry_run:
      return True

    stdout_pipe = subprocess.PIPE
    if not verbose:
      stderr_pipe = subprocess.PIPE
    else:
      stderr_pipe = subprocess.STDOUT

    env = _make_clean_env()
    env['PYTHONDONTWRITEBYTECODE'] = 'x'
    process = subprocess.Popen(' '.join(cmd),
                               stdout = stdout_pipe,
                               stderr = stderr_pipe,
                               shell = True,
                               env = env)
    output = process.communicate()
    exit_code = process.wait()

    stdout_output = output[0]
    stderr_output = output[1]
    success = exit_code == 0
    spew_output = not success or verbose
    if success:
      label = 'passed'
    else:
      label = 'FAILED'
    if spew_output:
      print 'bes_test.py: %7s: %s' % (label, remove_head)
      sys.stdout.write(stdout_output)
      if not success:
        sys.stdout.write(stderr_output)
      sys.stdout.flush()
    return success
  except Exception, ex:
    print 'bes_test.py: Caught exception on %s: %s' % (filename, str(ex))
    return False

def _match_test(patterns, filename):
  filename = filename.lower()
  for pattern in patterns:
    if fnmatch.fnmatch(s, pattern.lower()):
      return True
  return False

def _search_for_tests(search_patterns, where):
  result = []
  possible_tests = file_finder.find_tests(where)
  for filename in possible_tests:
    if _match_test(search_patterns, filename):
      result.append(filename)
  return sorted(_unique_list(result))

def _is_fnmatch_pattern(pattern):
  for c in [ '*', '?', '[', ']', '!' ]:
    if pattern.count(c) > 0:
      return True
  return False

def _make_fnmatch_pattern(pattern):
  pattern = pattern.lower()
  if _is_fnmatch_pattern(pattern):
    return pattern
  return '*%s*' % (pattern)

def _unique_list(l):
  return list(set(l))

def _make_clean_env():
  'Return a clean environment suitable for deterministic build related tasks.'
  clean_path = '/bin:/usr/bin:/usr/sbin:/sbin'
  clean_vars = [ 'BES_LOG', 'PYTHONPATH', 'DISPLAY', 'HOME', 'LANG', 'SHELL', 'TERM', 'TERM_PROGRAM', 'TMOUT', 'TMPDIR', 'USER', 'XAUTHORITY', '__CF_USER_TEXT_ENCODING' ]
  clean_env = {}
  for k, v in os.environ.items():
    if k in clean_vars:
      clean_env[k] = v
  clean_env['PATH'] = clean_path
  return clean_env

def _make_count_blurb(index, total):
  length = int(math.log10(total)) + 1
  index = str(index)
  count = str(total)
  index_blurb = (' ' * (length - len(index))) + index
  count_blurb = (' ' * (length - len(count))) + count
  return '[%s of %s]' % (index_blurb, count_blurb)

def _parse_unit_test_desc(s):
  'Parse a unit test description in the form filename:fixutre.function'
  filename, _, right = s.partition(':')
  if '.' in right:
    fixture, _, function = right.partition('.')
  else:
    fixture, function = ( None, right )
  return unit_test_desc(filename, fixture or None, function or None)

files_and_filters = namedtuple('files_and_filters', 'files,filters')
def _separate_files_and_filters(args):
  files = []
  filter_descriptions = []
  for f in args:
    normalized_path = _filepath_normalize(f)
    if not normalized_path:
      filter_descriptions.append(f)
    else:
      files.append(f)
  filters = [ _parse_unit_test_desc(f) for f in (filter_descriptions or []) ]
  return files_and_filters(files, filters)

def _make_filters_patterns(filters):
  patterns = []
  for f in filters:
    filename_pattern = None
    fixture_pattern = None
    function_pattern = None
    if f.filename:
      filename_pattern = _make_fnmatch_pattern(f.filename)
    if f.fixture:
      fixture_pattern = _make_fnmatch_pattern(f.fixture)
    if f.function:
      function_pattern = _make_fnmatch_pattern(f.function)
    patterns.append(unit_test_desc(filename_pattern, fixture_pattern, function_pattern))
  return patterns

def _match_filenames(files, patterns):
  result = []
  for filename in files:
    if _match_test(patterns, filename):
      result.append(filename)
  return sorted(_unique_list(result))

class util(object):

  @classmethod
  def unique_list(clazz, l):
    return list(set(l))

class file_util(object):

  @classmethod
  def read(clazz, filename):
    with open(filename, 'r') as fin:
      return fin.read()

  @classmethod
  def remove_head(clazz, filename, head):
    head = path.normpath(head) + os.sep
    if filename.startswith(head):
      return filename[len(head):]
    return filename

class environ_util(object):

  @classmethod
  def pythonpath_get(clazz):
    return os.environ.get('PYTHONPATH', '').split(':')
  
  @classmethod
  def pythonpath_set(clazz, pythonpath):
    assert isinstance(pythonpath, list)
    os.environ['PYTHONPATH'] = ':'.join(pythonpath)

  @classmethod
  def pythonpath_remove(clazz, what):
    pythonpath = clazz.pythonpath_get()
    if what in pythonpath:
      pythonpath.remove(what)
    clazz.pythonpath_set(pythonpath)
    
  @classmethod
  def pythonpath_prepend(clazz, what):
    pythonpath = clazz.pythonpath_get()
    pythonpath.insert(0, what)
    clazz.pythonpath_set(pythonpath)
    
class string_util(object):

  @classmethod
  def parse_list(clazz, s):
    return [ x.strip() for x in s.strip().split('\n') if x.strip() ]
  
class file_finder(object):

  @classmethod
  def find_python_files(clazz, d):
    cmd = [ 'find', d, '-name', '*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return string_util.parse_list(result)

  @classmethod
  def find_tests(clazz, d):
    cmd = [ 'find', d, '-name', 'test_*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return string_util.parse_list(result)
  
class git(object):

  status_item = namedtuple('status_item', 'modifier,filename')

  @classmethod
  def parse_status_line(clazz, root, line):
    line = line.strip()
    v = re.findall('\s*(\w+)\s+(.*)', line)
    if len(v) != 1:
      return None
    assert len(v[0]) == 2
    modifier = v[0][0]
    filename = v[0][1]
    return clazz.status_item(modifier, path.join(root, filename))

  @classmethod
  def parse_status(clazz, root, text):
    lines = string_util.parse_list(text)
    return [ clazz.parse_status_line(root, line) for line in lines ]

  @classmethod
  def status(clazz, root):
    cmd = [ 'git', 'st', '--porcelain', '.' ]
    result = subprocess.check_output(cmd, shell = False, cwd = root)
    items = clazz.parse_status(root, text)
    assert None not in items
    return items

  @classmethod
  def modified_files(clazz, root):
    items = clazz.status(root)
    return [ item.filename for item in items if 'M' in item.modifier ]

  @classmethod
  def modified_python_files(clazz, root):
    return [ f for f in clazz.modified_files(root) if f.endswith('.py') ]

  @classmethod
  def root(clazz, filename):
    'Return the repo root for the given filename or raise and exception if not under git control.'
    cmd = [ 'git', 'rev-parse', '--show-toplevel' ]
    result = subprocess.check_output(cmd, shell = False, cwd = path.dirname(filename))
    lines = string_util.parse_list(result)
    assert len(lines) == 1
    return lines[0]

  @classmethod
  def roots_for_many_files(clazz, files):
    return util.unique_list([ clazz.root(filename) for filename in files ])


class egg_util(object):

  @classmethod
  def make(clazz, setup_dot_py):
    assert path.isfile(setup_dot_py)
    temp_dir = tempfile.mkdtemp()
    src_dir = path.dirname(setup_dot_py)
    shutil.rmtree(temp_dir)
    shutil.copytree(src_dir, temp_dir, symlinks = True)
    cmd = [ 'python', 'setup.py', 'bdist_egg' ]
    subprocess.check_output(cmd, shell = False, cwd = temp_dir)
    eggs = glob.glob('%s/dist/*.egg' % (temp_dir))
    assert len(eggs) == 1
    return eggs[0]
  
import unittest

class test_case(unittest.TestCase):
  
  def foo(self): 
    assert False

class test_bes_test_caca(test_case):

  def test_parse_unit_test_desc(self):
    self.assertEqual( ( 'foo.py', 'fix', 'func' ), _parse_unit_test_desc('foo.py:fix.func') )
    self.assertEqual( ( 'foo.py', None, None ), _parse_unit_test_desc('foo.py') )
    self.assertEqual( ( 'foo.py', None, None ), _parse_unit_test_desc('foo.py:') )
    self.assertEqual( ( 'foo.py', None, 'fix' ), _parse_unit_test_desc('foo.py:fix') )

class test_string_util(test_case):
  def test_parse_list(self):
    self.assertEqual( [ 'foo', 'bar' ], string_util.parse_list('foo\nbar\n') )
    self.assertEqual( [ 'foo', 'bar' ], string_util.parse_list('foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], string_util.parse_list('\nfoo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], string_util.parse_list('\n foo\nbar') )
    self.assertEqual( [ 'foo', 'bar' ], string_util.parse_list('\n foo\nbar ') )
    self.assertEqual( [ 'foo', 'bar' ], string_util.parse_list('\n foo\nbar \n') )
    self.assertEqual( [], string_util.parse_list('\n\n\n') )

class test_file_util(test_case):

  def test_remove_head(self):
    self.assertEqual( 'foo/bar/foo.py', file_util.remove_head('/root/x/y/foo/bar/foo.py', '/root/x/y') )
    self.assertEqual( 'foo/bar/foo.py', file_util.remove_head('/root/x/y/foo/bar/foo.py', '/root/x/y/') )
    self.assertEqual( 'foo/bar/foo.py', file_util.remove_head('root/x/y/foo/bar/foo.py', 'root/x/y') )
    self.assertEqual( 'foo/bar/foo.py', file_util.remove_head('root/x/y/foo/bar/foo.py', 'root/x/y/') )

class test_git(test_case):

  def test_parse_status_line(self):
    self.assertEqual( ('M', '/root/foo/bar/__init__.py'), git.parse_status_line('/root', ' M foo/bar/__init__.py') )
    self.assertEqual( ('A', '/root/foo/bar/apple.py'), git.parse_status_line('/root', 'A  foo/bar/apple.py') )
    self.assertEqual( ('D', '/root/foo/bar/orange.py'), git.parse_status_line('/root', ' D foo/bar/orange.py') )

  def test_parse_status(self):
    text = '''
 M foo/bar/__init__.py
A  foo/bar/apple.py
 D foo/bar/orange.py
A  foo/bar/tests/test_apple.py
 D foo/bar/tests/test_orange.py
 M foo/bar/pear.py
 M bin/kiwi.py
'''
    self.assertEqual( [
      ( 'M', '/root/foo/bar/__init__.py' ),
      ( 'A', '/root/foo/bar/apple.py' ),
      ( 'D', '/root/foo/bar/orange.py' ),
      ( 'A', '/root/foo/bar/tests/test_apple.py' ),
      ( 'D', '/root/foo/bar/tests/test_orange.py' ),
      ( 'M', '/root/foo/bar/pear.py' ),
      ( 'M', '/root/bin/kiwi.py' ),
    ],
                      git.parse_status('/root', text) )
    
if len(sys.argv) >= 2 and sys.argv[1] in [ '--unit' ]:
  sys.argv = sys.argv[0:1]
  unittest.main()

if __name__ == '__main__':
  raise SystemExit(main())

    
