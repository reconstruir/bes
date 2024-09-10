#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.system.host import host
from bes.system.check import check
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.btl.btl_parser_base import btl_parser_base
from bes.btl.btl_parser_options import btl_parser_options
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error
from bes.btl.btl_parser_state_base import btl_parser_state_base
from bes.btl.btl_parser_tester_mixin import btl_parser_tester_mixin

from bes.config.ini.bc_ini_lexer import bc_ini_lexer
from bes.config.ini.bc_ini_parser import bc_ini_parser

from _test_ini_mixin import _test_ini_mixin

class test_bc_ini_parser(btl_parser_tester_mixin, _test_ini_mixin, unit_test):

  def test_parse_empty(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
''', str(result.root_node) )

  def test_parse_global_comment_only(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse(';empty')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
''', str(result.root_node) )

  def test_parse_section_comment_only(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('''[fruit]
;empty''')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=1,2:i=1
''', str(result.root_node) )
    
  def test_parse_global_only(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
fruit=apple
color=red

fruit=kiwi
color=green
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:fruit:p=2,1:i=1
      n_value;t_value:apple:p=2,7:i=3
    n_key_value;
      n_key;t_key:color:p=3,1:i=5
      n_value;t_value:red:p=3,7:i=7
    n_key_value;
      n_key;t_key:fruit:p=5,1:i=10
      n_value;t_value:kiwi:p=5,7:i=12
    n_key_value;
      n_key;t_key:color:p=6,1:i=14
      n_value;t_value:green:p=6,7:i=16
  n_sections;    
''', str(result.root_node) )

  def test_parse_one_empty_section(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('[fruit]')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=1,2:i=1
''', str(result.root_node) )

  def test_parse_two_empty_sections(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    result = p.parse('[fruit]\n[cheese]\n')
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=1,2:i=1
    n_section;t_section_name:cheese:p=2,2:i=5
''', str(result.root_node) )
    
  def test_parse_one_section(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name=apple
color=red
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value:apple:p=3,6:i=7
      n_key_value;
        n_key;t_key:color:p=4,1:i=9
        n_value;t_value:red:p=4,7:i=11
''', str(result.root_node) )

  def test_parse_two_sections(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name=apple
color=red

[cheese]
name=vieux
smell=stink
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value:apple:p=3,6:i=7
      n_key_value;
        n_key;t_key:color:p=4,1:i=9
        n_value;t_value:red:p=4,7:i=11
    n_section;t_section_name:cheese:p=6,2:i=15
      n_key_value;
        n_key;t_key:name:p=7,1:i=18
        n_value;t_value:vieux:p=7,6:i=20
      n_key_value;
        n_key;t_key:smell:p=8,1:i=22
        n_value;t_value:stink:p=8,7:i=24
''', str(result.root_node) )

  def test_parse_multiple_sessions(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
fruit=apple
color=red
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:fruit:p=2,1:i=1
      n_value;t_value:apple:p=2,7:i=3
    n_key_value;
      n_key;t_key:color:p=3,1:i=5
      n_value;t_value:red:p=3,7:i=7
  n_sections;    
''', str(result.root_node) )

    text = '''
fruit=melon
color=green
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:fruit:p=2,1:i=1
      n_value;t_value:melon:p=2,7:i=3
    n_key_value;
      n_key;t_key:color:p=3,1:i=5
      n_value;t_value:green:p=3,7:i=7
  n_sections;    
''', str(result.root_node) )

  def test_parse_section_key_only_ends_in_line_break(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name=
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value::p=3,6
''', str(result.root_node) )

  def test_parse_section_key_only_ends_in_eos(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
[fruit]
name='''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:fruit:p=2,2:i=2
      n_key_value;
        n_key;t_key:name:p=3,1:i=5
        n_value;t_value::p=3,6
''', str(result.root_node) )

  def test_parse_global_key_only_ends_in_line_break(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
name=
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:name:p=2,1:i=1
      n_value;t_value::p=2,6
  n_sections;    
''', str(result.root_node) )

  def test_parse_global_key_only_ends_in_eos(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
name='''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:name:p=2,1:i=1
      n_value;t_value::p=2,6
  n_sections;    
''', str(result.root_node) )

  def test_parse_global_comment_instead_of_value(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
kiwi = ; foo
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:kiwi:p=2,1:i=1
      n_value;t_value::p=2,8
  n_sections;
''', str(result.root_node) )

  def test_parse_global_comment_after_value(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
kiwi = foo ; that was foo
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:kiwi:p=2,1:i=1
      n_value;t_value:foo :p=2,8:i=5
  n_sections;
''', str(result.root_node) )
    
  def test_parse_double_comment(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
a =
;;
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:a:p=2,1:i=1
      n_value;t_value::p=2,4
  n_sections;    
''', str(result.root_node) )

  def test_parse_global_two_comment_instead_of_value(self):
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    text = '''
kiwi = ; foo
melon = ; bar
'''
    result = p.parse(text)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:kiwi:p=2,1:i=1
      n_value;t_value::p=2,8
    n_key_value;
      n_key;t_key:melon:p=3,1:i=8
      n_value;t_value::p=3,9
  n_sections;    
