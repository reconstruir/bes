from setuptools import setup, find_packages

setup(
  name = 'bes',
  version = '1.0',
  packages = find_packages(),
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
  scripts = [ 'bin/bes_archive_tool.py', 'bin/bes_mac_address_cache.py', 'bin/bes_test.py' ],
)
