#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json, struct, unittest

_int_packer = struct.Struct('I')

def encode_int(i):
  return _int_packer.pack(( i ))

def decode_int(data):
  return _int_packer.unpack(data)[0]

def encode_request(request):
  json_data = json.dumps(request)
#  size_data = encode_int(len(json_data))
#  return size_data + json_data
  return json_data

def decode_request(request):
  json_data = json.dumps(request)
#  size_data = encode_int(len(json_data))
#  return size_data + json_data
  return json_data

def receive_message(sock):
#  size_data = sock.recv(4)
#  size = decode_int(size_data)
  data = sock.recv(1024 * 64)
  return json.loads(data)

def send_message(sock, message):
  data = encode_request(message)
  #len_sent = sock.write(data)
  sock.write(data)
  #print "data='%s'; data_len=%d; len_sent=%d" % (data, len(data), len_sent)
  #assert len_sent == len(data)

class TestServerTools(unittest.TestCase):

  def test_encode(self):
    self.assertEqual( 666, decode_int(encode_int(666)) )

if __name__ == "__main__":
  unittest.main()
