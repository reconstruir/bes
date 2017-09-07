from setuptools import setup, find_packages
import os, subprocess

_WANT_TESTS = bool(os.environ.get('BES_EGG_INCLUDE_TESTS', None))

def _find_tests(d):
  cmd = [ 'find', d, '-name', 'test_*.py' ]
  result = subprocess.check_output(cmd, shell = False)
  tests = [ test.strip() for test in result.strip().split('\n') if test.strip() ]
  tests = [ test[len(d)+1:] for test in tests ]
  return sorted(tests)

def find_tests(d):
  if not _WANT_TESTS:
    return []
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
