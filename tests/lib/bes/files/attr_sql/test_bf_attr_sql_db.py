#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from os import path

from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test

from bes.files.attr_sql.bf_attr_sql_db import bf_attr_sql_db
#from rmt.vb.vb_attachment import vb_attachment
#from rmt.vb.vb_attachment_list import vb_attachment_list
#from rmt.vb.vb_db import vb_db
#from rmt.vb.vb_error import vb_error
#from rmt.vb.vb_post import vb_post
#from rmt.vb.vb_post_list import vb_post_list
#from rmt.vb.vb_showthread_result import vb_showthread_result

#from example_content import example_content

class test_bf_attr_sql_db(unit_test):

  def _make_tmp_db(self):
    tmp_db_filename = path.join(self.make_temp_dir(), 'test.db')
    return bf_attr_sql_db(tmp_db_filename)

  def test_set_get_value(self):
    db = self._make_tmp_db()
    value = 'kiwi'.encode('utf-8')
    db.set_value('hash_666', 'fruit', 'kiwi'.encode('utf-8'))
    self.assertEqual( value, db.get_value('hash_666', 'fruit') )

if __name__ == '__main__':
  unit_test.main()
