#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import tempfile, shutil, subprocess

class egg_maker(object):

  @classmethod
  def make(clazz, setup_dot_py):
    assert path.isfile(setup_dot_py)
    temp_dir = tempfile.mkdtemp()
    src_dir = path.dirname(setup_dot_py)
    shutil.rmtree(temp_dir)
    shutil.copytree(src_dir, temp_dir, symlinks = True)
    cmd = [ 'python', 'setup.py', 'bdist_egg' ]
    subprocess.check_output(cmd, shell = False, cwd = temp_dir)
    eggs = glob.glob('%s/dist/*.egg' % (temp_dir))
    assert len(eggs) == 1
    return eggs[0]