''', str(result.root_node) )
    
  def test_parse_example_gitea(self):
    source = self.demo_filename('test_data/gitea.app.ini')
    text = self.demo_text('test_data/gitea.app.ini')
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    parser_options = btl_parser_options(source = source)
    result = p.parse(text, options = parser_options)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
    n_key_value;
      n_key;t_key:APP_NAME:p=44,1:i=123
      n_value;t_value::p=44,12
    n_key_value;
      n_key;t_key:RUN_USER:p=47,1:i=136
      n_value;t_value::p=47,12
  n_sections;
    n_section;t_section_name:server:p=58,2:i=172
    n_section;t_section_name:database:p=337,2:i=1008
      n_key_value;
        n_key;t_key:DB_TYPE:p=347,1:i=1038
        n_value;t_value:mysql:p=347,11:i=1042
      n_key_value;
        n_key;t_key:HOST:p=348,1:i=1044
        n_value;t_value:127.0.0.1:3306 :p=348,8:i=1048
      n_key_value;
        n_key;t_key:NAME:p=349,1:i=1052
        n_value;t_value:gitea:p=349,8:i=1056
      n_key_value;
        n_key;t_key:USER:p=350,1:i=1058
        n_value;t_value:root:p=350,8:i=1062
    n_section;t_section_name:security:p=415,2:i=1255
      n_key_value;
        n_key;t_key:INSTALL_LOCK:p=420,1:i=1270
        n_value;t_value:false:p=420,16:i=1274
      n_key_value;
        n_key;t_key:SECRET_KEY:p=424,1:i=1285
        n_value;t_value::p=424,13
      n_key_value;
        n_key;t_key:INTERNAL_TOKEN:p=431,1:i=1307
        n_value;t_value::p=431,16
    n_section;t_section_name:camo:p=497,2:i=1504
    n_section;t_section_name:oauth2:p=514,2:i=1554
      n_key_value;
        n_key;t_key:ENABLE:p=519,1:i=1569
        n_value;t_value:true:p=519,10:i=1573
    n_section;t_section_name:log:p=555,2:i=1679
      n_key_value;
        n_key;t_key:MODE:p=566,1:i=1712
        n_value;t_value:console:p=566,8:i=1716
      n_key_value;
        n_key;t_key:LEVEL:p=569,1:i=1724
        n_value;t_value:Info:p=569,9:i=1728
    n_section;t_section_name:git:p=651,2:i=1970
    n_section;t_section_name:service:p=717,2:i=2163
''', str(result.root_node) )

  def test_parse_example_business_objects(self):
    # This format is a bit whacky which is why i use it to stress test the parser
    source = self.demo_filename('test_data/business_objects.ini')
    text = self.demo_text('test_data/business_objects.ini')
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    parser_options = btl_parser_options(source = source)
    result = p.parse(text, options = parser_options)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:OTHER:p=1,2:i=1
    n_section;t_section_name:OTHER:p=3,2:i=6
      n_key_value;
        n_key;t_key:QUIET:p=5,1:i=10
        n_value;t_value:/qa:p=5,7:i=12
    n_section;t_section_name:INSTALL:p=7,2:i=16
      n_key_value;
        n_key;t_key:ALLUSERS:p=9,1:i=20
        n_value;t_value:"1":p=9,10:i=22
      n_key_value;
        n_key;t_key:AS_ADMIN_IS_SECURE:p=11,1:i=25
        n_value;t_value:"":p=11,20:i=27
      n_key_value;
        n_key;t_key:AS_ADMIN_PASSWORD:p=13,1:i=30
        n_value;t_value:"":p=13,19:i=32
      n_key_value;
        n_key;t_key:AS_ADMIN_PORT:p=15,1:i=35
        n_value;t_value:"8080":p=15,15:i=37
      n_key_value;
        n_key;t_key:AS_ADMIN_USERNAME:p=17,1:i=40
        n_value;t_value:"admin":p=17,19:i=42
      n_key_value;
        n_key;t_key:AS_DIR:p=19,1:i=45
        n_value;t_value:"C:\\Program Files\\Business Objects\\Tomcat55" AS_INSTANCE="localhost":p=19,8:i=47
      n_key_value;
        n_key;t_key:AS_SERVER:p=21,1:i=50
        n_value;t_value:"tomcat55":p=21,11:i=52
      n_key_value;
        n_key;t_key:AS_SERVICE_NAME:p=23,1:i=55
        n_value;t_value:"BOE120Tomcat":p=23,17:i=57
      n_key_value;
        n_key;t_key:AS_VIRTUAL_HOST:p=25,1:i=60
        n_value;t_value:"":p=25,17:i=62
      n_key_value;
        n_key;t_key:ApplicationUsers:p=27,1:i=65
        n_value;t_value:"AllUsers":p=27,18:i=67
      n_key_value;
        n_key;t_key:CADNODE:p=29,1:i=70
        n_value;t_value:"BUSINESSABCDEF":p=29,9:i=72
      n_key_value;
        n_key;t_key:CADPORT:p=31,1:i=75
        n_value;t_value:"6410":p=31,9:i=77
      n_key_value;
        n_key;t_key:CLIENTAUDITINGPORT:p=33,1:i=80
        n_value;t_value:"6420":p=33,20:i=82
      n_key_value;
        n_key;t_key:CLIENTLANGUAGE:p=35,1:i=85
        n_value;t_value:"EN":p=35,16:i=87
      n_key_value;
        n_key;t_key:CLUSTERCMS:p=37,1:i=90
        n_value;t_value:"False":p=37,12:i=92
      n_key_value;
        n_key;t_key:CMSPASSWORD:p=39,1:i=95
        n_value;t_value:"":p=39,13:i=97
      n_key_value;
        n_key;t_key:COMPANYNAME:p=41,1:i=100
        n_value;t_value:"":p=41,13:i=102
      n_key_value;
        n_key;t_key:DATABASEAUDITDRIVER:p=43,1:i=105
        n_value;t_value:"SQLAnyWhereDatabaseSubSystem" DATABASECONNECT="":p=43,21:i=107
      n_key_value;
        n_key;t_key:DATABASEDB:p=45,1:i=110
        n_value;t_value:"BOE120":p=45,12:i=112
      n_key_value;
        n_key;t_key:DATABASEDB_AUDIT:p=47,1:i=115
        n_value;t_value:"BOE120_AUDIT":p=47,18:i=117
      n_key_value;
        n_key;t_key:DATABASEDRIVER:p=49,1:i=120
        n_value;t_value:"SQLAnyWhereDatabaseSubSystem" DATABASEDSN="Business Objects CMS":p=49,16:i=122
      n_key_value;
        n_key;t_key:DATABASEDSN_AUDIT:p=51,1:i=125
        n_value;t_value:"Business Objects Audit Server" DATABASENWLAYER_AUDIT="ODBC":p=51,19:i=127
      n_key_value;
        n_key;t_key:DATABASEPORT:p=53,1:i=130
        n_value;t_value:"2638":p=53,14:i=132
      n_key_value;
        n_key;t_key:DATABASEPORT_AUDIT:p=55,1:i=135
        n_value;t_value:"2638":p=55,20:i=137
      n_key_value;
        n_key;t_key:DATABASEPWD:p=57,1:i=140
        n_value;t_value:"password1":p=57,13:i=142
      n_key_value;
        n_key;t_key:DATABASEPWD_AUDIT:p=59,1:i=145
        n_value;t_value:"password1":p=59,19:i=147
      n_key_value;
        n_key;t_key:DATABASEPWD_SQLANYWHEREROOT:p=61,1:i=150
        n_value;t_value:"password1":p=61,29:i=152
      n_key_value;
        n_key;t_key:DATABASERDMS_AUDIT:p=63,1:i=155
        n_value;t_value:"MySQL 5":p=63,20:i=157
      n_key_value;
        n_key;t_key:DATABASESERVER_AUDIT:p=65,1:i=160
        n_value;t_value:"localhost":p=65,22:i=162
      n_key_value;
        n_key;t_key:DATABASEUID:p=67,1:i=165
        n_value;t_value:"sa":p=67,13:i=167
      n_key_value;
        n_key;t_key:DATABASEUID_AUDIT:p=69,1:i=170
        n_value;t_value:"sa":p=69,19:i=172
      n_key_value;
        n_key;t_key:DATABASE_AUDIT_CONNSVR:p=71,1:i=175
        n_value;t_value:"connsvr":p=71,24:i=177
      n_key_value;
        n_key;t_key:ENABLELOGFILE:p=73,1:i=180
        n_value;t_value:"1":p=73,15:i=182
      n_key_value;
        n_key;t_key:ENABLESERVERS:p=75,1:i=185
        n_value;t_value:"1":p=75,15:i=187
      n_key_value;
        n_key;t_key:INSTALL.LP.EN.SELECTED:p=77,1:i=190
        n_value;t_value:"1":p=77,24:i=192
      n_key_value;
        n_key;t_key:INSTALL.LP.FR.SELECTED:p=79,1:i=195
        n_value;t_value:"1":p=79,24:i=197
      n_key_value;
        n_key;t_key:INSTALLDBTYPE:p=81,1:i=200
        n_value;t_value:"SQL":p=81,15:i=202
      n_key_value;
        n_key;t_key:INSTALLDIR:p=83,1:i=205
        n_value;t_value:"C:\\Program Files\\Business Objects\\" INSTALLLEVEL="6":p=83,12:i=207
      n_key_value;
        n_key;t_key:INSTALLMODE:p=85,1:i=210
        n_value;t_value:"New":p=85,13:i=212
      n_key_value;
        n_key;t_key:INSTALLSWITCH:p=87,1:i=215
        n_value;t_value:"Server":p=87,15:i=217
      n_key_value;
        n_key;t_key:INSTALL_DB_TYPE:p=89,1:i=220
        n_value;t_value:"SQLANYWHERE":p=89,17:i=222
      n_key_value;
        n_key;t_key:MYSQLPORT:p=91,1:i=225
        n_value;t_value:"3306":p=91,11:i=227
      n_key_value;
        n_key;t_key:MYSQL_REMOTE_ACCESS:p=93,1:i=230
        n_value;t_value:"":p=93,21:i=232
      n_key_value;
        n_key;t_key:NEWCMSPASSWORD:p=95,1:i=235
        n_value;t_value:"password1":p=95,16:i=237
      n_key_value;
        n_key;t_key:NSPORT:p=97,1:i=240
        n_value;t_value:"6400":p=97,8:i=242
      n_key_value;
        n_key;t_key:PIDKEY:p=99,1:i=245
        n_value;t_value:"XXXXX-XXXXXXX-XXXXXXX-XXXX":p=99,8:i=247
      n_key_value;
        n_key;t_key:Privileged:p=101,1:i=250
        n_value;t_value:"1":p=101,12:i=252
      n_key_value;
        n_key;t_key:SINGLESERVER:p=103,1:i=255
        n_value;t_value:"":p=103,14:i=257
      n_key_value;
        n_key;t_key:SKIP_DEPLOYMENT:p=105,1:i=260
        n_value;t_value:"":p=105,17:i=262
      n_key_value;
        n_key;t_key:TOMCAT_CONNECTION_PORT:p=107,1:i=265
        n_value;t_value:"8080":p=107,24:i=267
      n_key_value;
        n_key;t_key:TOMCAT_REDIRECT_PORT:p=109,1:i=270
        n_value;t_value:"8443":p=109,22:i=272
      n_key_value;
        n_key;t_key:TOMCAT_SHUTDOWN_PORT:p=111,1:i=275
        n_value;t_value:"8005":p=111,22:i=277
      n_key_value;
        n_key;t_key:USERNAME:p=113,1:i=280
        n_value;t_value:"Business Objects":p=113,10:i=282
      n_key_value;
        n_key;t_key:WCADOTNETINSTALL:p=115,1:i=285
        n_value;t_value:"False":p=115,18:i=287
      n_key_value;
        n_key;t_key:WCAEXISTINGINSTALL:p=117,1:i=290
        n_value;t_value:"False":p=117,20:i=292
      n_key_value;
        n_key;t_key:WCAJAVAINSTALL:p=119,1:i=295
        n_value;t_value:"True":p=119,16:i=297
      n_key_value;
        n_key;t_key:WCATOMCATINSTALL:p=121,1:i=300
        n_value;t_value:"True":p=121,18:i=302
      n_key_value;
        n_key;t_key:WDEPLOY_LANGUAGES:p=123,1:i=305
        n_value;t_value:"en,fr":p=123,19:i=307
      n_key_value;
        n_key;t_key:WDEPLOY_LATER:p=125,1:i=310
        n_value;t_value:"":p=125,15:i=312
      n_key_value;
        n_key;t_key:WEBSITE_METABASE_NUMBER:p=127,1:i=315
        n_value;t_value:"1":p=127,25:i=317
      n_key_value;
        n_key;t_key:WEBSITE_NAME:p=129,1:i=320
        n_value;t_value:"":p=129,14:i=322
      n_key_value;
        n_key;t_key:WEBSITE_PORT:p=131,1:i=325
        n_value;t_value:"80":p=131,14:i=327
    n_section;t_section_name:FEATURES:p=133,2:i=331
      n_key_value;
        n_key;t_key:REMOVE:p=135,1:i=335
        n_value;t_value:"WCADotNet,WebApplicationContainer":p=135,8:i=337
      n_key_value;
        n_key;t_key:ADDLOCAL:p=137,1:i=340
        n_value;t_value:"Tomcat,Universe,qaaws,Complete,DotNETSDK,Dot NET2SDK,ImportWizard,VSDesigner,AlwaysInstall,BeforeIn stall,VBA62,Reporter,Clients,WRC,DataSourceMigrationWiz ard,CrystalBVM,MetaDataDesigner,ConversionTool,PubWiz,De signer,DotNetRASSDK,DotNetViewersSDK,VSHELP,RenetSDK,De velopersFiles,JavaRASSDK,BOEJavaSDK,JavaViewersSDK,Re beanSDK,WebServicesSDK,UnivTransMgr,wdeploy,BIPWeb Comp,WebTierComp,BOEWebServices,CCM,ServerComponents,Map ping,Repository,CRPE,MetaData,CMS,Auditor,MySQL,EventServ er,InputFRS,OutputFRS,CacheServer,PageServer,Publication Server,DotNETOnly,ReportAppServer,MDASS,CRJobServ er,DestJobServer,LOVJobServer,DeskIJobServer,ProgramJob Server,WebIJobServer,AdaptiveJobServer,PublishingSer vice,AdaptiveProcessingServer,SearchingService,CrystalRe portDataProvider,AuditProxyService,Webi,RAS21,DAS,AuditRp tUnvEN,DADataFederator,DataAccess,HPNeoview,OLAP,My Cube,SOFA,DAMySQL,DAGenericODBC,SFORCE,XML,BDE,dBase,FileSystem,DANETEZZA,DAMi crosoft,DAIBMDB2,IBM,Redbrick,DAIBMInformix,OLE_DB_Da ta,DAProgressOpenEdge,DAOracle,SybaseAnywhere,DASy base,SybaseASE,SybaseIQ,SymantecACT,DANCRTeradata,Text DA,Btrieve,CharacterSeparated,ExportSupport,ExpDisk File,ExpRichTextFormat,ExpWordforWindows,PDF,ExpText,Ex pExcel,ExpCrystalReports,XMLExport,LegacyXMLExport,Sam plesEN,UserHelp,LanguagePackCostingFeatureen,LanguagePack CostingFeature":p=137,10:i=342
      n_key_value;
        n_key;t_key:ADDSOURCE:p=139,1:i=345
        n_value;t_value:"":p=139,11:i=347
      n_key_value;
        n_key;t_key:ADVERTISE:p=141,1:i=350
        n_value;t_value:"":p=141,11:i=352
