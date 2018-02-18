#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

# A script to run python unit tests.  Does not use any bes code to avoid
# chicken-and-egg issues and to be standalone
import argparse, ast, copy, fnmatch, math, os, os.path as path, platform, random, re, subprocess, sys
import exceptions, glob, shutil, time, tempfile
from collections import namedtuple

_NAME = path.basename(sys.argv[0])

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
                      action = 'append',
                      default = [],
                      help = 'Python executable) to use.  Multiple flags can be used for running with mutiple times with different python versions [ python ]')
#  parser.add_argument('--ignore',
#                      action = 'append',
#                      default = [],
#                      help = 'Patterns of filenames to ignore []')
  parser.add_argument('--page',
                      '-p',
                      action = 'store_true',
                      default = False,
                      help = 'Page output with $PAGER [ False ]')
  parser.add_argument('--profile',
                      action = 'store',
                      default = None,
                      help = 'Profile the code with cProfile and store the output in the given argument [ None ]')
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
  parser.add_argument('--print-tests',
                      action = 'store_true',
                      default = False,
                      help = 'Print the list of unit tests [ False ]')
  parser.add_argument('--print-files',
                      action = 'store_true',
                      default = False,
                      help = 'Print the list of unit files [ False ]')
  parser.add_argument('--egg',
                      action = 'store_true',
                      default = False,
                      help = 'Make an egg of the package and run the tests against that instead the live files. [ False ]')
  parser.add_argument('--save-egg',
                      action = 'store_true',
                      default = False,
                      help = 'Save the egg in the current directory. [ False ]')
  parser.add_argument('--ignore',
                      action = 'append',
                      default = [],
                      help = 'Patterns of filenames to ignore []')
  args = parser.parse_args()
  
  cwd = os.getcwd()

  if not args.files:
    args.files = [ cwd ]
  
  files, filters = _separate_files_and_filters(args.files)

  files = file_resolve.resolve_files_and_dirs(files)
  
  # Don't include this script in the list since it needs to be run bes_test.py --unit to work
  files = [ f for f in files if not f.endswith('bes_test.py') ]
  files = [ f for f in files if f.lower().endswith('.py') ]
  files = [ f for f in files if not file_util.is_broken_link(f) ]
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

  if args.print_tests:
    unit_test_inspect.print_inspect_map(test_map, files, cwd)
    return 0
    
  patterns = _make_filters_patterns(filters)
  filename_patterns = [ p.filename for p in patterns if p.filename ]
  if filename_patterns:
    files = _match_filenames(files, filename_patterns)

  filtered_files = file_filter.filter_files(files, test_map, patterns)
  if patterns and not filtered_files:
    printer.writeln_name('No matches for: %s' % (' '.join([ str(p) for p in patterns])))
    return 1
    
  filtered_files = file_filter.ignore_files(filtered_files, args.ignore)
  if not filtered_files:
    return 1

  if args.print_files:
    for filename in file_filter.filenames(filtered_files):
      print(path.relpath(filename))
    return 0

  try:
    any_git_root = git.root(filtered_files[0].filename)
  except subprocess.CalledProcessError as ex:
    any_git_root = None
  if any_git_root:
    config_find_root = file_util.parent_dir(any_git_root)
    bescfg = config_file.load_configs(config_find_root)
#    print('bescfg: %s' % (str(bescfg)))
    env_dirs = file_filter.env_dirs(filtered_files)
    names = [ bescfg.env_dirs[env_dir]['name'] for env_dir in env_dirs ]
    resolved_deps = dependency_resolver.resolve_deps(bescfg.dep_map, names)
#    print('env_dirs=%s' % (env_dirs))
#    print('names=%s' % (names))
#    print('resolved_deps=%s' % (str(resolved_deps)))
    for name in resolved_deps:
      config = bescfg.configs[name]
      pythonpath = config.get('PYTHONPATH', None)
