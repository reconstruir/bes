#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.version import version_info

class test_version_info(unit_test):

  def test_read_string(self):
    text = '''#!/usr/bin/env python
BES_VERSION = u'1.0.0'
BES_AUTHOR_NAME = u'Sally Foo'
BES_AUTHOR_EMAIL = u'sally@foo.com'
BES_ADDRESS = u''
BES_TAG = u''
BES_TIMESTAMP = u''
'''
    self.assertEqual( (u'1.0.0', u'Sally Foo', u'sally@foo.com', u'', u'', u''), version_info.read_string(text) )
    
  def test___str__(self):
    expected = '''\
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

BES_VERSION = u'1.0'
BES_AUTHOR_NAME = u'Sally Bar'
BES_AUTHOR_EMAIL = u'sally@bar.com'
BES_ADDRESS = u''
BES_TAG = u''
BES_TIMESTAMP = u''
'''
    self.assertMultiLineEqual( expected, str(version_info(u'1.0', u'Sally Bar', u'sally@bar.com', u'', u'', u'')) )
    
  def test_change(self):
    vi = version_info(u'1.0', u'Sally Bar', u'sally@bar.com', u'', u'', u'')
    self.assertEqual( (u'1.0', u'Sally Bar', u'sally@bar.com', u'', u'666', u'123'), vi.change(tag = u'666', timestamp = u'123') )
    
  def test_version_string(self):
    self.assertEqual(u'1.0:foo@bar:123:abc', version_info(u'1.0', u'Sally Bar', u'sally@bar.com', u'foo@bar', u'123', u'abc').version_string() )
    
if __name__ == '__main__':
  unit_test.main()
