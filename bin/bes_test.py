#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# A script to run python unit tests.  Depends on bes which as bit of a chicken-and-egg
# problem when unit testing bes itself.  Use the standalone bes_test version to avoid
# the issue.
# FOO
import argparse, copy, math, os, os.path as path, subprocess, sys
import time, tempfile
from collections import namedtuple

from bes.testing.framework import argument_resolver, printer
from bes.version import version_info
from bes.system import env_var, os_env
from bes.git import git
from bes.fs import file_find, file_util
from bes.egg import egg

# TODO:
#  - figure out how to stop on first failure within one module
#  - https://stackoverflow.com/questions/6813837/stop-testsuite-if-a-testcase-find-an-error
# - cleanup egg dropping

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
  parser.add_argument('--root-dir',
                      action = 'store',
                      default = None,
                      help = 'The root directory for all your projets.  By default its computed from your git struture.  [ None ]')
  parser.add_argument('--dont-hack-env',
                      action = 'store_true',
                      default = False,
                      help = 'Dont hack PATH and PYTHONPATH. [ False ]')
  args = parser.parse_args()
  
  cwd = os.getcwd()

  if args.version:
    import bes
    print(version_info.version_info_for_module(bes).version_string(delimiter = ' '))
    return 0
  
  if not args.files:
    args.files = [ cwd ]

  ar = argument_resolver(cwd, args.files, root_dir = args.root_dir, file_ignore_filename = '.bes_test_ignore')
  ar.num_iterations = args.iterations
  ar.randomize = args.randomize

  ar.ignore_with_patterns(args.ignore)

  if not ar.resolved_files:
    return 1

  if args.print_files:
    ar.print_files()
    return 0

  # Start with a clean environment so unit testing can be deterministic and not subject
  # to whatever the user happened to have exported.  PYTHONPATH and PATH for dependencies
  # are set below by iterating the configs 
  if args.dont_hack_env:
    keep_keys = [ 'PATH', 'PYTHONPATH' ]
  else:
    keep_keys = None
    
  env = os_env.make_clean_env(keep_keys = keep_keys)
  env['PYTHONDONTWRITEBYTECODE'] = 'x'
  
  deps = ar.dependencies()
  configs = ar.configs(deps)
  variables = {
    'rebuild_dir': path.expanduser('~/.rebuild'),
  }
  if not args.dont_hack_env:
    for c in configs:
      substituted = c.substitute(variables)
      env_var(env, 'PATH').append(substituted.data.unixpath)
      env_var(env, 'PYTHONPATH').append(substituted.data.pythonpath)
    
  num_passed = 0
  num_failed = 0
  num_executed = 0
  num_tests = len(ar.resolved_files)
  failed_tests = []

  # Remove current dir from sys.path to avoid side effects
  if cwd in sys.path:
    sys.path.remove(cwd)

  if args.egg:
    setup_dot_py = path.join(cwd, 'setup.py')
    if not path.isfile(setup_dot_py):
      raise RuntimeError('No setup.py found in %s to make the egg.' % (cwd))
    egg_zip = egg.make(setup_dot_py)
    p = env_var(env, 'PYTHONPATH')
    p.remove(cwd)
    p.prepend(egg_zip)
    if args.save_egg:
      file_util.copy(egg_zip, path.join(cwd, path.basename(egg_zip)))

  if args.check_pre_commit:
    missing_from_git = []
    for finfo in ar.resolved_files:
      filename = finfo.filename
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

  if not args.dry_run and args.page:
    printer.OUTPUT = tempfile.NamedTemporaryFile(prefix = 'bes_test', delete = True, mode = 'w')

  total_tests = _count_tests(ar.inspect_map, ar.resolved_files)
  total_files = len(ar.resolved_files)

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
  for i, test_desc in enumerate(ar.resolved_files):
    file_info = test_desc.file_info
    filename = file_info.filename
    if not filename in timings:
      timings[filename] = []
    for python_exe in args.python:
      result = _test_execute(python_exe, ar.inspect_map, filename, test_desc.tests, options, i + 1, total_files, cwd, env)
      timings[filename].append(result.elapsed_time)
      total_num_tests += result.num_tests_run
      num_executed += 1
      if result.success:
        num_passed += 1
      else:
        num_failed += 1
        failed_tests.append(( python_exe, filename ))
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
    for python_exe, filename in failed_tests:
      if len(options.interpreters) > 1:
        python_exe_blurb = path.basename(python_exe).rjust(longest_python_exe)
      else:
        python_exe_blurb = ''
      printer.writeln_name('FAILED: %s %s' % (python_exe_blurb, file_util.remove_head(filename, cwd)))

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

def _test_execute(python_exe, test_map, filename, tests, options, index, total_files, cwd, env):
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

    env = copy.deepcopy(env)
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
    total += len(test_map[test.file_info.filename])
  return total
  
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

def _python_exe_blurb(python_exe, interpreters):
  if len(interpreters) <= 1:
    return ''
  longest_python_exe = max([len(path.basename(p)) for p in options.interpreters])
  return path.basename(python_exe).rjust(longest_python_exe)
      
if __name__ == '__main__':
  raise SystemExit(main())

    
