#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path
from bes.test import unit_test_helper
from bes.common import Shell

class test_functions(unit_test_helper):

  def xtest_function(self):
    script = '%s.sh' % (path.splitext(__file__)[0])
    print "running: %s" % (script)
    rv = Shell.execute(script, shell = False, stderr_to_stdout = True, raise_error = False)
    print rv.stdout
    self.assertEqual( 0, rv.exit_code )
    
if __name__ == "__main__":
  unit_test_helper.main()