''', str(result.root_node) )

  def test_parse_example1(self):
    source = self.demo_filename('test_data/example1.ini')
    text = self.demo_text('test_data/example1.ini')
    l = bc_ini_lexer()
    p = bc_ini_parser(l)
    variables = { 'v_comment_begin': '#' }
    parser_options = btl_parser_options(source = source,
                                      variables = variables)
    result = p.parse(text, options = parser_options)
    #print(str(result.root_node))
    self.assert_python_code_text_equal( '''
n_root;
  n_global_section;
  n_sections;
    n_section;t_section_name:http:p=6,2:i=12
      n_key_value;
        n_key;t_key:port:p=7,1:i=15
        n_value;t_value:8080:p=7,6:i=17
      n_key_value;
        n_key;t_key:username:p=8,1:i=19
        n_value;t_value:httpuser:p=8,10:i=21
    n_section;t_section_name:https:p=11,2:i=28
      n_key_value;
        n_key;t_key:port:p=12,1:i=31
        n_value;t_value:8043:p=12,6:i=33
      n_key_value;
        n_key;t_key:username:p=13,1:i=35
        n_value;t_value:httpsuser:p=13,10:i=37
    n_section;t_section_name:FTP:p=16,2:i=44
      n_key_value;
        n_key;t_key:port:p=17,1:i=47
        n_value;t_value:8043:p=17,6:i=49
      n_key_value;
        n_key;t_key:username:p=18,1:i=51
        n_value;t_value:ftpuser:p=18,10:i=53
    n_section;t_section_name:database:p=21,2:i=60
      n_key_value;
        n_key;t_key:driverclass:p=22,1:i=63
        n_value;t_value:com.mysql.jdbc.Driver:p=22,17:i=67
      n_key_value;
        n_key;t_key:dbName:p=23,1:i=69
        n_value;t_value:mydatabase:p=23,17:i=73
      n_key_value;
        n_key;t_key:port:p=24,1:i=75
        n_value;t_value:3306:p=24,17:i=79
      n_key_value;
        n_key;t_key:username:p=25,1:i=81
        n_value;t_value:root:p=25,17:i=85
      n_key_value;
        n_key;t_key:password:p=26,1:i=87
        n_value;t_value:secure :p=26,17:i=91
    n_section;t_section_name:settings:p=28,2:i=99
      n_key_value;
        n_key;t_key:enable_ssl:p=29,1:i=102
        n_value;t_value:true:p=29,14:i=106
      n_key_value;
        n_key;t_key:enable_2mf:p=30,1:i=108
        n_value;t_value:true:p=30,15:i=112
''', str(result.root_node) )
    
if __name__ == '__main__':
  unit_test.main()
