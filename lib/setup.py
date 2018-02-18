#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

import os
print('fuck: pwd=%s' % (os.getcwd()))

setup(
  name = 'bes',
  version = '@VERSION@',
  packages = find_packages(include = ['bes*']),
  include_package_data = True,
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
  scripts = [
    '../bin/bes_test.py',
    '../bin/bes_path.py',
    '../bin/bes_refactor.py',
  ],
)
