from setuptools import setup, find_packages

import fnmatch, os, subprocess

_WANT_TESTS = bool(os.environ.get('BES_EGG_INCLUDE_TESTS', None))

def _find_tests(d):
  cmd = [ 'find', d, '-type', 'f' ]
  print "CMD: ", cmd
  rv = subprocess.check_output(cmd, shell = False)
  print "RV: ", rv
  files = [ f.strip() for f in rv.split('\n') if f.strip() ]
  result = []
  for f in files:
    print "FILE: ", f
  for f in files:
    if fnmatch.fnmatch(f, '*/tests/test_*.py*') or fnmatch.fnmatch(f, '*/test_data/*'):
      result.append(f)
  tests = [ f[len(d)+1:] for f in result ]
  return sorted(tests)

def find_tests(d):
  if not _WANT_TESTS:
    return []
  for x in _find_tests(d):
    print "CACA: ", x
  return _find_tests(d)

setup(
  name = 'bes',
  version = '1.0.0',
  packages = find_packages(include = ['bes*']),
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
  include_package_data = True,
  package_data = {
    'bes': find_tests('bes'),
  },
  scripts = [
    'bin/bes_test.py',
    'bin/bes_path.py',
  ],
)
