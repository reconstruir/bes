# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, time
from datetime import datetime
from collections import namedtuple

from bes.common.check import check
from bes.system.log import logger
from bes.system.env_override import env_override
from bes.fs.temp_file import temp_file

from .git_download_options import git_download_options
from .git_error import git_error
from .git_remote import git_remote
from .git_repo import git_repo

class git_download(object):
  'A class to deal with downloading revision tarballs wholesale.'

  _log = logger('git_download')

  @classmethod
  def download(clazz, address, revision, output_filename = None,
               base_name = None, download_options = None):
    'git archive with additional support to include untracked files for local repos.'
    check.check_string(address)
    check.check_string(revision)
    check.check_string(base_name, allow_none = True)
    check.check_string(output_filename, allow_none = True)

    download_options = download_options or git_download_options()
    
    clazz._log.log_method_d()
    name = clazz._address_name(address)
    if not base_name:
      base_name = '{}-{}'.format(name, revision)

    if not output_filename:
      output_filename = '{}.tar.gz'.format(base_name)

    clazz._log.log_d('name={} base_name={} output_filename={}'.format(name,
                                                                      base_name,
                                                                      output_filename))
    download_options = download_options or git_download_options()
    clazz._do_download(address, revision, output_filename, base_name, download_options)

  @classmethod
  def _do_download(clazz, address, revision, output_filename,
                   base_name, download_options):
    tmp_root_dir = temp_file.make_temp_dir(delete = not download_options.debug)
    repo = git_repo(tmp_root_dir, address = address)
    repo.clone(options = download_options)
    repo.archive_to_file(base_name, revision, output_filename, archive_format = 'tgz')
    return output_filename

  @classmethod
  def _do_download_with_temp_ssh(clazz, address, revision, output_filename,
                                 base_name, download_options):
    with env_override.temp_home() as env:
      clazz._do_download(address, revision, output_filename, base_name, download_options)
  
  @classmethod
  def _address_name(clazz, address):
    p = git_remote.parse(address)
    return p.project
    
