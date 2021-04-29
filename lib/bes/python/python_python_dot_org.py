#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import re

from bes.common.check import check
from bes.compat import url_compat
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.host import host
from bes.text.text_line_parser import text_line_parser
from bes.url.url_util import url_util
from bes.version.software_version import software_version

from .python_version import python_version
from .python_error import python_error

class python_python_dot_org(object):
  'Class to deal with python.org listings and downloads'
  
  @classmethod
  def available_versions(clazz, system, num):
    'Return a list of python versions available to install.'
    check.check_string(system)
    check.check_int(num)

    all_possible_version = clazz.all_possible_versions(system)
    if not num:
      return all_possible_version
    major_version_table = {}
    for full_version in all_possible_version:
      major_version = python_version.version(full_version)
      if not major_version in major_version_table:
        major_version_table[major_version] = []
      major_version_table[major_version].append(full_version)

    result = []
    for major_version in sorted([ key for key in major_version_table.keys() ]):
      available_versions = major_version_table[major_version]
      limited_versions = available_versions[0 : num]
      result.extend(limited_versions)
    return software_version.sort_versions(result)

  # theres no point showing obsolete (and sometimes dangerous) versions
  _MIN_PYTHON2_VERSION = '2.7'
  _MIN_PYTHON3_VERSION = '3.7'

  @classmethod
  def _should_include_version(clazz, full_version):
    'Return True if the given python version is one we want to expose'
    # python2: any 2.7
    if software_version.compare(full_version, '2.7') >= 0 and software_version.compare(full_version, '2.7') < 0:
      return True
    # python3: 3.7 and greater
    if software_version.compare(full_version, '3.7') >= 0 and software_version.compare(full_version, '4.0') < 0:
      return True
    return False
  
  @classmethod
  def all_possible_versions(clazz, system):
    '''
    Return a list of all possible versions according to the python.org index for 
    a union of all platforms.
    Some of these dont exist for some platforms so you need to call filter_versions()
    to get a valid list.
    '''
    check.check_string(system)
    
    index = clazz._download_available_index()
    possible = [ v for v in index if clazz._should_include_version(v) ]
    existing = [ v for v in possible if clazz.full_version_exists(system, v) ]
    return software_version.sort_versions(existing, reverse = True)

  @classmethod
  def filter_versions(clazz, system):
    '''
    Return a list of all possible versions according to the python.org index for 
    a union of all platforms.
    Some of these dont exist for some platforms so you need to call filter_versions()
    to get a valid list.
    '''
    
    index = clazz._download_available_index()
    sorted_index = software_version.sort_versions(index, reverse = True)
    return [ v for v in sorted_index if clazz._should_include_version(v) ]
  
  _BASE_URL = 'https://www.python.org/ftp/python/'
  @classmethod
  def macos_package_url(clazz, full_version):
    'Return the macos package url for a specific version of python.'
    check.check_string(full_version)

    basename = 'python-{full_version}-macosx10.9.pkg'.format(full_version = full_version)
    fragment = '{full_version}/{basename}'.format(full_version = full_version, basename = basename)
    return url_compat.urljoin(clazz._BASE_URL, fragment)

  @classmethod
  def windows_package_url(clazz, full_version):
    'Return the windows package url for a specific version of python.'
    check.check_string(full_version)

    basename = 'python-{full_version}-amd64.exe'.format(full_version = full_version)
    fragment = '{full_version}/{basename}'.format(full_version = full_version, basename = basename)
    return url_compat.urljoin(clazz._BASE_URL, fragment)

  @classmethod
  def package_url(clazz, system, full_version):
    'Return the package url for a specific version of python for system.'
    check.check_string(full_version)

    if system == host.WINDOWS:
      url = clazz.windows_package_url(full_version)
    elif system == host.MACOS:
      url = clazz.macos_package_url(full_version)
    else:
      host.raise_unsupported_system(system = system)
    return url

  @classmethod
  def full_version_exists(clazz, system, full_version):
    '''
    Return True if the package for full version exists for system.
    Sometimes python.org has versions in the index that dont exist
    for some platforms.
    '''
    check.check_string(system)
    check.check_string(full_version)

    url = clazz.package_url(system, full_version)
    return url_util.exists(url)
  
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
    url = clazz.package_url(system, full_version)
    return clazz._downlod_url(url, debug = False)
  
  @classmethod
  def _download_available_index(clazz):
    'Download and parse the available python version index.'

    response = url_util.get('https://www.python.org/ftp/python/')
    content = response.content.decode('utf-8')
    lines = text_line_parser.parse_lines(content, strip_comments = False, strip_text = True, remove_empties = True)
    result = []
    for line in lines:
      f = re.findall(r'^.*href=\"(\d+\.\d+.*)\/\".*$', line)
      if len(f) == 1:
        result.append(f[0])
    return result
  
