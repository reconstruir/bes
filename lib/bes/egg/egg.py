#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, glob, os, os.path as path, shutil, tempfile
from bes.archive.archiver import archiver
from bes.system.execute import execute
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git import git 

class egg(object):

  @classmethod
  def make(clazz, root_dir, revision, setup_filename, untracked = False, debug = False):
    'Make an egg from a git root_dir.  setup_filename is relative to that root'
    git.check_is_repo(root_dir)
    base_name = path.basename(root_dir)
    tmp_archive_filename = temp_file.make_temp_file(delete = not debug,
                                                    prefix = '%s.egg.' % (base_name),
                                                    suffix = '.tar.gz')
    if debug:
      print('tmp_archive_filename: %s' % (tmp_archive_filename))
    git.archive(root_dir, revision, base_name, tmp_archive_filename, untracked = untracked)
      
    tmp_extract_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print('tmp_extract_dir: %s' % (tmp_extract_dir))
    archiver.extract_all(tmp_archive_filename, tmp_extract_dir, strip_common_ancestor = True)

    cmd = [ 'python', setup_filename, 'bdist_egg' ]
    env = copy.deepcopy(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    #print('cmd=%s; cwd=%s; evn=%s' % (cmd, tmp_extract_dir, env))
    execute.execute(cmd, shell = False, cwd = tmp_extract_dir, env = env, non_blocking = debug)
    eggs = glob.glob('%s/dist/*.egg' % (tmp_extract_dir))
    if len(eggs) == 0:
      raise RuntimeError('no egg got laid: %s - %s' % (root_dir, setup_filename))
    if len(eggs) > 1:
      raise RuntimeError('too many eggs got laid (probably downloaded requirements): %s - %s' % (root_dir, setup_filename))
    return eggs[0]

  @classmethod
  def unpack(clazz, egg_filename, output_dir):
    if not archiver.is_valid(egg_filename):
      raise RuntimeError('not a valid egg: ' % (egg_filename))
    file_util.mkdir(output_dir)
    archiver.extract_all(egg_filename, output_dir)
