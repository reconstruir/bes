#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, re
from os import path

from ..system.check import check
from bes.system.log import logger
from bes.fs.temp_file import temp_file
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.system.command_line import command_line
from bes.fs.file_replace import file_replace

from collections import namedtuple

from .bat_docker_exe import bat_docker_exe
from .bat_docker_error import bat_docker_error
from .bat_docker_util import bat_docker_util
from .bat_docker_container import bat_docker_container

class bat_docker_run(object):
  'Class to deal with docker run.'
  
  log = logger('docker')
  
  _run_result = namedtuple('_run_result', 'container_id, exit_code, stdout, input_dir, output_dir')
  @classmethod
  def run(clazz, image_id, command, run_files = None, run_files_substitutions = None,
          run_label = None, volumes = None, env = None, name = None, restart = False,
          detach = False, tty = False, interactive = False, expose = None, debug = False,
          non_blocking = True, remove = True, tmp_dir = None):
    check.check_string(image_id)
    check.check_string(command)
    check.check_string_seq(run_files, allow_none = True)
    check.check_dict(run_files_substitutions, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_string(run_label, allow_none = True)
    check.check_string(name, allow_none = True)
    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_dict(volumes, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_bool(restart)
    check.check_bool(detach)
    check.check_bool(tty)
    check.check_bool(interactive)
    check.check_int(expose, allow_none = True)
    check.check_bool(debug)
    check.check_bool(non_blocking)
    check.check_bool(remove)
    check.check_string(tmp_dir, allow_none = True)

    cli = command_line.parse_args(command)
    
    env = env or {}
    volumes = volumes or {}
    command_args = cli[1:]
    run_files = run_files or []
    run_files_substitutions = run_files_substitutions or {}
    run_label = run_label or 'docker.run'
    tmp_dir = tmp_dir or os.getcwd()
    
    tmp_run_dir = temp_file.make_temp_dir(suffix = '-{}'.format(run_label), dir = tmp_dir, delete = not debug)

    input_dir = path.join(tmp_run_dir, 'input')
    output_dir = path.join(tmp_run_dir, 'output')

    for cf in run_files:
      src_file = path.join(os.getcwd(), cf)
      dst_file = path.join(input_dir, cf)
      if not path.isfile(src_file):
        raise bat_docker_error('run file not found: "{}"'.format(src_file))
      if run_files_substitutions and file_mime.is_text(src_file):
        file_replace.copy_with_substitute(src_file, dst_file, run_files_substitutions, backup = False)
      else:
        file_util.copy(src_file, dst_file)
    
    bat_docker_run_args = [ 'run' ]
    if detach:
      bat_docker_run_args.append('--detach')
    if tty:
      bat_docker_run_args.append('--tty')
    if interactive:
      bat_docker_run_args.append('--interactive')
    if remove:
      bat_docker_run_args.append('--rm')
    bat_docker_run_args.extend(clazz._make_env_args(env))
    volumes[input_dir] = '/input'
    volumes[output_dir] = '/output'
    bat_docker_run_args.extend(clazz._make_volume_args(volumes))
    if expose:
      bat_docker_run_args.extend([ '--expose', str(expose) ])
    if restart:
      bat_docker_run_args.extend([ '--restart', restart ])
    if name:
      bat_docker_run_args.extend([ '--name', name ])
    bat_docker_run_args.append(image_id)
    bat_docker_run_args.append(cli[0])
    bat_docker_run_args.extend(cli[1:])
    clazz.log.log_d('running docker: {}'.format(' '.join(bat_docker_run_args)))
    rv = bat_docker_exe.call_docker(bat_docker_run_args, non_blocking = non_blocking)
    container_id = bat_docker_container.last_container()
    return clazz._run_result(container_id, rv.exit_code, rv.stdout, input_dir, output_dir)

  @classmethod
  def _make_env_args(self, env):
    env_args = []
    for key, value in env.items():
      env_args.append('--env')
      env_args.append('{}={}'.format(key, value))
    return env_args

  @classmethod
  def _make_volume_args(self, env):
    env_args = []
    for key, value in env.items():
      env_args.append('--volume')
      env_args.append('{}:{}'.format(key, value))
    return env_args
  