#      print('name=%s; pythonpath=%s' % (name, pythonpath))
      environ_util.pythonpath_prepend(':'.join(pythonpath))
   
  num_passed = 0
  num_failed = 0
  num_executed = 0
  num_tests = len(filtered_files)
  failed_tests = []

  # Remove current dir from sys.path to avoid side effects
  if cwd in sys.path:
    sys.path.remove(cwd)

  if args.egg:
    setup_dot_py = path.join(cwd, 'lib', 'setup.py')
    if not path.isfile(setup_dot_py):
      raise RuntimeError('No setup.py found in %s to make the egg.' % (cwd))
    egg = egg_util.make(setup_dot_py)
    environ_util.pythonpath_remove(cwd)
    environ_util.pythonpath_prepend(egg)
    if args.save_egg:
      file_util.copy(egg, path.join(cwd, path.basename(egg)))
    #print('PYTHONPATH: %s' % (':'.join(environ_util.pythonpath_get())))
    
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

  if args.profile:
    args.profile = path.abspath(args.profile)

  if not args.python:
    args.python = [ 'python' ]
  
  options = test_options(args.dry_run, args.verbose, args.stop, args.timing,
                         args.profile, args.python)
  
  timings = {}

  total_time_start = time.time()
  
  stopped = False
  for i, f in enumerate(filtered_files):
    if not f.filename in timings:
      timings[f.filename] = []
    for python_exe in args.python:
      result = _test_execute(python_exe, test_map, f.filename, f.tests, options, i + 1, total_files, cwd)
      timings[f.filename].append(result.elapsed_time)
      total_num_tests += result.num_tests_run
      num_executed += 1
      if result.success:
        num_passed += 1
      else:
        num_failed += 1
        failed_tests.append(( python_exe, f ))
      if args.stop and not result.success:
        stopped = True
    if stopped:
      break
  total_elapsed_time = 1000 * (time.time() - total_time_start)
    
  if args.dry_run:
    return 0
  num_skipped = num_tests - num_executed
  summary_parts = []

  if total_num_tests == total_tests:
    function_summary = '(%d %s)' % (total_tests, _make_test_string(total_tests))
  else:
    function_summary = '(%d of %d %s)' % (total_num_tests, total_tests, _make_test_string(total_tests))
    
  if num_failed > 0:
    summary_parts.append('%d of %d FAILED' % (num_failed, num_tests))
  summary_parts.append('%d of %d passed %s' % (num_passed, num_tests, function_summary))
  if num_skipped > 0:
    summary_parts.append('%d of %d skipped' % (num_skipped, num_tests))

  summary = '; '.join(summary_parts)
  printer.writeln_name('%s' % (summary))
  if failed_tests:
    longest_python_exe = max([len(path.basename(p)) for p in options.interpreters])
    for python_exe, f in failed_tests:
      if len(options.interpreters) > 1:
        python_exe_blurb = path.basename(python_exe).rjust(longest_python_exe)
      else:
        python_exe_blurb = ''
      printer.writeln_name('FAILED: %s %s' % (python_exe_blurb, file_util.remove_head(f.filename, cwd)))

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
        
      printer.writeln_name('timing: %s%s - %2.2f ms %s' % (count_blurb, short_filename, avg_ms, run_blurb))
    if total_elapsed_time >= 1000.0:
      printer.writeln_name('total time: %2.2f s' % (total_elapsed_time / 1000.0))
    else:
      printer.writeln_name('total time: %2.2f ms' % (total_elapsed_time))
      
  if args.page:
    subprocess.call([ args.pager, printer.OUTPUT.name ])
    
  return rv

def _timing_average(l):
  return float(sum(l)) / float(len(l))

