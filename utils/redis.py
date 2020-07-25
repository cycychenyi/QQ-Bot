#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import redis

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from private_config import redis as redis_config


def set(key, value, ex=None):
    pool = redis.ConnectionPool(host='localhost', port=6379, password=redis_config['password'], db=0)
    r = redis.StrictRedis(connection_pool=pool)
    success = r.set(key, value, ex)
    r.connection_pool.disconnect()
    return success


def get(key):
    pool = redis.ConnectionPool(host='localhost', port=6379, password=redis_config['password'], db=0)
    r = redis.StrictRedis(connection_pool=pool)
    result = r.get(key)
    r.connection_pool.disconnect()
    return result


def delete(key):
    pool = redis.ConnectionPool(host='localhost', port=6379, password=redis_config['password'], db=0)
    r = redis.StrictRedis(connection_pool=pool)
    rowcount = r.delete(key)
    r.connection_pool.disconnect()
    return rowcount
