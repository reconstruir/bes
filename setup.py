#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from setuptools import setup, find_packages

ver = {}
with open('lib/bes/ver.py', 'r', encoding = 'utf-8') as f:
  exec(f.read(), {}, ver)
  
with open('README.md', 'r', encoding = 'utf-8') as fh:
  long_description = fh.read()
    
setup(
  name = 'bes',
  version = ver['BES_VERSION'],
  packages = find_packages('lib'),
  package_dir= {'' : 'lib'},
  include_package_data = True,
  zip_safe = True,
  author = ver['BES_AUTHOR_NAME'],
  author_email = ver['BES_AUTHOR_EMAIL'],
  description = 'An experimental collection of modules related to automation and CICD',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = 'https://gitlab.com/rebuilder/bes',
  classifiers = [
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: Apache Software License :: 2.0',
    'Operating System :: OS Independent',
  ],  python_requires = '>=3.7',
  scripts = [
    'bin/bes_test.py',
    #'bin/bes_refactor.py',
  ],
)
