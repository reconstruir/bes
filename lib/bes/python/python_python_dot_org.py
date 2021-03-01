#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import re

from bes.common.check import check
from bes.compat import url_compat
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.url.url_util import url_util
from bes.version.software_version import software_version
from bes.text.text_line_parser import text_line_parser

from .python_version import python_version

class python_python_dot_org(object):
  'Class to deal with python.org listings and downloads'
  
  @classmethod
  def available_versions(clazz, num):
    'Return a list of python versions available to install.'
    check.check_int(num)
    
    index = clazz._download_available_index()
    sorted_index = software_version.sort_versions(index, reverse = True)
    # theres no point showing versions older than 2.7
    modern_index = [ v for v in sorted_index if software_version.compare(v, '2.7') > 0 ]
    if not num:
      return modern_index
    version_table = {}
    for any_version in modern_index:
      major_version = python_version.any_version_to_version(any_version)
      if not major_version in version_table:
        version_table[major_version] = []
      version_table[major_version].append(any_version)
    result = []

    # theres no point showing obsolete (and sometimes dangerous) versions
    obsolete_versions = ( '3.0', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6' )
    
    for version in sorted([ key for key in version_table.keys() ]):
      if not version in obsolete_versions:
        versions = version_table[version][0 : num]
        result.extend(versions)
    return software_version.sort_versions(result)

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
  def downlod_package_to_temp_file(clazz, url, debug = False):
    tmp_dir = temp_file.make_temp_dir(suffix = '-python-download')
    basename = path.basename(url)
    tmp_package = path.join(tmp_dir, basename)
    url_util.download_to_file(url, tmp_package)
    return tmp_package
  
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
  
