#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from .bf_checksum_db import checksum_db

class bf_global_checksum_db(bf_checksum_db):

  def __init__(self):
    db_filename = path.expanduser('~/.bes/bes_global_checksum_db.sqlite')
    super().__init__(db_filename)
