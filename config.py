#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform

from nonebot.default_config import *

from private_config import coolq

if 'Windows' in platform.platform():
    HOST = '127.0.0.1'
else:
    HOST = '0.0.0.0'
PORT = 8080

SUPERUSERS = coolq['superusers']
COMMAND_START = {''}
