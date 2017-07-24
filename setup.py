from setuptools import setup, find_packages

#print "FUCK: ", find_packages()

packages = [
#  'lib',
  'bes',
  
#  'lib.bes.android',
#  'lib.bes.archive',
#  'lib.bes.common',
#  'lib.bes.debug',
#  'lib.bes.fs',
#  'lib.bes.hardware',
#  'lib.bes.key_value',
#  'lib.bes.match',
#  'lib.bes.net',
#  'lib.bes.network',
#  'lib.bes.python',
#  'lib.bes.system',
#  'lib.bes.test',
#  'lib.bes.text',
#  'lib.bes.thread',
#  'lib.bes.unix',
#  'lib.bes.net.util',
]

package_dir = {
  'bes': 'lib/bes',
  }
setup(
  name = 'bes',
  version = '1.0',
  package_dir = package_dir,
#  packages = find_packages(),
  packages = packages,
#  py_modules = [ 'bes' ],
#  modules = [ 'lib' ],
  zip_safe = True,
  author='Ramiro Estrugo',
  author_email='bes@fateware.com',
  scripts = [ 'bin/bes_archive_tool.py', 'bin/bes_mac_address_cache.py', 'bin/bes_test.py' ],
)
