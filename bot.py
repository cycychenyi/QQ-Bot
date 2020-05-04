#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import nonebot

import config

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'bot', 'plugins'),
        'bot.plugins'
    )
    nonebot.run()

