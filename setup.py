from setuptools import setup, find_packages

setup(
  name = 'bes',
  version = '1.0.0',
  packages = find_packages(),
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
  scripts = [
    'bin/bes_test.py',
    'bin/bes_path.py',
  ],
)
