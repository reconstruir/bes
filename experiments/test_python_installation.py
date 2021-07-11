from bes.python.python_installation_v2 import python_installation_v2
from bes.pip.pip_project_v2 import pip_project_v2
from bes.fs.file_util import file_util

pe = '/usr/local/opt/python@3.7/bin/python3.7'
pe = '/usr/local/opt/python@3.8/bin/python3.8'
pe = '/usr/local/opt/python@3.9/bin/python3.9'
#pe = '/usr/bin/python2.7'
#pe = '/usr/bin/python3'

file_util.remove('PROJECTS')

pp = pip_project_v2('bar', 'PROJECTS', pe)
pp.install('macholib')

#pp.install('pyinstaller')
#print('   pip_exe: {}'.format(pp.pip_exe))
#print('python_exe: {}'.format(pp.python_exe))
#print('      PATH: {}'.format(pp.PATH))
#print('PYTHONPATH: {}'.format(pp.PYTHONPATH))
