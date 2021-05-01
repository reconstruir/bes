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
    if check.is_string(full_version):
      full_version = python_version(full_version)
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
    tmp_dir = temp_file.make_temp_dir(suffix = '-python-download', delete = not debug)
    basename = path.basename(url)
    tmp_package = path.join(tmp_dir, basename)
    url_util.download_to_file(url, tmp_package)
    if debug:
      print('tmp python package download: {}'.format(tmp_package))
    expected_checksum = clazz._fetch_checksum(url)
    if not expected_checksum:
      raise python_error('Failed to determine checksum for: {}'.format(url))
    actual_checksum = file_util.checksum('md5', tmp_package)
    if expected_checksum != actual_checksum:
      msg = '''
CHECKSUM MISMATCH: url={url}
CHECKSUM MISMATCH: expected={expected}
CHECKSUM MISMATCH: actual={actual}
CHECKSUM MISMATCH: filename={filename}
CHECKSUM MISMATCH: run with --debug to keep and debug the download
'''.format(url = url,
           expected = expected_checksum,
           actual = actual_checksum,
           filename = tmp_package)
      raise python_error(msg)
    return tmp_package

  @classmethod
  def download_package(clazz, system, full_version, debug = False):
    'Download the major.minor.revision full version of python to a temporary file.'
    if check.is_string(full_version):
      full_version = python_version(full_version)
    check.check_python_version(full_version)

    url = clazz.find_package_url(system, full_version)
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

  @classmethod
  def _full_version_for_url(clazz, url):
    'Download the major.minor.revision full version of python to a temporary file.'

    f = re.findall(r'^https://www.python.org/ftp/python/(\d+\.\d+\.\d+)/.*$', url)
    if not f:
      return None
    if len(f) != 1:
      return None
    return python_version(f[0])
  
  @classmethod
  def _checksum_index_url(clazz, url):
    full_version = clazz._full_version_for_url(url)
    assert full_version
    return 'https://www.python.org/downloads/release/python-{}/'.format(full_version.join_parts(''))

  @classmethod
  def _fetch_checksum(clazz, url):
    index_url = clazz._checksum_index_url(url)
    response = url_util.get(index_url)
    content = response.content.decode('utf-8')
    parser = text_line_parser(content)
    start_pattern = url
    end_pattern = url + '.asc'
    section = parser.cut_lines(start_pattern, end_pattern, include_pattern = False)
    if len(section) != 4:
      return None
    line = section[2].text
    f = re.findall(r'^\s*\<td\>([0-9a-f]+)\<\/td\>\s*$', line)
    if not f:
      return None
    if len(f) != 1:
      return None
    return f[0]
