#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

setup(
  name = 'foo',
  version = '1.0.0',
  packages = find_packages(include = ['foo*']),
  include_package_data = True,
  zip_safe = True,
  author = 'Ramiro Estrugo',
  author_email = 'ramiro@fateware.com',
  scripts = [
    '../bin/foo_prog.py',
  ],
)
