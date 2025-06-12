#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os
from os import path

from ..system.check import check
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.script.blurb import blurb
from bes.system.env_var import os_env_var
from bes.system.execute import execute
from bes.system.which import which
from bes.system.log import logger
from bes.git.git_repo import git_repo

from bes.docker_image_maker.dim_ecr import dim_ecr
from bes.docker_image_maker.dim_python import dim_python
from bes.docker_image_maker.dim_step import dim_step
from bes.docker_image_maker.dim_system import dim_system
from bes.docker_image_maker.dim_task_descriptor import dim_task_descriptor
from bes.docker_image_maker.dim_task_failed_entry import dim_task_failed_entry
from bes.docker_image_maker.dim_task_options import dim_task_options
from bes.docker_image_maker.dim_task_processor import dim_task_processor
from bes.docker_image_maker.dim_task_result import dim_task_result
from bes.docker_image_maker.dim_task_run_result import dim_task_run_result

from bes.docker.bat_docker_images import bat_docker_images
from bes.docker.bat_docker_error import bat_docker_error

from bes.aws.aws_ecr import aws_ecr

class dim_build_cli(object):

  def __init__(self, root_dir):
    
    blurb.add_blurb(self, 'build')
    self._root_dir = root_dir
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('--python', action = 'append', default = [],
                             dest = 'python_versions', choices = dim_python.PYTHON_VERSIONS,
                             help = 'Python version to build for.  Multiple --python flags can be given [ {} ]'.format(dim_python.DEFAULT_PYTHON_VERSION))
    self.parser.add_argument('-s', '--system', action = 'append', default = [],
                             dest = 'systems', choices = dim_system.CLI_CHOICES,
                             help = 'System to build for.  Multiple --system flags can be given [ {} ]'.format(' '.join(dim_system.CLI_CHOICES)))
    self.parser.add_argument('-i', '--image', action = 'append', default = [],
                             dest = 'steps', choices = dim_step.STEP_NAMES,
                             help = 'Image to build.  Multiple --image flags can be given [ {} ]'.format(' '.join(dim_step.STEP_NAMES)))
    self.parser.add_argument('-b', '--build', action = 'store_true', default = False,
                             help = 'Whether to build the image [ False ]')
    self.parser.add_argument('-t', '--test', action = 'store_true', default = False,
                             help = 'Test the resulting image [ False ]')
    self.parser.add_argument('--publish-egoist', action = 'store_true', default = False,
                             help = 'Whether to publish the resulting egoist [ False ]')
    self.parser.add_argument('--publish-image', action = 'store_true', default = False,
                             help = 'Whether to publish the resulting docker image [ False ]')
    self.parser.add_argument('-f', '--follow', action = 'store_true', default = False,
                             help = 'Follow the log of a build or test [ False ]')
    self.parser.add_argument('-l', '--log', action = 'store_true', default = False,
                             help = 'Print the log right away when a failure happens [ False ]')
    self.parser.add_argument('-v', '--verbose', action = 'store_true', default = False,
                             help = 'Verbose output [ False ]')
    self.parser.add_argument('--clean', action = 'store_true', default = False,
                             help = 'Cleanup docker processes and images [ False ]')
    self.parser.add_argument('--very-clean', action = 'store_true', default = False,
                             help = 'Cleanup docker processes and images and *all* image maker images too [ False ]')
    self.parser.add_argument('--no-pull', action = 'store_true', default = False,
                             help = 'Do not pull any docker images.  Build everything locally. [ False ]')
    self.parser.add_argument('--print-ecr-images', action = 'store_true', default = False,
                             help = 'Print all the image maker images in ecr. [ False ]')
    self.parser.add_argument('--version', action = 'store', default = None,
                             dest = 'bes_version',
                             help = 'The version of bes to build. [ None ]')
    self.parser.add_argument('more_args', action = 'store', default = [], nargs = '*',
                             help = 'Args for the script. [ None ]')

  def run(self):
    args = self.parser.parse_args()
    blurb.set_verbose(args.verbose)
    args.python_versions = dim_python.resolve_python_versions(args.python_versions)
    args.systems = dim_system.resolve_systems(args.systems)
    args.steps = dim_step.resolve_steps(args.steps)
    self.logs_dir = path.join(os.getcwd(), 'BUILD', 'logs')
    self.egoist = self._find_egoist()
    self.temp_dir = temp_file.make_temp_dir(suffix = 'build')
    self.repo = git_repo('.', find_root = True)

    if args.print_ecr_images:
      self._print_ecr_images()
      return 0

    self.bes_version = args.bes_version or self.repo.greatest_remote_tag()
      
    self.blurb('                 steps: {}'.format(' '.join(args.steps)))
    self.blurb('               systems: {}'.format(' '.join(args.systems)))
    self.blurb('       python_versions: {}'.format(' '.join(args.python_versions)))
    self.blurb('                 build: {}'.format(args.build))
    self.blurb('                  test: {}'.format(args.test))
    self.blurb('        publish_egoist: {}'.format(args.publish_egoist))
    self.blurb('         publish_image: {}'.format(args.publish_image))
    self.blurb('                 clean: {}'.format(args.clean))
    self.blurb('            very_clean: {}'.format(args.very_clean))
    self.blurb('bes_version: {}'.format(self.bes_version))

    if args.clean and args.very_clean:
      self.blurb('Only one of --clean or --very-clean should be given.')
      return 1

    if args.clean:
      self._clean()
      return 0

    if args.very_clean:
      self._very_clean()
      return 0

    result = self._do_run(args)
    if result.success:
      self.blurb('SUCCESS')
      return 0

    for failed_entry in result.failed_entries:
      self.blurb('FAILED: {} => {}'.format(failed_entry.descriptor.bat_docker_tag,
                                           failed_entry.log))
    return 1

  def _do_run(self, args):
    failed_entries = []

    processor = dim_task_processor()
    descriptors = self._make_descriptors(self._task_build, args)
    results = processor.run(descriptors)
    
    for result in results:
      if not result.success:
        failed_entry = dim_task_failed_entry(result.descriptor,
                                             result.log_relative)
        failed_entries.append(failed_entry)

    self._cleanup()
        
    return dim_task_run_result(len(failed_entries) == 0, failed_entries)

  def _cleanup(self):
    cmd = [
      self.egoist,
      'docker',
      'cleanup',
      '--running-containers',
      '--exited-containers',
      '--untagged-images',
    ]
    self.blurb('cleanup')
    rv = execute.execute(cmd, raise_error = False,
                         non_blocking = False,
                         stderr_to_stdout = True,
                         cwd = os.getcwd())

  def _clean(self):
    self._cleanup()
    
  def _very_clean(self):
    self._cleanup()
    self._docker_remove_image('builder-cacerts')
    images = bat_docker_images.list_images()
    for image in images:
      repo = image.repository
      if repo is not None and self._repo_should_be_cleaned_up(image.repository):
        self._docker_remove_image(image.image_id)

  def _print_ecr_images(self):
    repos = aws_ecr.list_repos()
    image_maker_repos = [ repo for repo in repos if repo.name.startswith(dim_ecr.REPO_NAME_PREFIX) ]
    images = []
    for repo in image_maker_repos:
      next_images = aws_ecr.list_images(repo.name)
      images.extend(next_images)

    tagged_images = []
    for image in images: #, key = lambda image: image.name
      for tag in image.tags:
        tagged_images.append('{}:{}'.format(image.repo_name, tag))
    for image in sorted(tagged_images):
      print(image)

  def _repo_should_be_cleaned_up(self, repo_name):
    prefixes = [
      'ego_cicd',
      'ego-cicd',
      '407733091588.dkr.ecr.us-west-2.amazonaws.com/ego-cicd',
    ]
    for prefix in prefixes:
      if repo_name.startswith(prefix):
        return True
    return False
      
  def _docker_remove_image(self, image):
    try:
      info = bat_docker_images.inspect(image)
      bat_docker_images.remove(image, force = True)
    except bat_docker_error as ex:
      pass
           
  @classmethod
  def _make_descriptors(clazz, function, args):
    result = []
    options = dim_task_options()
    options.verbose = args.verbose
    options.follow = args.follow
    options.log = args.log
    options.more_args = args.more_args
    options.test = args.test
    options.build = args.build
    options.publish_egoist = args.publish_egoist
    options.publish_image = args.publish_image
    options.no_pull = args.no_pull
    
    for system in args.systems:
      for step in args.steps:
        for python_version in args.python_versions:
          descriptor = dim_task_descriptor(function, step, system, python_version, options)
          result.append(descriptor)
    return result
  
  def _resolve_systems(self, systems):
    result = []
    for system in systems:
      if system == 'all':
        result.extend(dim_system.VERSIONED_SYSTEMS)
      elif system == 'exp':
        result.extend(dim_system.EXPERIMENTAL_VERSIONED_SYSTEMS)
      elif system == 'allexp':
        result.extend(dim_system.ALL_VERSIONED_SYSTEMS)
      elif system in dim_system.SYSTEM_NAMES:
        for possible_system in dim_system.ALL_VERSIONED_SYSTEMS:
          if possible_system.startswith(system):
            result.append(possible_system)
      else:
        result.append(system)
    return tuple(set(result))
  
  def _task_build(self, descriptor):
    check.check_dim_task_descriptor(descriptor)

    build_script = self._find_script(descriptor.step_name)
    script_args = descriptor.script_args
    bes_version_args = [ 'bes_version={}'.format(self.bes_version) ]
    log = path.join(self.logs_dir, descriptor.log_filename())
    cmd = [ self.egoist, 'script', 'run', build_script, descriptor.system ] + script_args + bes_version_args
    self.blurb('building {} => {}'.format(descriptor.bat_docker_tag, path.relpath(log)))
    rv = execute.execute(cmd, raise_error = False,
                         non_blocking = descriptor.options.follow,
                         stderr_to_stdout = True,
                         cwd = os.getcwd())
    file_util.save(log, content = rv.stdout)
    success = rv.exit_code == 0
    if not success and not descriptor.options.follow and descriptor.options.log:
      print(rv.stdout)
    return dim_task_result(success, log, descriptor)

  @classmethod
  def _find_egoist(clazz):
    v = os_env_var('EGOIST')
    if v.is_set:
      if not path.exists(v.value):
        raise RuntimeError('${EGOIST} not found: {}'.format(v.value))
      if not file_path.is_executable(v.value):
        raise RuntimeError('${EGOIST} not an executable: {}'.format(v.value))
      return v.value
    for possible_egoist in [ 'egoist', 'egoist2.py', 'egoist3.py' ]:
      egoist = which.which(possible_egoist, raise_error = False)
      if egoist:
        return egoist
    raise RuntimeError('egoist not found in either the environment or PATH.')

  def _find_script(self, step_name):
    assert step_name in dim_step.STEP_NAMES
    script_filename = 'egoist_step_{}.py'.format(step_name)
    script_path = path.abspath(path.join(self._root_dir, 'steps', step_name, script_filename))
    if not path.isfile(script_path):
      raise RuntimeError('script not found: {}'.format(script_filename))
    return script_path
      
  @classmethod
  def main(clazz, root_dir):
    return dim_build_cli(root_dir).run()
