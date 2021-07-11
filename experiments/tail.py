#!/usr/bin/env python

import argparse
import os
import os.path as path
import platform
import socket
import subprocess
import sys
import sys
import tarfile
import tempfile
import zipfile
import time

def follow(fd):
  ## get existing lines
  for line in fd:
    yield line
  ## follow the remaining lines
  fd.seek(0, os.SEEK_END)
  while True:
    line = fd.readline()
    if not line:
      time.sleep(0.1)
      continue
    yield line

class file_tailer(object):

  def __init__(self):
    pass
  
  def main(self):
    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose log output [ False ]')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode.  Save temp files and log the script itself [ False ]')
    p.add_argument('--tty', action = 'store', default = None,
                   help = 'tty to log to in debug mode [ False ]')
    p.add_argument('--port', action = 'store', default = 9999, type = int,
                   help = 'Port to bind to for tail clients [ False ]')
    p.add_argument('--num', action = 'store', default = 10, type = int,
                   help = 'Number of lines to show at first [ False ]')
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The file to tail []')
    args = p.parse_args()

    if not path.exists(args.filename):
      raise IOError('file not found: "{}"'.format(args.filename))
    
    if not path.isfile(args.filename):
      raise IOError('not a file: "{}"'.format(args.filename))

    self._socket = None
    self._start_socket(args.port)
    
    with open(args.filename, 'r') as fd:
      first = True
      while True:
        print('loop')
        lines = follow(fd)
        if first:
          first = False
          print('before')
          for i in range(0, args.num):
            for line in lines:
              print(line.strip())
          print('after')
        for line in lines:
          print(line.strip())
    return 0

  def _log(self, message):
    print(message)
  
  def _start_socket(self, port):
    if not port:
      return
    address = ( 'localhost', port )
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._log('binding socket to port {}'.format(port))
    self._socket.bind(address)
    print('bound')

  def _stop_socket(self):
    self._socket.close()
    self._socket = None
    
  @classmethod
  def run(clazz):
    raise SystemExit(file_tailer().main())
  
  x='''
  def _start_socket(self, port):
    if not port:
      return
    address = ( 'localhost', port )
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._log('binding socket to port {}'.format(port))
    self._socket.bind(address)

  def _stop_socket(self):
    self._socket.close()
    self._socket = None
    
  def _execute(self, dest_dir, command, output_log, entry_command_args):
    entry_command_args = entry_command_args or []
    stdout_pipe = subprocess.PIPE
    stderr_pipe = subprocess.STDOUT
    command_abs = path.join(dest_dir, command)
    if not path.isfile(command_abs):
      raise IOError('entry command not found: "{}"'.format(command_abs))
    args = [ command_abs ] + entry_command_args
    self._log('args={} cwd={}'.format(args, dest_dir))
    os.chmod(command_abs, 0o0755)
    process = subprocess.Popen(args,
                               stdout = stdout_pipe,
                               stderr = stderr_pipe,
                               shell = False,
                               cwd = dest_dir,
                               universal_newlines = True)

    if self._socket:
      self._log('socket listening')
      self._socket.listen(1)
      self._log('calling accept')
      connection, client_address = self._socket.accept()
      self._log('connection={} client_address={}'.format(connection, client_address))

    stdout_lines = []
    if True:
      # Poll process for new output until finished
      while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        stdout_lines.append(nextline)
        self._log('process: {}'.format(nextline))

    output = process.communicate()
    exit_code = process.wait()
    self._mkdir(path.dirname(output_log))
    stdout = output[0]
    with open(output_log, 'a') as fout:
      fout.write(stdout)
      fout.flush()
    return exit_code

  @classmethod
  def _mkdir(clazz, p):
    if path.isdir(p):
      return
    os.makedirs(p)
  
  def _unpack_package_zip(self, package_zip, dest_dir):
    with zipfile.ZipFile(package_zip, mode = 'r') as f:
      f.extractall(path = dest_dir)

  def _unpack_package_tar(self, package_tar, dest_dir):
    with tarfile.open(package_tar, mode = 'r') as f:
      f.extractall(path = dest_dir)

  def _unpack_package(self, package, dest_dir):
    if zipfile.is_zipfile(package):
      self._unpack_package_zip(package, dest_dir)
    elif tarfile.is_tarfile(package):
      self._unpack_package_tar(package, dest_dir)
    else:
      raise RuntimeError('unknown archive type: "{}"'.format(package))
      
  def _log(self, message):
    if not self._debug:
      return
    s = '{}: {}\n'.format(self._name, message)
    with open(self._console_device, 'w') as f:
      f.write(s)
      f.flush()

  @classmethod
  def _find_console_device(clazz):
    system = platform.system()
    if system == 'Windows':
      return 'con:'
    elif system == 'Darwin':
      return '/dev/ttys000'
    elif system == 'Linux':
      return '/dev/console'
    else:
      raise RuntimeError('unknown platform: "{}"'.format(system))

if __name__ == '__main__':
  package_caller.run()
'''  

from os import listdir,SEEK_END
from os.path import isfile, join, getmtime
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import time
import subprocess
import select
#from urllib.parse import parse_qs,urlparse

from bes.compat import url_compat

import logging
import sys, os, socket
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer

class RequestsHandler(BaseHTTPRequestHandler):
  cgi_directories = ["/www"] #to run all scripts in '/www' folder
  def do_GET(self):
    with open('/tmp/caca.log', 'r') as fd:
      lines = follow(fd)
      for line in lines:
        print('line: {}'.format(line.strip()))
    
    #self.wfile.write(bytes("</body></html>", "utf-8"))
    self.send_error(404, "Page '%s' not found" % self.path)


    
#    logging.info (self.path)
#    try:
#      if self.path == '/ls':
#        listfiles(self)
#      elif self.path.startswith('/tail'):
#        tail(self)
#    except IOError:
#      self.send_error(404, "Page '%s' not found" % self.path)

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
  pass
  
def www_main():
  s = ThreadingSimpleServer(("localhost", 9999), RequestsHandler)
  s.serve_forever()
      
if __name__ == '__main__':
  www_main()
  #file_tailer.run()
  
