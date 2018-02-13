#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

setup(
  name = 'bes',
  version = '1.0.0',
  packages = find_packages(include = ['bes*']),
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'bes@fateware.com',
  scripts = [
    '../bin/bes_test.py',
    '../bin/bes_path.py',
    '../bin/bes_refactor.py',
  ],
)
