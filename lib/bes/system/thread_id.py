#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .impl_import import impl_import

thread_id = impl_import.load(__name__, 'thread_id', globals())
