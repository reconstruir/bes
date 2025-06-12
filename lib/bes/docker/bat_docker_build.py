#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, re
from os import path

from ..system.check import check
from bes.fs.file_replace import file_replace
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.log import logger

from collections import namedtuple

from .bat_docker_error import bat_docker_error
from .bat_docker_exe import bat_docker_exe
from .bat_docker_images import bat_docker_images
from .bat_docker_tag import bat_docker_tag
from .bat_docker_util import bat_docker_util

class bat_docker_build(object):
  'Class to deal with docker build.'
  
  log = logger('docker')

  _build_result = namedtuple('_build_result', 'exit_code, stdout, image_id')
  @classmethod
  def build(clazz, dockerfile = None, dockerfile_substitutions = None,
            build_args = None, repo_name = None, tag = None, context_files = None,
            context_label = '', debug = False, non_blocking = True):
#    check.check_string(dockerfile, allow_none = True)
#    check.check_dict(dockerfile_substitutions, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
#    check.check_dict(build_args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
#    check.check_string(tag, allow_none = True)
#    check.check_string_seq(context_files, allow_none = True)
#    check.check_string(context_label, allow_none = True)
#    check.check_bool(debug)
#    check.check_bool(non_blocking)

    if tag and not repo_name:
      raise bat_docker_error('If tag is given then repo_name shoudld be given too.')
    
    dockerfile = dockerfile or 'Dockerfile'
    dockerfile_substitutions = dockerfile_substitutions or {}
    build_args = build_args or {}
    context_files = context_files or []
    context_label = context_label or 'docker.build'

    if not path.isfile(dockerfile):
      raise bat_docker_error('Dockerfile not found: "{}"'.format(dockerfile))
    
    tmp_context_dir = temp_file.make_temp_dir(suffix = '-{}'.format(context_label), delete = not debug)
    if debug:
      print('tmp_context_dir={}'.format(tmp_context_dir))

    clazz._copy_context_file(dockerfile, os.getcwd(), tmp_context_dir, substitutions = dockerfile_substitutions)
    
    for cf in context_files:
      clazz._copy_context_file(cf, os.getcwd(), tmp_context_dir)

    build_args_args = []
    for key, value in build_args.items():
      build_args_args.append('--build-arg')
      build_args_args.append('{}={}'.format(key, value))
      
    bat_docker_build_args = [ 'build' ]
    bat_docker_build_args.extend(build_args_args)
    bat_docker_build_args.extend([ '--file', dockerfile ])
    bat_docker_build_args.append('.')

    if repo_name:
      named_tag = bat_docker_util.make_tagged_image_name(repo_name, tag)
    else:
      named_tag = None
    
    old_checksum = None
    if named_tag:
      try:
        old_checksum = bat_docker_images.inspect_checksum(named_tag)
      except bat_docker_error as ex:
        pass

    rv = bat_docker_exe.call_docker(bat_docker_build_args, cwd = tmp_context_dir, non_blocking = non_blocking)
    if rv.exit_code == 0:
      image_id = clazz._parse_build_result(rv.stdout)
      if named_tag:
        new_checksum = bat_docker_images.inspect_checksum(image_id)
        if new_checksum != old_checksum:
          bat_docker_tag.tag_image(image_id, repo_name, tag or 'latest')
    else:
      image_id = None
    file_util.remove(tmp_context_dir)
    return clazz._build_result(rv.exit_code, rv.stdout, image_id)

  @classmethod
  def _parse_build_result(clazz, text):
    lines = bat_docker_util.parse_lines(text)
    for line in reversed(lines):
      instance_id = clazz._parse_successfully_built_line(line)
      if instance_id:
        return instance_id
    raise bat_docker_error('failed to parse successfully built status')

  @classmethod
  def _parse_successfully_built_line(clazz, line):
    f = re.findall(r'^Successfully\s+built\s+(.+)$', line)
    if not f:
      return None
    assert len(f) == 1
    return f[0]

  @classmethod
  def _copy_context_file(clazz, filename, src_dir, dst_dir, substitutions = None):
    substitutions = substitutions or {}
    src_file = path.join(src_dir, filename)
    dst_file = clazz._make_dst_file(dst_dir, filename)
    if not path.isfile(src_file):
      raise bat_docker_error('context file not found: "{}"'.format(src_file))
    if substitutions:
      file_replace.copy_with_substitute(src_file, dst_file, substitutions, backup = False)
    else:
      file_util.copy(src_file, dst_file)

  @classmethod
  def _make_dst_file(clazz, dst_dir, filename):
    return path.join(dst_dir, clazz._fix_relative_file(filename))

  @classmethod
  def _fix_relative_file(clazz, filename):
    while filename.startswith('../'):
      filename = filename[3:]
    return filename