class file_filter(object):
  file_and_tests = namedtuple('file_and_tests', 'filename,tests')

  @classmethod
  def filter_files(clazz, files, available, patterns):
    if not patterns:
      return [ clazz.file_and_tests(filename, None) for filename in files ]
    result = []
    for filename in files:
      assert filename in available
      available_for_filename = available[filename]
      matching_tests = _matching_tests(available_for_filename, patterns)
      if matching_tests:
        result.append(clazz.file_and_tests(filename, matching_tests))
    return result

  @classmethod
  def ignore_files(clazz, filtered_files, ignore_patterns):
    return [ f for f in filtered_files if not clazz.filename_matches_any_pattern(f.filename, ignore_patterns) ]

  @classmethod
  def filenames(clazz, filtered_files):
    return sorted([ f.filename for f in filtered_files ])

  @classmethod
  def common_prefix(clazz, filtered_files):
    return path.commonprefix([f.filename for f in filtered_files]).rpartition(os.sep)[0]
  
  @classmethod
  def filename_matches_any_pattern(clazz, filename, patterns):
    for pattern in patterns:
      if fnmatch.fnmatch(filename, pattern):
        return True
    return False
  
  @classmethod
  def env_dirs(clazz, filtered_files):
    filenames = [ f.filename for f in filtered_files ]
    roots = [ clazz._test_file_get_root(f) for f in filenames ]
    roots = util.unique_list(roots)
    roots = [ f for f in roots if f ]
    result = []
    for root in roots:
      env_dir = path.join(root, 'env')
      if path.isdir(env_dir):
        result.append(env_dir)
    return result
  
  @classmethod
  def _test_file_get_root(clazz, filename):
    if '/lib/' in filename:
      return filename.partition('/lib')[0]
    elif '/bin/' in filename:
      return filename.partition('/bin')[0]
    else:
      return None

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

test_options = namedtuple('test_options', 'dry_run,verbose,stop_on_failure,timing,profile_output,interpreters')
test_result = namedtuple('test_result', 'success,num_tests_run,elapsed_time')

def _test_data_dir(filename):
  data_dir = os.environ.get('BES_TEST_DATA_DIR', None)
  if not data_dir:
    data_dir = file_find.find_in_ancestors(path.dirname(filename), 'test_data')
  return data_dir or ''

