#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import glob
import os.path as path

from bes.archive.archiver import archiver
from bes.common.check import check
from bes.common.time_util import time_util
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git import git 
from bes.git.git_clone_options import git_clone_options
from bes.git.git_remote import git_remote
from bes.git.git_util import git_util
from bes.python.python_exe import python_exe
from bes.system.execute import execute
from bes.system.os_env import os_env
from bes.version.version_info import version_info

from .egg_error import egg_error
from .egg_options import egg_options

class egg(object):

  @classmethod
  def make_from_git_archive(clazz, root_dir, revision, options = None):
    'Make an egg from a git root_dir.  setup_filename is relative to that root'
    git.check_is_repo(root_dir)
    check.check_string(revision)
    check.check_egg_options(options, allow_none = True)
    
    options = options or egg_options()
    project_name = path.basename(root_dir)
    tmp_archive_filename = temp_file.make_temp_file(delete = not options.debug,
                                                    prefix = '%s.egg.'.format(options.project_name),
                                                    suffix = '.tar.gz')
    if options.debug:
      print('tmp_archive_filename: %s' % (tmp_archive_filename))
    git.archive(root_dir, revision, project_name, tmp_archive_filename, untracked = untracked)
      
    tmp_extract_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print('tmp_extract_dir: %s' % (tmp_extract_dir))
    archiver.extract_all(tmp_archive_filename, tmp_extract_dir, strip_common_ancestor = True)
    return clazz.make_from_local_dir(tmp_extract_dir,
                                     revision,
                                     setup_filename,
                                     address = address,
                                     version_filename = version_filename,
                                     project_name = project_name,
                                     debug = debug,
                                     verbose = verbose)

  @classmethod
  def make_from_local_dir(clazz, local_dir, revision, address = None, options = None):
    'Make an egg from a local directory'
    check.check_string(local_dir)
    check.check_string(revision)
    check.check_egg_options(options, allow_none = True)

    options = options or egg_options()
    project_name = options.project_name or path.basename(local_dir)

    if options.version_filename:
      version_filename_abs = path.join(local_dir, options.version_filename)
      vi = version_info.read_file(version_filename_abs)
      timestamp = time_util.timestamp(delimiter = '-', milliseconds = False)
      vi = vi.change(version = revision,
                     address = address,
                     tag = revision,
                     timestamp = timestamp)
      vi.save_file(version_filename_abs)

    cmd = [ python_exe.default_exe(), options.setup_filename, 'bdist_egg' ]
    env = os_env.clone_current_env(d = { 'PYTHONDONTWRITEBYTECODE': '1' }, allow_override = True)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    execute.execute(cmd,
                    shell = False,
                    cwd = local_dir,
                    env = env,
                    non_blocking = options.verbose)
    eggs = glob.glob('{}/dist/*.egg'.format(local_dir))
    if len(eggs) == 0:
      raise egg_error('no egg got laid:  {} - {}'.format(local_dir, options.setup_filename))
    if len(eggs) > 1:
      raise egg_error('too many eggs got laid (probably downloaded requirements): {} - {}'.format(local_dir,
                                                                                                  options.setup_filename))
    return eggs[0]
  
  @classmethod
  def make_from_address(clazz, address, revision, options = None):
    'Make an egg from a git address'
    check.check_string(address)
    check.check_string(revision)
    check.check_egg_options(options, allow_none = True)
    
    options = options or egg_options()
    clone_options = git_clone_options(branch = revision)
    repo = git_util.clone_to_temp_dir(address, options = clone_options, debug = options.debug)
    remote_info = git_remote.parse(address)
    project_name = options.project_name or remote_info.project
    return clazz.make_from_local_dir(repo.root, revision, address = address, options = options)

  @classmethod
  def unpack(clazz, egg_filename, output_dir):
    if not archiver.is_valid(egg_filename):
      raise egg_error('not a valid egg: ' % (egg_filename))
    file_util.mkdir(output_dir)
    archiver.extract_all(egg_filename, output_dir)
