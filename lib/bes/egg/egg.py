#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, glob, os, os.path as path, shutil, tempfile
from bes.archive import archiver
from bes.system import execute
from bes.fs import file_util

class egg(object):

  @classmethod
  def make(clazz, setup_filename):
    assert path.isfile(setup_filename)
    temp_dir = tempfile.mkdtemp()
    src_dir = path.dirname(setup_filename)
    assert path.isdir(src_dir)
    shutil.rmtree(temp_dir)
    shutil.copytree(src_dir, temp_dir, symlinks = True)
    cmd = [ 'python', path.basename(setup_filename), 'bdist_egg' ]
    env = copy.deepcopy(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    execute.execute(cmd, shell = False, cwd = temp_dir, env = env)
    eggs = glob.glob('%s/dist/*.egg' % (temp_dir))
    assert len(eggs) == 1
    return eggs[0]

  @classmethod
  def unpack(clazz, egg_filename, output_dir):
    if not archiver.is_valid(egg_filename):
      raise RuntimeError('not a valid egg: ' % (egg_filename))
    file_util.mkdir(output_dir)
    archiver.extract(egg_filename, output_dir)
