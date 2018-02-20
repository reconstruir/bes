#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

ver = {}
exec(open('lib/bes/ver.py', 'r').read(), {}, ver)
setup(
  name = 'bes',
  version = ver['BES_VERSION'],
  packages = find_packages('lib'),
  package_dir= {'' : 'lib'},
  include_package_data = True,
  zip_safe = True,
  author = ver['BES_AUTHOR_NAME'],
  author_email = ver['BES_AUTHOR_EMAIL'],
  scripts = [
    'bin/bes_test.py',
    'bin/bes_path.py',
    'bin/bes_refactor.py',
  ],
)
