#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# A script to run python unit tests.  Does not use any bes code to avoid
# chicken-and-egg issues and to be standalone
import argparse, ast, copy, fnmatch, math, os, os.path as path, platform, random, re, subprocess, sys
import exceptions, glob, shutil, time, tempfile
from collections import namedtuple

from bes.testing.framework import argument_resolver, config_file_caca, file_filter, unit_test_inspect
from bes.testing.framework import unit_test_description
from bes.common import algorithm, object_util, string_util
from bes.version import version_info
from bes.git import git
from bes.text import comments, lines
from bes.fs import file_find, file_path, file_util
from bes.dependency import dependency_resolver
from bes.egg import egg

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
  parser.add_argument('--version',
                      '-V',
                      action = 'store_true',
                      default = False,
                      help = 'Show version [ False ]')
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
  parser.add_argument('--check-pre-commit',
                      action = 'store_true',
                      default = False,
                      help = 'Run pre commit checks [ False ]')
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

  if args.version:
    import bes
    print(version_info.version_info_for_module(bes).version_string())
    return 0
  
  if not args.files:
    args.files = [ cwd ]

  ar = argument_resolver(cwd, args.files)
  
  files = file_resolve.resolve_files_and_dirs(ar.files)
  
  # Don't include this script in the list since it needs to be run bes_test.py --unit to work
  files = [ f for f in files if not f.endswith('bes_test.py') ]
  files = [ f for f in files if 'test_data/bes.testing' not in f ]
  files = [ f for f in files if f.lower().endswith('.py') ]
  files = [ f for f in files if not file_util.is_broken_link(f) ]
  test_map = unit_test_inspect.inspect_map(files)

  # We want only the files that have tests
  files = sorted(test_map.keys())
  
  if args.git:
    git_roots = algorithm.unique([ git.root(f) for f in files ])
    git_modified = []
    for root in git_roots:
      modified_py_files = [ f for f in git.modified_files(root) if f.endswith('.py') ]
      git_modified.extend(modified_py_files)
      files = file_resolve.resolve_files_and_dirs(git_modified)
    files = [ f for f in files if f in test_map ]
  if args.print_tests:
    unit_test_inspect.print_inspect_map(test_map, files, cwd)
    return 0
    
  patterns = _make_filters_patterns(ar.filters)
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
    config_find_root = file_path.parent_dir(any_git_root)
    bescfg = config_file_caca.load_configs(config_find_root)
    #print('bescfg: %s' % (str(bescfg)))
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
    setup_dot_py = path.join(cwd, 'setup.py')
    if not path.isfile(setup_dot_py):
      raise RuntimeError('No setup.py found in %s to make the egg.' % (cwd))
    egg_zip = egg.make(setup_dot_py)
    environ_util.pythonpath_remove(cwd)
    environ_util.pythonpath_prepend(egg_zip)
    if args.save_egg:
      file_util.copy(egg_zip, path.join(cwd, path.basename(egg_zip)))
    #print('PYTHONPATH: %s' % (':'.join(environ_util.pythonpath_get())))

  if args.check_pre_commit:
    missing_from_git = []
    for f in filtered_files:
      filename = f.filename
      st = git.status(git.root(filename), filename)
      if st:
        assert len(st) == 1
        if st[0].action == '??':
          missing_from_git.append(filename)
    if missing_from_git:
      for f in missing_from_git:
        printer.writeln_name('PRE_COMMIT: missing from git: %s' % (path.relpath(f)))
      return 1
    
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
    patterns.append(unit_test_description(filename_pattern, fixture_pattern, function_pattern))
  return patterns

def _match_filenames(files, patterns):
  result = []
  for filename in files:
    if _match_test(patterns, filename):
      result.append(filename)
  return sorted(algorithm.unique(result))

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
    
class caca_file_find(object):

  @classmethod
  def find_python_files(clazz, d):
    cmd = [ 'find', d, '-name', '*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return lines.parse_lines(result)

  @classmethod
  def find_tests(clazz, d):
    cmd = [ 'find', d, '-name', 'test_*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return lines.parse_lines(result)

  @classmethod
  def find(clazz, d, *args):
    cmd = [ 'find', d ] + list(args)
    result = subprocess.check_output(cmd, shell = False)
    return lines.parse_lines(result)

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
    result = algorithm.unique(result)
    result = [ path.normpath(r) for r in result ]
    return sorted(result)

  @classmethod
  def _resolve_dir(clazz, d):
    assert path.isdir(d)
    config = clazz._read_config_file(d)
    if config is None:
      return caca_file_find.find_python_files(d)
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
    return sorted(algorithm.unique(files))
  
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

def _python_exe_blurb(python_exe, interpreters):
  if len(interpreters) <= 1:
    return ''
  longest_python_exe = max([len(path.basename(p)) for p in options.interpreters])
  return path.basename(python_exe).rjust(longest_python_exe)
      
if __name__ == '__main__':
  raise SystemExit(main())

    
