#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
import subprocess

from collections import namedtuple

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.log import logger

class python_script(object):
  'Class to deal with the running pythong scripts.'

  _log = logger('python_script')

  _run_script_result = namedtuple('_run_script_result', 'exit_code, output')
  @classmethod
  def run_script(clazz, exe, script, args = None):
    'Run the script and return the result.'
    check.check_string(exe)
    check.check_string(script)
    check.check_string_seq(args, allow_none = True)

    args = list(args or [])
    tmp_script = temp_file.make_temp_file(content = script, suffix = '.py')
    cmd = [ exe, tmp_script ] + args
    clazz._log.log_d('run_script: exe={} cmd={}'.format(exe, cmd))
    clazz._log.log_d('run_script: script=\n{}\n'.format(script))

    try:
      output_bytes = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
      exit_code = 0
      clazz._log.log_d('run_script: success')
    except subprocess.CalledProcessError as ex:
      clazz._log.log_d('run_script: caught: {}'.format(str(ex)))
      output_bytes = ex.output
      exit_code = ex.returncode
      clazz._log.log_d('run_script: failed')
    finally:
      file_util.remove(tmp_script)
    output = codecs.decode(output_bytes, 'utf-8').strip()
    clazz._log.log_d('run_script: exit_code={} output="{}"')
    return clazz._run_script_result(exit_code, output)
    
  @classmethod
  def sys_executable(clazz, exe):
    'Return the value of sys.executable for the given python executable'
    check.check_string(exe)

    script = r'''\
import sys
assert len(sys.argv) == 2
_filename = sys.argv[1]
with open(_filename, 'w') as f:
  f.write(sys.executable)
raise SystemExit(0)
'''
    tmp_output = temp_file.make_temp_file()
    clazz.run_script(exe, script, [ tmp_output ])
    return file_util.read(tmp_output, codec = 'utf-8').strip()

  @classmethod
  def site_packages_path(clazz, exe):
    'Return a list of paths needed for the site-packages of the given python'
    check.check_string(exe)

    script = r'''\
import site
for p in site.getsitepackages():
  print(p)
raise SystemExit(0)
'''
    rv = clazz.run_script(exe, script)
    lines = [ line for line in rv.output.splitlines() if line ]
    return lines