def _test_execute(python_exe, test_map, filename, tests, options, index, total_files, cwd):
  short_filename = file_util.remove_head(filename, cwd)

  cmd = [ python_exe, '-B' ]

  if options.profile_output:
    cmd.extend(['-m', 'cProfile', '-o', options.profile_output ])

  cmd.append(filename)
    
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
    longest_python_exe = max([len(path.basename(p)) for p in options.interpreters])
    if len(options.interpreters) > 1:
      python_exe_blurb = path.basename(python_exe).rjust(longest_python_exe)
      python_exe_blurb_sep = ' '
    else:
      python_exe_blurb = ''
      python_exe_blurb_sep = ''
    blurb = '%7s:%s%s%s %s - %s ' % (label, filename_count_blurb, python_exe_blurb_sep, python_exe_blurb, short_filename, function_count_blurb)
    printer.writeln_name(blurb)

    if options.dry_run:
      return test_result(True, 0, 0.0)

    env = environ_util.make_clean_env()
    env['PYTHONDONTWRITEBYTECODE'] = 'x'
    env['BES_TEST_DATA_DIR'] = _test_data_dir(filename)
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
      printer.writeln_name('%7s: %s' % (label, short_filename))
      printer.writeln(output)
    return test_result(success, wanted_unit_tests, elapsed_time)
  except Exception, ex:
    printer.writeln_name('Caught exception on %s: %s' % (filename, str(ex)))
    return test_result(False, wanted_unit_tests, 0.0)

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

  @classmethod
  def listify(clazz, o):
    'Return a list version of o whether its iterable or not.'
    if isinstance(o, list): #clazz.is_iterable(o):
      return [ x for x in o ]
    else:
      return [ o ]

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
  def copy(clazz, src, dst):
    clazz.mkdir(path.dirname(dst))
    shutil.copy(src, dst)
    
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

  @classmethod
  def parent_dir(clazz, d):
    return path.normpath(path.join(d, os.pardir))

  @classmethod
  def is_broken_link(clazz, filename):
    return path.islink(filename) and not path.isfile(os.readlink(filename))
  
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
  def pythonpath_contains(clazz, what):
    pythonpath = clazz.pythonpath_get()
    return what in clazz.pythonpath_get()

  @classmethod
  def unixpath_get(clazz):
    return os.environ.get('PATH', '').split(':')
  
  @classmethod
  def unixpath_set(clazz, unixpath):
    assert isinstance(unixpath, list)
    os.environ['PATH'] = ':'.join(unixpath)

  @classmethod
  def unixpath_remove(clazz, what):
    unixpath = clazz.unixpath_get()
    if what in unixpath:
      unixpath.remove(what)
    clazz.unixpath_set(unixpath)
    
  @classmethod
  def unixpath_prepend(clazz, what):
    unixpath = clazz.unixpath_get()
    unixpath.insert(0, what)
    clazz.unixpath_set(unixpath)

  @classmethod
  def unixpath_contains(clazz, what):
    unixpath = clazz.unixpath_get()
    return what in clazz.unixpath_get()

  @classmethod
  def make_clean_env(clazz):
    'Return a clean environment suitable for deterministic build related tasks.'
    clean_path = '/bin:/usr/bin:/usr/sbin:/sbin'
    clean_vars = [ 'BES_LOG', 'PYTHONPATH', 'DISPLAY', 'HOME', 'LANG', 'SHELL', 'TERM', 'TERM_PROGRAM', 'TMOUT', 'TMPDIR', 'USER', 'XAUTHORITY', '__CF_USER_TEXT_ENCODING', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH' ]
    clean_env = {}
    for k, v in os.environ.items():
      if k in clean_vars or k.startswith('REBUILD'):
        clean_env[k] = v
    clean_env['PATH'] = clean_path
    return clean_env
    
class string_util(object):

  @classmethod
  def parse_list(clazz, s):
    return [ x.strip() for x in s.strip().split('\n') if x.strip() ]

  @classmethod
  def split_by_white_space(clazz, s):
    tokens = [ token.strip() for token in re.split('\s+', s) ]
    return [ token for token in tokens if token ]

  @classmethod
  def remove_comments(clazz, s):
    return re.sub('#.*', '', s)
  
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

  @classmethod
  def find(clazz, d, *args):
    cmd = [ 'find', d ] + list(args)
    result = subprocess.check_output(cmd, shell = False)
    return string_util.parse_list(result)

  @classmethod
  def find_in_ancestors(clazz, where, filename):
    assert path.isdir(where)
    parent = where
    while True:
      what = path.join(parent, filename)
      if path.exists(what):
        return what
      parent = file_util.parent_dir(parent)
      if parent == '/':
        return None
  
class file_resolve(object):

  @classmethod
  def resolve_files_and_dirs(clazz, files_and_dirs):
    result = []
    for f in files_and_dirs:
      if path.isfile(f):
        result += clazz._resolve_file(f)
      elif path.isdir(f):
        result += clazz._resolve_dir(f)
    result += clazz.tests_for_many_files(result)
    result = util.unique_list(result)
    result = [ path.normpath(r) for r in result ]
    return sorted(result)

  @classmethod
  def _resolve_dir(clazz, d):
    assert path.isdir(d)
    config = clazz._read_config_file(d)
    if config is None:
      return file_find.find_python_files(d)
    return clazz.resolve_files_and_dirs(config)
    
  @classmethod
  def _resolve_file(clazz, f):
    assert path.isfile(f)
    return [ path.abspath(path.normpath(f)) ]

  @classmethod
  def _read_config_file(clazz, d):
    p = path.join(d, '.bes_test_dirs')
    if not path.exists(p):
      return None
    content = file_util.read(p)
    lines = [ f for f in content.split('\n') if f ]
    files = [ path.join(d, f) for f in lines ]
    return sorted(util.unique_list(files))
  
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
    src_dir = path.join(path.dirname(setup_dot_py), '..')
    shutil.rmtree(temp_dir)
    shutil.copytree(src_dir, temp_dir, symlinks = True)
    cmd = [ 'python', 'setup.py', 'bdist_egg' ]
    build_dir = path.join(temp_dir, 'lib')
    subprocess.check_output(cmd, shell = False, cwd = build_dir)
    eggs = glob.glob('%s/dist/*.egg' % (build_dir))
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

  def __str__(self):
    v = []
    if self.filename:
      v.append(self.filename)
      v.append('.')
    if self.fixture:
      v.append(self.fixture)
    v.append(':')
    if self.function:
      v.append(self.function)
    return ''.join(v)
  
class unit_test_inspect(object):
  unit_test = namedtuple('unit_test', 'filename,fixture,function')

  @classmethod
  def inspect_file(clazz, filename):
    code = file_util.read(filename)
    if 'bes:skip_unit_test=1' in code:
      return []
    tree = ast.parse(code, filename = filename)
    s = ast.dump(tree, annotate_fields = True, include_attributes = True)
    result = []
    for node in tree.body:
      if clazz._node_is_unit_test_class(node):
        for statement in node.body:
          if isinstance(statement, ast.FunctionDef):
            if statement.name.startswith('test_'):
              result.append(clazz.unit_test(filename, node.name, statement.name))
    return result

  @classmethod
  def _node_is_unit_test_class(clazz, node):
    if not isinstance(node, ast.ClassDef):
      return False
    for i, base in enumerate(node.bases):
      base_class_name = clazz._base_class_name(base)
      if base_class_name in [ 'unittest.TestCase', 'unit_test', 'script_unit_test' ]:
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
  def writeln_name(clazz, s):
    clazz.write(_NAME)
    clazz.write(': ')
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

class config_file(object):

  bescfg = namedtuple('bescfg', 'root_dir,configs,dep_map,env_dirs')

  @classmethod
  def load_configs(clazz, d):
    root_dir = path.abspath(d)
    configs = {}
    config_files = config_file.find_config_files(root_dir)
    env_dirs = {}
    for f in config_files:
      config = config_file.read_config_file(f)
      configs[config['name']] = config
      env_dirs[path.join(config['root_dir'], 'env')] = config
    dep_map = clazz._make_dep_map(configs)
    return clazz.bescfg(root_dir, configs, dep_map, env_dirs)
    
  @classmethod
  def _make_dep_map(clazz, configs):
    dep_map = {}
    for name, config in configs.items():
      dep_map[name] = set(config.get('requires', []))
    return dep_map
    
  @classmethod
  def find_config_files(clazz, d):
    return file_find.find(d, '-maxdepth', '4', '-name', '*.bescfg')

  @classmethod
  def read_config_file(clazz, filename):
    filename = path.abspath(filename)
    root = path.normpath(path.join(path.dirname(filename), '..'))
    content = file_util.read(filename)
    config = clazz.parse(content)
    variables = {
      'root': root,
      'rebuild_dir': path.expanduser('~/.rebuild'),
    }
    config = clazz.substitute_variables(config, variables)
    config['filename'] = filename
    config['root_dir'] = root
    return config
    
  @classmethod
  def parse(clazz, s):
    result = {}
    lines = s.split('\n')
    lines = [ string_util.remove_comments(line) for line in lines ]
    lines = [ line.strip() for line in lines ]
    lines = [ line for line in lines if line ]
    for line in lines:
      key, sep, value = line.partition(':')
      assert sep == ':'
      key = key.strip()
      value = value.strip()
      if key == 'requires':
        value = tuple(sorted(string_util.split_by_white_space(value)))
      elif key in [ 'PATH', 'PYTHONPATH' ]:
        value = value.split(':')
      assert key not in result
      result[key] = value
    return result

  @classmethod
  def substitute_variables(clazz, config, variables):
    assert isinstance(config, dict)
    assert isinstance(variables, dict)
    result = copy.deepcopy(config)
    for key in config.keys():
      clazz._sub_one(result, key, variables)
    return result
    
  @classmethod
  def _sub_one(clazz, config, key, variables):
    assert isinstance(config, dict)
    assert isinstance(key, basestring)
    assert isinstance(variables, dict)
    value = config[key]
    for var_name, var_value in variables.items():
      sub_key = '${%s}' % (var_name)
      value = clazz._replace_value(value, sub_key, var_value)
    config[key] = value
    
  @classmethod
  def _replace_value(clazz, value, sub_key, sub_value):
    assert isinstance(value, ( basestring, tuple, list ) )
    assert isinstance(sub_key, basestring)
    assert isinstance(sub_value, basestring)
    if isinstance(value, basestring):
      return value.replace(sub_key, sub_value)
    elif isinstance(value, tuple):
      return tuple([ x.replace(sub_key, sub_value) for x in value ])
    elif isinstance(value, list):
      return [ x.replace(sub_key, sub_value) for x in value ]

def _python_exe_blurb(python_exe, interpreters):
  if len(interpreters) <= 1:
    return ''
  longest_python_exe = max([len(path.basename(p)) for p in options.interpreters])
  return path.basename(python_exe).rjust(longest_python_exe)
    
class toposort(object):    
  #######################################################################
  # Implements a topological sort algorithm.
  #
  # Copyright 2014 True Blade Systems, Inc.
  #
  # Licensed under the Apache License, Version 2.0 (the "License");
  # you may not use this file except in compliance with the License.
  # You may obtain a copy of the License at
  #
  # http://www.apache.org/licenses/LICENSE-2.0
  #
  # Unless required by applicable law or agreed to in writing, software
  # distributed under the License is distributed on an "AS IS" BASIS,
  # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  # See the License for the specific language governing permissions and
  # limitations under the License.
  #
  # Notes:
  #  Based on http://code.activestate.com/recipes/578272-topological-sort
  #   with these major changes:
  #    Added unittests.
  #    Deleted doctests (maybe not the best idea in the world, but it cleans
  #     up the docstring).
  #    Moved functools import to the top of the file.
  #    Changed assert to a ValueError.
  #    Changed iter[items|keys] to [items|keys], for python 3
  #     compatibility. I don't think it matters for python 2 these are
  #     now lists instead of iterables.
  #    Copy the input so as to leave it unmodified.
  #    Renamed function from toposort2 to toposort.
  #    Handle empty input.
  #    Switch tests to use set literals.
  #
  ########################################################################

    @classmethod
    def toposort(clazz, data):
        """Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependences, each subsequent set consists of items that depend upon
    items in the preceeding sets.
    """
  
        from functools import reduce as _reduce
        
        # Special case empty input.
        if len(data) == 0:
            return
    
        # Copy the input so as to leave it unmodified.
        data = data.copy()
    
        # Ignore self dependencies.
        for k, v in data.items():
            v.discard(k)
        # Find all items that don't depend on anything.
        extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())
        # Add empty dependences where needed.
        data.update({item:set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in data.items() if len(dep) == 0)
            if not ordered:
                break
            yield ordered
            data = {item: (dep - ordered)
                    for item, dep in data.items()
                        if item not in ordered}
        if len(data) != 0:
            ex = ValueError('Cyclic dependencies exist among these items: {}'.format(', '.join(repr(x) for x in data.items())))
            setattr(ex, 'cyclic_deps', data)
            raise ex
    
    @classmethod
    def toposort_flatten(clazz, data, sort=True):
        """Returns a single list of dependencies. For any set returned by
    toposort(), those items are sorted and appended to the result (just to
    make the results deterministic)."""
    
        result = []
        for d in clazz.toposort(data):
            result.extend((sorted if sort else list)(d))
        return result

class cyclic_dependency_error(Exception):
  def __init__(self, message, cyclic_deps):
    super(cyclic_dependency_error, self).__init__(message)
    self.cyclic_deps = cyclic_deps

class missing_dependency_error(Exception):
  def __init__(self, message, missing_deps):
    super(missing_dependency_error, self).__init__(message)
    self.missing_deps = missing_deps
      
class dependency_resolver(object):

  @classmethod
  def build_order_flat(clazz, dep_map):
    'Return the build order for the given map of scripts.'
    return toposort.toposort_flatten(dep_map, sort = True)

  @classmethod
  def build_order(clazz, dep_map):
    'Return the build order for the given map of scripts.'
    return [ d for d in toposort.toposort(dep_map) ]

  @classmethod
  def check_missing(clazz, available, wanted):
    'Return a list of packages wanted but missing in available.'
    assert isinstance(available, ( list, set ))
    assert isinstance(wanted, ( list, set ))
    missing_set = set(wanted) - set(available)
    return sorted(list(missing_set))

  @classmethod
  def is_cyclic(clazz, dep_map):
    'Return True if the map has an cyclycal dependencies.'
    return len(clazz.cyclic_deps(dep_map)) > 0

  @classmethod
  def cyclic_deps(clazz, dep_map):
    'Return a list of dependencies in dep_map that that are cyclic.'
    try:
      clazz.build_order_flat(dep_map)
      return []
    except ValueError, ex:
      cyclic_deps = getattr(ex, 'cyclic_deps')
      return sorted(cyclic_deps.keys())

  @classmethod
  def resolve_deps(clazz, dep_map, names):
    '''
    Return a set of resolved dependencies for the given name or names.
    Sorted alphabetically, not in build order.
    '''

    cyclic_deps = clazz.cyclic_deps(dep_map)
    if len(cyclic_deps) > 0:
      raise cyclic_dependency_error('Cyclic dependencies found: %s' % (' '.join(cyclic_deps)), cyclic_deps)

    order = clazz.build_order_flat(dep_map)
    names = util.listify(names)
    result = set(names)
    for name in names:
      result |= clazz.__resolve_deps(dep_map, name)
    return sorted(list(result))

  @classmethod
  def __resolve_deps(clazz, dep_map, name):
    'Return a set of resolved dependencies for the given name.  Not in build order.'
    assert isinstance(name, basestring)
    if name not in dep_map:
      raise missing_dependency_error('Missing dependency: %s' % (name), [ name ])
    result = set()
    deps = dep_map[name]
    assert isinstance(deps, set)
    result |= deps
    for dep in deps:
      result |= clazz.__resolve_deps(dep_map, dep)
    return result
      
import unittest

class test_case(unittest.TestCase):

  @classmethod
  def make_tmp_file(clazz, content, mode = None):
    content = content or ''
    _, filename = tempfile.mkstemp()
    file_util.save(filename, content = content, mode = mode)
    return filename
  
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

  def test_split_by_white_space(self):
    self.assertEqual( [ 'foo', 'bar' ], string_util.split_by_white_space('    foo  bar   ') )
    
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

  def test_inspect_file_disbled(self):
    content = '''
import unittest
class test_apple_fixture(unittest.TestCase):

  def xtest_foo(self):
    self.assertEqual( 6, 3 + 3 )

  def xtest_bar(self):
    self.assertEqual( 7, 3 + 4 )
'''
    filename = self.make_tmp_file(content)
    self.assertEqual( [
    ],
                      unit_test_inspect.inspect_file(filename) )
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
    
  def test_inspect_file_unit_test(self):
    content = '''
from bes.testing.unit_test import unit_test
class test_apple_fixture(unit_test):

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

class test_config_file(test_case):

  def test_parse(self):
    text = '''
# foo
name: foo
PATH: ${root}/bin
PYTHONPATH: ${root}/lib
requires: bar baz
'''
    
    self.assertEqual( {
      'name': 'foo',
      'PATH': [ '${root}/bin' ],
      'PYTHONPATH': [ '${root}/lib' ],
      'requires': ( 'bar', 'baz' ),
    }, config_file.parse(text) )

  def test_substitute_variables(self):
    config = {
      'name': 'foo',
      'PATH': [ '${root}/bin' ],
      'PYTHONPATH': [ '${root}/lib' ],
      'requires': ( 'bar', 'baz' ),
    }
    variables = { 'root': '/home/pato' }
    self.assertEqual( {
      'name': 'foo',
      'PATH': [ '/home/pato/bin' ],
      'PYTHONPATH': [ '/home/pato/lib' ],
      'requires': ( 'bar', 'baz' ),
    }, config_file.substitute_variables(config, variables) )

class test_dependency_resolver(test_case):

  def test_resolve_deps(self):
    dep_map = {
      'foo': set(),
      'bar': set(),
      'kiwi': set( [ 'foo' ] ),
      'cheese': set( [ 'kiwi', 'bar' ] ),
    }
    self.assertEqual( [ 'foo' ], dependency_resolver.resolve_deps(dep_map, 'foo') )
    self.assertEqual( [ 'bar' ], dependency_resolver.resolve_deps(dep_map, 'bar') )
    self.assertEqual( [ 'foo', 'kiwi' ], dependency_resolver.resolve_deps(dep_map, [ 'foo', 'kiwi' ]) )
    self.assertEqual( [ 'foo' ], dependency_resolver.resolve_deps(dep_map, [ 'foo', 'foo' ]) )

  def test_resolve_deps_cyclic(self):
    cycle_dep_map = {
      'c1': set( [ 'c2' ] ),
      'c2': set( [ 'c1' ] ),
      'c3': set( [ 'c4' ] ),
      'c4': set( [ 'c3' ] ),
      'f1': set( [ 'f2' ] ),
      'f2': set( [ 'f3' ] ),
      'f3': set( [ 'f1' ] ),
      'n1': set( [] ),
      'n2': set( [ 'n1' ] ),
    }
    with self.assertRaises(cyclic_dependency_error) as context:
      dependency_resolver.resolve_deps(cycle_dep_map, [ 'c1' ])
    self.assertEquals( [ 'c1', 'c2', 'c3', 'c4', 'f1', 'f2', 'f3' ], context.exception.cyclic_deps )

  def test_resolve_deps_missing(self):
    missing_dep_map = {
      'c1': set( [ 'x1' ] ),
      'c2': set( [ 'x2' ] ),
    }
    with self.assertRaises(missing_dependency_error) as context:
      dependency_resolver.resolve_deps(missing_dep_map, [ 'c1' ])
    self.assertEquals( [ 'x1' ], context.exception.missing_deps )

  def test_is_cyclic(self):
    cycle_dep_map = {
      'c1': set( [ 'c2' ] ),
      'c2': set( [ 'c1' ] ),
      'c3': set( [ 'c4' ] ),
      'c4': set( [ 'c3' ] ),
      'f1': set( [ 'f2' ] ),
      'f2': set( [ 'f3' ] ),
      'f3': set( [ 'f1' ] ),
    }
    no_cycle_dep_map = {
      'f1': set( [ 'f3' ] ),
      'f2': set( [ 'f3' ] ),
    }
    self.assertEqual( True, dependency_resolver.is_cyclic(cycle_dep_map) )
    self.assertEqual( False, dependency_resolver.is_cyclic(no_cycle_dep_map) )

  def test_cyclic_deps(self):
    cycle_dep_map = {
      'c1': set( [ 'c2' ] ),
      'c2': set( [ 'c1' ] ),
      'c3': set( [ 'c4' ] ),
      'c4': set( [ 'c3' ] ),
      'f1': set( [ 'f2' ] ),
      'f2': set( [ 'f3' ] ),
      'f3': set( [ 'f1' ] ),
    }
    self.assertEqual( [ 'c1', 'c2', 'c3', 'c4', 'f1', 'f2', 'f3' ], dependency_resolver.cyclic_deps(cycle_dep_map) )

  def test_check_missing(self):
    available = [
      'd1',
      'd2',
      'd3',
    ]
    self.assertEqual( [], dependency_resolver.check_missing(available, [ 'd1' ]) )
    self.assertEqual( [], dependency_resolver.check_missing(available, [ 'd1', 'd2', 'd3' ]) )
    self.assertEqual( [ 'n1' ], dependency_resolver.check_missing(available, [ 'd1', 'd2', 'd3', 'n1' ]) )
    self.assertEqual( [ 'n1' ], dependency_resolver.check_missing(available, [ 'n1' ]) )
    self.assertEqual( [ 'n1', 'n2' ], dependency_resolver.check_missing(available, [ 'd1', 'd2', 'd3', 'n1', 'n2' ]) )
    self.assertEqual( [ 'n1', 'n2' ], dependency_resolver.check_missing(available, [ 'n1', 'n2' ]) )
    
if len(sys.argv) >= 2 and sys.argv[1] in [ '--unit' ]:
  sys.argv = sys.argv[0:1]
  unittest.main()

if __name__ == '__main__':
  raise SystemExit(main())

    
