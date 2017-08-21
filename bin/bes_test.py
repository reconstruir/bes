#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

# A script to run python unit tests.  Does not use any bes code to avoid
# chicken-and-egg issues.
import argparse, ast, fnmatch, math, os, os.path as path, platform, random, re, subprocess, sys
import exceptions, glob, shutil, time, tempfile
from collections import namedtuple

# TODO:
#  - figure out how to stop on first failure within one module
#  - https://stackoverflow.com/questions/6813837/stop-testsuite-if-a-testcase-find-an-error
# - cleanup egg dropping
# - use AST for determining if a file has tests

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
  parser.add_argument('--timing',
                      '-t',
                      action = 'store_true',
                      default = False,
                      help = 'Show the amount of time it takes to run tests [ False ]')
  parser.add_argument('--verbose',
                      '-v',
                      action = 'store_true',
                      default = False,
                      help = 'Verbose debug output [ False ]')
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
                      action = 'store',
                      default = 'python',
                      help = 'Python executable to use [ python ]')
  parser.add_argument('--page',
                      '-p',
                      action = 'store_true',
                      default = False,
                      help = 'Page output with $PAGER [ False ]')
  parser.add_argument('--pager',
                      action = 'store',
                      default = os.environ.get('PAGER', 'more'),
                      help = 'Pager to use when paging [ %s ]' % (os.environ.get('PAGER', 'more')))
  parser.add_argument('--iterations',
                      '-i',
                      action = 'store',
                      default = 1,
                      type = int,
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
  
  cwd = os.getcwd()

  if not args.files:
    args.files = [ cwd ]
  
  files, filters = _separate_files_and_filters(args.files)

  files = file_resolve.resolve_files_and_dirs(files)

  # Don't include this script in the list since it needs to be run bes_test.py --unit to work
  files = [ f for f in files if not f.endswith('bes_test.py') ]
  
  test_map = unit_test_inspect.inspect_map(files)

  # We want only the files that have tests
  files = sorted(test_map.keys())
  
  if args.git:
    git_roots = git.roots_for_many_files(files)
    git_modified = []
    for root in git_roots:
      git_modified.extend(git.modified_python_files(root))
    files = file_resolve.resolve_files_and_dirs(git_modified)
    files = [ f for f in files if f in test_map ]

  if args.dump:
    unit_test_inspect.print_inspect_map(test_map, files, cwd)
    return 0
    
  patterns = _make_filters_patterns(filters)
  filename_patterns = [ p.filename for p in patterns if p.filename ]
  if filename_patterns:
    files = _match_filenames(files, filename_patterns)

  filtered_files = _filter_files(files, test_map, patterns)

  num_passed = 0
  num_failed = 0
  num_executed = 0
  num_tests = len(filtered_files)
  failed_tests = []

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

  if args.iterations > 1:
    filtered_files = sorted(filtered_files * args.iterations)
  
  if args.randomize:
    random.shuffle(filtered_files)

  if not args.dry_run and args.page:
    printer.OUTPUT = tempfile.NamedTemporaryFile(prefix = 'bes_test', delete = True, mode = 'w')

  total_tests = _count_tests(test_map, filtered_files)
  total_files = len(filtered_files)

  total_num_tests = 0
  options = test_options(args.dry_run, args.verbose, args.stop, args.timing)

  timings = {}
  
  for i, f in enumerate(filtered_files):
    if not f.filename in timings:
      timings[f.filename] = []
    result = _test_execute(args.python, test_map, f.filename, f.tests, options, i + 1, total_files, cwd)
    timings[f.filename].append(result.elapsed_time)
    total_num_tests += result.num_tests_run
    num_executed += 1
    if result.success:
      num_passed += 1
    else:
      num_failed += 1
      failed_tests.append(f)

    if args.stop and not result.success:
      break
  if args.dry_run:
    return 0
  num_skipped = num_tests - num_executed
  summary_parts = []

  if total_num_tests == total_tests:
    function_summary = '(%d %s)' % (total_tests, _make_test_string(total_tests))
  else:
    function_summary = '(%d of %d)' % (total_num_tests, total_tests)
    
  if num_failed > 0:
    summary_parts.append('%d of %d FAILED' % (num_failed, num_tests))
  summary_parts.append('%d of %d passed %s' % (num_passed, num_tests, function_summary))
  if num_skipped > 0:
    summary_parts.append('%d of %d skipped' % (num_skipped, num_tests))

  summary = '; '.join(summary_parts)
  printer.writeln('bes_test.py: %s' % (summary))
  if failed_tests:
    for f in failed_tests:
      printer.writeln('bes_test.py: FAILED: %s' % (file_util.remove_head(f.filename, cwd)))

  if num_failed > 0:
    rv = 1
  else:
    rv = 0

  if args.timing:
    filenames = sorted(timings.keys())
    num_filenames = len(filenames)
    for i, filename in zip(range(0, num_filenames), filenames):
      short_filename = file_util.remove_head(filename, cwd)
      all_timings = timings[filename]
      num_timings = len(all_timings)
      avg_ms = _timing_average(all_timings) * 1000.0
      if num_timings > 1:
        run_blurb = '(average of %d runs)' % (num_timings)
      else:
        run_blurb = ''
      if num_filenames > 1:
        count_blurb = '[%s of %s] ' % (i + 1, num_filenames)
      else:
        count_blurb = ''
        
      printer.writeln('bes_test.py: timing: %s%s - %2.2f ms %s' % (count_blurb, short_filename, avg_ms, run_blurb))
    
  if args.page:
    subprocess.call([ args.pager, printer.OUTPUT.name ])
    
  return rv

def _timing_average(l):
  return float(sum(l)) / float(len(l))

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

test_options = namedtuple('test_options', 'dry_run,verbose,stop_on_failure,timing')
test_result = namedtuple('test_result', 'success,num_tests_run,elapsed_time')

def _test_execute(python, test_map, filename, tests, options, index, total_files, cwd):
  short_filename = file_util.remove_head(filename, cwd)
  cmd = [ python, '-B', filename ]

  total_unit_tests = len(test_map[filename])
  
  if tests:
    cmd.extend([ '%s.%s' % (test.fixture, test.function) for test in tests ])
    wanted_unit_tests = len([ test for test in tests if test.filename == filename ])
  else:
    wanted_unit_tests = total_unit_tests

  if wanted_unit_tests == total_unit_tests:
    function_count_blurb = '(%d %s)' % (total_unit_tests, _make_test_string(total_unit_tests))
  else:
    function_count_blurb = '(%d of %d)' % (wanted_unit_tests, total_unit_tests)
    
  try:
#    if options.stop:
#      cmd.append('--stop')
    
    if total_files > 1:
      filename_count_blurb = ' ' + _make_count_blurb(index, total_files)
    else:
      filename_count_blurb = ''

    if options.dry_run:
      label = 'dry-run'
    else:
      label = 'testing'

    blurb = 'bes_test.py:%7s:%s %s - %s ' % (label, filename_count_blurb, short_filename, function_count_blurb)
    printer.writeln(blurb)

    if options.dry_run:
      return test_result(True, 0, 0.0)

    env = environ_util.make_clean_env()
    env['PYTHONDONTWRITEBYTECODE'] = 'x'
    time_start = time.time()
    process = subprocess.Popen(' '.join(cmd),
                               stdout = subprocess.PIPE,
                               stderr = subprocess.STDOUT,
                               shell = True,
                               env = env)
    output = process.communicate()
    exit_code = process.wait()
    elapsed_time = time.time() - time_start
    output = output[0]
    success = exit_code == 0
    writeln_output = not success or options.verbose
    if success:
      label = 'passed'
    else:
      label = 'FAILED'
    if writeln_output:
      printer.writeln('bes_test.py: %7s: %s' % (label, short_filename))
      printer.writeln(output)
    return test_result(success, wanted_unit_tests, elapsed_time)
  except Exception, ex:
    printer.writeln('bes_test.py: Caught exception on %s: %s' % (filename, str(ex)))
    return test_result(False, wanted_unit_tests, elapsed_time)

def _count_tests(test_map, tests):
  total = 0
  for test in tests:
    total += len(test_map[test.filename])
  return total
  
def _match_test(patterns, filename):
  filename = filename.lower()
  for pattern in patterns:
    if fnmatch.fnmatch(filename, pattern.lower()):
      return True
  return False

def _search_for_tests(search_patterns, where):
  result = []
  possible_tests = file_find.find_tests(where)
  for filename in possible_tests:
    if _match_test(search_patterns, filename):
      result.append(filename)
  return sorted(util.unique_list(result))

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

def _make_test_string(total):
  if total == 1:
    return 'test'
  else:
    return 'tests'

def _make_count_blurb(index, total):
  length = int(math.log10(total)) + 1
  index = str(index)
  count = str(total)
  index_blurb = (' ' * (length - len(index))) + index
  count_blurb = (' ' * (length - len(count))) + count
  return '[%s of %s]' % (index_blurb, count_blurb)

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
  filters = [ unit_test_desc.parse(f) for f in (filter_descriptions or []) ]
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
  return sorted(util.unique_list(result))

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
  
  @classmethod
  def mkdir(clazz, p):
    if path.isdir(p):
      return
    os.makedirs(p)

  @classmethod
  def save(clazz, filename, content = None, mode = None):
    'Atomically save content to filename using an intermediate temporary file.'
    dirname, basename = os.path.split(filename)
    clazz.mkdir(path.dirname(filename))
    tmp = tempfile.NamedTemporaryFile(prefix = basename, dir = dirname, delete = False, mode = 'w')
    if content:
      tmp.write(content)
    tmp.flush()
    os.fsync(tmp.fileno())
    tmp.close()
    if mode:
      os.chmod(tmp.name, mode)
    os.rename(tmp.name, filename)
    return filename
    
  @classmethod
  def remove(clazz, filename):
    try:
      if path.isdir(a):
        shutil.rmtree(filename)
      else:
        os.remove(filename)
    except Exception, ex:
      pass
      
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

  @classmethod
  def make_clean_env(clazz):
    'Return a clean environment suitable for deterministic build related tasks.'
    clean_path = '/bin:/usr/bin:/usr/sbin:/sbin'
    clean_vars = [ 'BES_LOG', 'PYTHONPATH', 'DISPLAY', 'HOME', 'LANG', 'SHELL', 'TERM', 'TERM_PROGRAM', 'TMOUT', 'TMPDIR', 'USER', 'XAUTHORITY', '__CF_USER_TEXT_ENCODING' ]
    clean_env = {}
    for k, v in os.environ.items():
      if k in clean_vars:
        clean_env[k] = v
    clean_env['PATH'] = clean_path
    return clean_env
    
class string_util(object):

  @classmethod
  def parse_list(clazz, s):
    return [ x.strip() for x in s.strip().split('\n') if x.strip() ]
  
class file_find(object):

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

class file_resolve(object):

  @classmethod
  def resolve_files_and_dirs(clazz, files_and_dirs):
    result = []
    for f in files_and_dirs:
      if path.isfile(f):
        result.append(path.abspath(path.normpath(f)))
      elif path.isdir(f):
        result += file_find.find_python_files(f)
    result += clazz.tests_for_many_files(result)
    result = util.unique_list(result)
    result = [ path.normpath(r) for r in result ]
    return sorted(result)

  @classmethod
  def find_tests(clazz, d):
    cmd = [ 'find', d, '-name', 'test_*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return string_util.parse_list(result)

  @classmethod
  def test_for_file(clazz, filename):
    basename = path.basename(filename)
    dirname = path.dirname(filename)
    name = path.splitext(basename)[0]
    test_filename = 'test_%s.py' % (name)
    test_full_path = path.join(dirname, 'tests', test_filename)
    if path.exists(test_full_path):
      return test_full_path
    return None

  @classmethod
  def tests_for_many_files(clazz, files):
    result = []
    for f in files:
      test = clazz.test_for_file(f)
      if test:
        result.append(test)
    return result
  
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
    result = [ clazz.parse_status_line(root, line) for line in lines ]
    return [ item for item in result if item ]

  @classmethod
  def status(clazz, root):
    cmd = [ 'git', 'st', '--porcelain', '.' ]
    result = subprocess.check_output(cmd, shell = False, cwd = root)
    items = clazz.parse_status(root, result)
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
    cwd = path.dirname(filename)
    result = subprocess.check_output(cmd, shell = False, cwd = cwd)
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

class unit_test_desc(namedtuple('unit_test_desc', 'filename,fixture,function')):

  def __new__(clazz, filename, fixture, function):
    return clazz.__bases__[0].__new__(clazz, filename, fixture, function)

  @classmethod
  def parse(clazz, s):
    'Parse a unit test description in the form filename:fixutre.function'
    filename, _, right = s.partition(':')
    if '.' in right:
      fixture, _, function = right.partition('.')
    else:
      fixture, function = ( None, right )
    return clazz(filename, fixture or None, function or None)
  
class unit_test_inspect(object):
  unit_test = namedtuple('unit_test', 'filename,fixture,function')

  @classmethod
  def inspect_file(clazz, filename):
    code = file_util.read(filename)
    tree = ast.parse(code)
    s = ast.dump(tree, annotate_fields = True, include_attributes = True)
    result = []
    for node in tree.body:
      if clazz._node_is_unit_test_class(node):
        for statement in node.body:
          if isinstance(statement, ast.FunctionDef):
            result.append(clazz.unit_test(filename, node.name, statement.name))
    return result

  @classmethod
  def _node_is_unit_test_class(clazz, node):
    if not isinstance(node, ast.ClassDef):
      return False
    for i, base in enumerate(node.bases):
      base_class_name = clazz._base_class_name(base)
      if base_class_name in [ 'unittest.TestCase', 'unit_test_helper' ]:
        return True
    return False
    
  @classmethod
  def _base_class_name(clazz, base):
    result = []
    for field in base._fields:
      value = getattr(base, field)
      if isinstance(value, ast.Name):
        result.append(value.id)
      elif isinstance(value, ( str, unicode)):
        result.append(value)
    return '.'.join(result)
    
  @classmethod
  def inspect_map(clazz, files):
    result = {}
    for f in files:
      f_path = path.abspath(f)
      try:
        tests = clazz.inspect_file(f_path)
        if tests:
          result[f_path] = clazz.inspect_file(f_path)
      except exceptions.SyntaxError, ex:
        printer.writeln('Failed to inspect: %s - %s' % (f, str(ex)))
        raise
      except Exception, ex:
        printer.writeln('Failed to inspect: %s - %s:%s' % (f, type(ex), str(ex)))
    return result

  @classmethod
  def print_inspect_map(clazz, inspect_map, files, cwd):
    for filename in sorted(inspect_map.keys()):
      if filename in files:
        printer.writeln('%s:' % (file_util.remove_head(filename, cwd)))
        for _, fixture, function in inspect_map[filename]:
          printer.writeln('  %s.%s' % (fixture, function))


class printer(object):
  OUTPUT = sys.stdout

  @classmethod
  def writeln(clazz, s):
    clazz.write(s)
    clazz.write('\n')
    clazz.flush()
          
  @classmethod
  def write(clazz, s, flush = False):
    clazz.OUTPUT.write(s)
    if flush:
      clazz.flush()
          
  @classmethod
  def flush(clazz):
    clazz.OUTPUT.flush()
          
import unittest

class test_case(unittest.TestCase):

  @classmethod
  def make_tmp_file(clazz, content, mode = None):
    content = content or ''
    _, filename = tempfile.mkstemp()
    file_util.save(filename, content = content, mode = mode)
    return filename
  
  def foo(self): 
    assert False

class test_unit_test_desc(test_case):

  def test_parse(self):
    self.assertEqual( ( 'foo.py', 'fix', 'func' ), unit_test_desc.parse('foo.py:fix.func') )
    self.assertEqual( ( 'foo.py', None, None ), unit_test_desc.parse('foo.py') )
    self.assertEqual( ( 'foo.py', None, None ), unit_test_desc.parse('foo.py:') )
    self.assertEqual( ( 'foo.py', None, 'fix' ), unit_test_desc.parse('foo.py:fix') )

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
    
class test_unit_test_inspect(test_case):

  def test_inspect_file(self):
    content = '''
import unittest
class test_apple_fixture(unittest.TestCase):

  def test_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def test_bar(self):
    self.assertEqual( 7, 3 + 4 )
'''
    filename = self.make_tmp_file(content)
    self.assertEqual( [
      ( filename, 'test_apple_fixture', 'test_foo' ),
      ( filename, 'test_apple_fixture', 'test_bar' ),
    ],
                      unit_test_inspect.inspect_file(filename) )
    file_util.remove(filename)

  def test_inspect_file_not_unit_test(self):
    content = '''
class test_apple_fixture(object):

  def test_foo(self):
    pass

  def test_bar(self):
    pass
'''
    filename = self.make_tmp_file(content)
    self.assertEqual( [], unit_test_inspect.inspect_file(filename) )
    file_util.remove(filename)

  def doesnt_work_test_inspect_file_TestCase_subclass(self):
    content = '''
import unittest
class unit_super(unittest.TestCase):
  _x = 5
class test_apple_fixture(unit_super):

  def test_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def test_bar(self):
    self.assertEqual( 7, 3 + 4 )


class somthing(unittest.TestCase):
  pass
'''
    filename = self.make_tmp_file(content)
    self.assertEqual( [
      ( filename, 'test_apple_fixture', 'test_foo' ),
      ( filename, 'test_apple_fixture', 'test_bar' ),
    ],
                      unit_test_inspect.inspect_file(filename) )
    file_util.remove(filename)
    
  def test_inspect_file_unit_test_helper(self):
    content = '''
from bes.test import unit_test_helper
class test_apple_fixture(unit_test_helper):

  def test_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def test_bar(self):
    self.assertEqual( 7, 3 + 4 )
'''
    filename = self.make_tmp_file(content)
    self.assertEqual( [
      ( filename, 'test_apple_fixture', 'test_foo' ),
      ( filename, 'test_apple_fixture', 'test_bar' ),
    ],
                      unit_test_inspect.inspect_file(filename) )
    file_util.remove(filename)
    
if len(sys.argv) >= 2 and sys.argv[1] in [ '--unit' ]:
  sys.argv = sys.argv[0:1]
  unittest.main()

if __name__ == '__main__':
  raise SystemExit(main())

    
