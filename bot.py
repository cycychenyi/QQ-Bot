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
	expire text not null
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
    target_expire text not null,
    today_new_words int default null,
    today_old_words int default null,
    today_all_words int default null,
    today_expire text default null,
    score int default 0 not null,
    all_words int default 0 not null,
    days int default 0 not null
);
'''.strip()
tomato_todo_group = '''
create table tomato_todo_group
(
	group_id int
		constraint tomato_todo_group_pk
			primary key
);
'''.strip()
tomato_todo_info = '''
create table tomato_todo_info
(
	password int
		constraint tomato_todo_group_pk
			primary key
);
'''.strip()

if __name__ == '__main__':
    # 初始化数据库
    tables = database.retrieve("select name from sqlite_master where type='table';")
    if ('vocabulary_dk_group',) not in tables:
        database.run(vocabulary_dk_group)
    if ('vocabulary_dk_user',) not in tables:
        database.run(vocabulary_dk_user)
    if ('tomato_todo_group',) not in tables:
        database.run(tomato_todo_group)
    if ('tomato_todo_info',) not in tables:
        database.run(tomato_todo_info)
    # 运行 nonebot
    nonebot.init(config)
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'bot', 'plugins'),
        'bot.plugins'
    )
    nonebot.run()
