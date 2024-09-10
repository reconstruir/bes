#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from os import path

from bes.python.pip_project import pip_project
from bes.python.pip_project_options import pip_project_options
from bes.python.python_testing import python_testing
from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_pyinstaller_builder(unit_test):

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def test_build(self):
    tmp_dir = self.make_temp_dir(suffix = '.test_pyinstaller_build', )
    venvs_dir = path.join(tmp_dir, 'venvs')
    print(f'PYTHON: {python_testing._PYTHONS.ANY_PYTHON3}')
    options = pip_project_options(root_dir = venvs_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = pip_project(options = options)
    project.install('pyinstaller', version = '6.10.0')

    program_content = r'''
#!/usr/bin/env python3

import sys

def test_re():
  'Test that re works'
  import re
  C = re.compile('^foo.*$')
  sys.stdout.write('test_re:')

def test_threading():
  'Test that threading works'
  import threading
  def worker():
    sys.stdout.write('test_threading:')
    return

  t = threading.Thread(target = worker)
  t.start()
  t.join()

def test_subprocess():
  'Test that subprocess works'
  import subprocess
  import platform
  if platform.system() == 'Windows':
    args = [ 'cmd', '/c', 'echo test_subprocess:' ]
  else:
    args = [ 'echo', 'test_subprocess:' ]
  p = subprocess.check_output(args)
  sys.stdout.write(p.decode('utf8').strip())

def test_subprocess_with_shell():
  'Test that subprocess with shell = True works'
  import subprocess
  p = subprocess.check_output('echo test_subprocess_with_shell:', shell = True)
  sys.stdout.write(p.decode('utf8').strip())

def test_json_hidden():
  'Test that using a stdlib module like json works by importing it hidden (not explicit)'
  exec('import json', locals(), globals())
  s = json.dumps({'foo': 'hi'})
  sys.stdout.write('test_json_hidden:')

def test_fakelib1():
  'Test that we can use something in a custom import.'
  from fakelib1 import fakelib1
  sys.stdout.write(fakelib1().something)

def test_fakelib2_hidden():
  'Test that using a personal module like fakelib works by importing it hidden (not explicit)'
  exec('from fakelib2 import fakelib2', locals(), globals())
  sys.stdout.write(fakelib2().something)

tests = [
  test_re,
  test_threading,
  test_subprocess,
  test_subprocess_with_shell,
  test_json_hidden,
  test_fakelib1,
  test_fakelib2_hidden,
]

for test in tests:
  test()

#import json
#from fakelib.foo import foo
#f = foo()
#sys.stdout.write(f.something)

sys.stdout.write('\n')
sys.stdout.flush()

raise SystemExit()
'''
    program_source = file_util.save(path.join(tmp_dir, 'program', 'program.py'), content = program_content)

    fakelib1_content = r'''
class fakelib1(object):
  def __init__(self):
    self.something = 'test_fakelib1:'
'''
  
    fakelib2_content = r'''
class fakelib2(object):
  def __init__(self):
    self.something = 'test_fakelib2_hidden:'
'''

    file_util.save(path.join(tmp_dir, 'program', 'fakelib1.py'), content = fakelib1_content)
    file_util.save(path.join(tmp_dir, 'program', 'fakelib2.py'), content = fakelib2_content)

    for p in project.PYTHONPATH:
      sys.path.insert(0, p)

    from bes.pyinstaller.pyinstaller_build import pyinstaller_build
    from bes.pyinstaller.pyinstaller_options import pyinstaller_options
      
    build_dir = path.join(tmp_dir, 'BUILD')
    options = pyinstaller_options(verbose = True,
                                  log_level = 'INFO',
                                  hidden_imports = [ 'json', 'fakelib1', 'fakelib2' ],
                                  build_dir = build_dir,
                                  replace_env = project.env)
    build_result = pyinstaller_build.build(program_source, options = options)
    self.assertTrue( path.exists(build_result.output_exe) )
    rv = execute.execute(build_result.output_exe, raise_error = False)
    self.assertEqual( 0, rv.exit_code )
    expected = 'test_re:test_threading:test_subprocess:test_subprocess_with_shell:test_json_hidden:test_fakelib1:test_fakelib2_hidden:'
    self.assertEqual( expected, rv.stdout.strip() )
    
if __name__ == '__main__':
  unit_test.main()
