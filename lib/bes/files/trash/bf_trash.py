#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.host import host
from bes.files.bf_check import bf_check

from ._detail._bf_trash_factory import _bf_trash_factory

class bf_trash(_bf_trash_factory.get_trash_super_class()):
  pass
