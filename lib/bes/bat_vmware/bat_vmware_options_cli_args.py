#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_vmware_options_cli_args(object):
  
  @classmethod
  def add_arguments(clazz, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    p.add_argument('--vmrest-username', action = 'store', type = str, default = None,
                   help = 'Username for vmrest.  None means generate a random one. [ None ]')
    p.add_argument('--vmrest-password', action = 'store', type = str, default = None,
                   help = 'Password for vmrest.  None means generate a random one. [ None ]')
    p.add_argument('--vmrest-port', action = 'store', type = int, default = 8697,
                   dest = 'vmrest_port',
                   help = 'Port for vmrest [ 8697 ]')
    p.add_argument('--username', action = 'store', type = str, default = None,
                   dest = 'login_username',
                   help = 'Username for vm uer login [ ]')
    p.add_argument('--password', action = 'store', type = str, default = None,
                   dest = 'login_password',
                   help = 'Password for vm user login [ ]')
    p.add_argument('--tty', action = 'store', default = None,
                   help = 'tty to log to in debug mode [ False ]')
    p.add_argument('--config', action = 'store', type = str, default = None,
                   dest = 'config_filename',
                   help = 'Use config filename [ False ]')
