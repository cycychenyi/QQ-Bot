#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import nonebot

import config

sys.path.append(os.path.dirname(__file__))
from utils import database

vocabulary_dk_group = '''
create table vocabulary_dk_group
(
	group_id int
		constraint vocabulary_dk_group_pk
			primary key,
	expire datetime not null
);
'''.strip()
vocabulary_dk_user = '''
create table vocabulary_dk_user
(
    user_id int
        constraint vocabulary_dk_user_pk
            primary key,
    name text not null,
    software text not null,
    target_new_words int default null,
    target_old_words int default null,
    target_all_words int default null,
    score int default 0 not null,
    all_words int default 0 not null,
    days int default 0 not null,
    expire datetime not null
);
'''.strip()

if __name__ == '__main__':
    # 初始化数据库
    tables = database.retrieve("select name from sqlite_master where type='table';")
    if ('vocabulary_dk_group',) not in tables:
        database.run(vocabulary_dk_group)
    if ('vocabulary_dk_user',) not in tables:
        database.run(vocabulary_dk_user)
    # 运行 nonebot
    nonebot.init(config)
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'bot', 'plugins'),
        'bot.plugins'
    )
    nonebot.run()
