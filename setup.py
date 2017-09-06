from setuptools import setup, find_packages

print "caca"

def find_tests():
  return [ 'bes/common/tests/test_string_util.py' ]

setup(
  name = 'bes',
  version = '1.0.0',
  packages = find_packages(include = ['bes*']),
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
#  include_package_data = True,
#  package_data = {
#    '': ['test_*.py'],
#  },
  scripts = [
    'bin/bes_test.py',
    'bin/bes_path.py',
  ],
)
