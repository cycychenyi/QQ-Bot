#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Dict

from utils import database


def read_card(card: str) -> Dict:
    # 群名片格式一：称呼 软件 每天新词数 每天复习数，比如：陈一 欧路 100 自动
    # 群名片格式二：昵称 软件 每日新旧单词总数，比如：陈一 欧路 300。
    # 目前可选软件包括：「欧路」、「墨墨」
    match_result = re.match(r'^(?P<name>.+) (?P<software>欧路|墨墨) '
                            r'(?P<target_new_words>\d+) (?P<target_old_words>\d+|自动)$', card)
    if match_result:
        return {
            'error': 0,
            'name': match_result.group('name'),
            'software': match_result.group('software'),
            'target_new_words': match_result.group('target_new_words'),
            'target_old_words': match_result.group('target_old_words')
        }
    else:
        match_result = re.match(r'^(?P<name>.+) (?P<software>欧路|墨墨) '
                                r'(?P<target_all_words>\d+)$', card)
        if match_result:
            return {
                'error': 0,
                'name': match_result.group('name'),
                'software': match_result.group('software'),
                'target_all_words': match_result.group('target_all_words')
            }
        else:
            return {
                'error': 1
            }


def add_user(group_id: int, user_id: int, card_result: Dict) -> None:
    name = card_result['name']
    software = card_result['software']
    expire = database.retrieve(f'select expire from vocabulary_dk_group where group_id={group_id};')[0][0]
    if 'target_all_words' not in card_result:
        # 目标格式一：每日新词数 + 每日复习数
        target_new_words = card_result['target_new_words']
        target_old_words = card_result['target_old_words']
        if target_old_words == '自动':
            target_old_words = 0
        database.run(f"insert into vocabulary_dk_user"
                     f"(user_id, name, software, target_new_words, target_old_words, expire)"
                     f"values ({user_id}, '{name}', '{software}', "
                     f"{target_new_words}, {target_old_words}, '{expire}');")
    else:
        # 目标格式二：每日新旧单词总数
        target_all_words = card_result['target_all_words']
        database.run(f"insert into vocabulary_dk_user"
                     f"(user_id, name, software, target_all_words, expire)"
                     f"values ({user_id}, '{name}', '{software}', {target_all_words}, '{expire}');")


def update_user(group_id: int, user_id: int, card_result: Dict) -> None:
    name = card_result['name']
    software = card_result['software']
    expire = database.retrieve(f'select expire from vocabulary_dk_group where group_id={group_id};')[0][0]
    if 'target_all_words' not in card_result:
        # 目标格式一：每日新词数 + 每日复习数
        target_new_words = card_result['target_new_words']
        target_old_words = card_result['target_old_words']
        database.run(f"update vocabulary_dk_user "
                     f"set name='{name}', software='{software}', "
                     f"target_new_words={target_new_words}, "
                     f"target_old_words={target_old_words}, "
                     f"target_all_words=null, "
                     f"expire='{expire}' "
                     f"where user_id={user_id};")
    else:
        # 目标格式二：每日新旧单词总数
        target_all_words = card_result['target_all_words']
        database.run(f"update vocabulary_dk_user "
                     f"set name='{name}', software='{software}', "
                     f"target_new_words=null, "
                     f"target_old_words=null, "
                     f"target_all_words={target_all_words}, "
                     f"expire='{expire}' "
                     f"where user_id={user_id};")
