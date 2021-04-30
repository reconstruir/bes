#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import re

from bes.common.check import check
from bes.compat import url_compat
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.host import host
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser
from bes.url.url_util import url_util

from .python_error import python_error
from .python_source import python_source
from .python_version import python_version
from .python_version_list import python_version_list

class python_python_dot_org(object):
  'Class to deal with python.org listings and downloads'

  _log = logger('python_dot_org')
  
  @classmethod
  def available_versions(clazz, system, num):
    'Return a list of python versions available to install.'
    check.check_string(system)
    check.check_int(num)

    all_possible_versions = clazz._all_possible_versions(system)
    clazz._log.log_d('available_versions: system={} all_possible_versions={}'.format(system, all_possible_versions.to_string()))
    
    if not num:
      result = all_possible_versions
    else:
      result = all_possible_versions.make_availability_list(num)
    clazz._log.log_d('available_versions: result={}'.format(all_possible_versions.to_string()))

    return result

  # theres no point showing obsolete (and sometimes dangerous) versions
  _MIN_PYTHON2_VERSION = '2.7'
  _MIN_PYTHON3_VERSION = '3.7'

  @classmethod
  def _should_include_version(clazz, full_version):
    check.check_python_version(full_version)
    
    'Return True if the given python version is one we want to expose'
    # python2: any 2.7
    if full_version >= '2.7.0' and full_version < '3.0.0':
      return True
    # python3: 3.7 and greater
    if full_version >= '3.7.0' and full_version < '4.0.0':
      return True
    return False
  
  @classmethod
  def _all_possible_versions(clazz, system):
    '''
    Return a list of all possible versions according to the python.org index for 
    a union of all platforms.
    Some of these dont exist for some platforms so you need to call _filter_versions()
    to get a valid list.
    '''
    check.check_string(system)
    
    index = clazz._download_available_index()
    possible = [ v for v in index if clazz._should_include_version(v) ]
    clazz._log.log_d('_all_possible_versions: system={} possible={}'.format(system, possible))
    existing = [ v for v in possible if clazz.find_package_url(system, v) != None ]
    clazz._log.log_d('_all_possible_versions: system={} existing={}'.format(system, existing))
    result = python_version_list(existing)
    result.sort()
    return result

  _BASE_URL = 'https://www.python.org/ftp/python/'
  @classmethod
  def possible_package_urls(clazz, system, full_version):
    'Return the package url for a specific version of python for system.'
    check.check_python_version(full_version)

    source = python_source.find_impl(system)
    filenames = source.possible_python_dot_org_installer_filenames(full_version)
    return [ url_compat.urljoin(clazz._BASE_URL, f) for f in filenames ]

  @classmethod
  def find_package_url(clazz, system, full_version):
    '''
    Return True if the package for full version exists for system.
    Sometimes python.org has versions in the index that dont exist
    for some platforms.
    '''
    check.check_string(system)
    check.check_python_version(full_version)

    urls = clazz.possible_package_urls(system, full_version)
    result = None
    for url in urls:
      exists = url_util.exists(url)
      clazz._log.log_d('find_package_url: url={} exists={}'.format(url, exists))
      if exists:
        result = url
        break
    clazz._log.log_d('find_package_url: full_version={} result={}'.format(full_version, result))
    return result
  
  @classmethod
  def _downlod_url(clazz, url, debug = False):
    if not url_util.exists(url):
      raise python_error('No python.org package found: "{}"'.format(url))
    tmp_dir = temp_file.make_temp_dir(suffix = '-python-download')
    basename = path.basename(url)
    tmp_package = path.join(tmp_dir, basename)
    url_util.download_to_file(url, tmp_package)
    return tmp_package

  @classmethod
  def download_package(clazz, system, full_version, debug = False):
    'Download the major.minor.revision full version of python to a temporary file.'
    url = clazz.possible_package_urls(system, full_version)
    return clazz._downlod_url(url, debug = False)
  
  @classmethod
  def _download_available_index(clazz):
    'Download and parse the available python version index.'

    response = url_util.get('https://www.python.org/ftp/python/')
    content = response.content.decode('utf-8')
    lines = text_line_parser.parse_lines(content, strip_comments = False, strip_text = True, remove_empties = True)
    result = python_version_list()
    for line in lines:
      f = re.findall(r'^.*href=\"(\d+\.\d+.*)\/\".*$', line)
      if len(f) == 1:
        v = python_version(f[0])
        if v.is_full_version():
          result.append(v)
    return result
  
