#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pkgutil
import json
from collections import namedtuple

class version(object):

  _version = namedtuple('_version', 'version,tag')
  
  @classmethod
  def version(clazz, name, version_filename):
    data = pkgutil.get_data(name, version_filename)
    v = json.loads(data)
    return clazz._version(v['version'], v['tag'])
