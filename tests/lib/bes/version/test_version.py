#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.version import version

class test_version(unit_test):

  def test_read_string(self):
    text = '''#!/usr/bin/env python
BES_VERSION = u'1.0.0'
BES_AUTHOR_NAME = u'Sally Foo'
BES_AUTHOR_EMAIL = u'sally@foo.com'
BES_ADDRESS = u''
BES_TAG = u''
'''
    self.assertEqual( (u'1.0.0', u'Sally Foo', u'sally@foo.com', u'', u''), version.read_string(text) )
    
if __name__ == '__main__':
  unit_test.main()
