#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import re
from typing import Dict, List

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
    target_expire = database.retrieve(f'select expire from vocabulary_dk_group where group_id={group_id};')[0][0]
    if 'target_all_words' not in card_result:
        # 目标格式一：每日新词数 + 每日复习数
        target_new_words = card_result['target_new_words']
        target_old_words = card_result['target_old_words']
        if target_old_words == '自动':
            target_old_words = 0
        database.run(f"insert into vocabulary_dk_user"
                     f"(user_id, name, software, target_new_words, target_old_words, target_expire)"
                     f"values ({user_id}, '{name}', '{software}', "
                     f"{target_new_words}, {target_old_words}, '{target_expire}');")
    else:
        # 目标格式二：每日新旧单词总数
        target_all_words = card_result['target_all_words']
        database.run(f"insert into vocabulary_dk_user"
                     f"(user_id, name, software, target_all_words, target_expire)"
                     f"values ({user_id}, '{name}', '{software}', {target_all_words}, '{target_expire}');")


def update_user(group_id: int, user_id: int, card_result: Dict) -> None:
    name = card_result['name']
    software = card_result['software']
    target_expire = database.retrieve(f'select expire from vocabulary_dk_group where group_id={group_id};')[0][0]
    if 'target_all_words' not in card_result:
        # 目标格式一：每日新词数 + 每日复习数
        target_new_words = card_result['target_new_words']
        target_old_words = card_result['target_old_words']
        database.run(f"update vocabulary_dk_user "
                     f"set name='{name}', software='{software}', "
                     f"target_new_words={target_new_words}, "
                     f"target_old_words={target_old_words}, "
                     f"target_all_words=null, "
                     f"target_expire='{target_expire}' "
                     f"where user_id={user_id};")
    else:
        # 目标格式二：每日新旧单词总数
        target_all_words = card_result['target_all_words']
        database.run(f"update vocabulary_dk_user "
                     f"set name='{name}', software='{software}', "
                     f"target_new_words=null, "
                     f"target_old_words=null, "
                     f"target_all_words={target_all_words}, "
                     f"target_expire='{target_expire}' "
                     f"where user_id={user_id};")


def check_user(user_id: int, group_id: int, card: str) -> List:
    """
    检查用户
    - 如果是新用户，检查群名片格式
        - 如果格式不正确，返回 []
        - 如果格式正确，添加用户
    - 如果是老用户，检查目标是否过期
        - 如果目标过期，检查群名片格式
            - 如果格式不正确，返回 []
            - 如果格式正确，更新用户目标
    :param user_id: 用户 QQ 号
    :param group_id: 群聊 QQ 号
    :param card: 用户群名片
    :return: 如果群名片格式不正确，返回 []，其他情况返回用户信息 result，result 中字段顺序为：
             user_id, name, software, target_new_words, target_old_words, target_all_words, target_expire,
             today_new_words, today_old_words, today_all_words, today_expire, score, all_words, days
    """

    # 查数据库，获取目标
    result = database.retrieve(f'select user_id, name, software, '
                               f'target_new_words, target_old_words, target_all_words, target_expire, '
                               f'today_new_words, today_old_words, today_all_words, today_expire, '
                               f'score, all_words, days from vocabulary_dk_user where user_id={user_id};')

    if not result:
        # 如果是新用户，检查群名片格式
        card_result = read_card(card)
        if card_result['error']:
            # 如果格式不正确，返回 []
            return []
        # 如果格式正确，添加用户
        add_user(group_id, user_id, card_result)
        result = database.retrieve(f'select user_id, name, software, '
                                   f'target_new_words, target_old_words, target_all_words, target_expire, '
                                   f'today_new_words, today_old_words, today_all_words, today_expire, '
                                   f'score, all_words, days from vocabulary_dk_user where user_id={user_id};')
    else:
        # 如果是老用户，检查目标是否过期
        target_expire = result[0][6]
        target_expire = datetime.datetime.strptime(target_expire, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        if now > target_expire:
            # 如果目标过期，检查群名片格式
            card_result = read_card(card)
            if card_result['error']:
                # 如果格式不正确，返回 []
                return []
            # 如果格式正确，更新用户目标
            update_user(group_id, user_id, card_result)

    print(result)
    return result


def get_today_expire() -> datetime.datetime:
    """
    获取今日打卡的过期时间，即第二天凌晨四点
    :return: 今日打卡的过期时间
    """
    now = datetime.datetime.now()
    if now.hour > 4:
        now += datetime.timedelta(days=1)
    now = now.replace(hour=4, minute=0, second=0, microsecond=0)
    return now


def get_today_score(target_new_words: int, target_old_words: int, target_all_words: int,
                    today_new_words: int, today_old_words: int, today_all_words: int) -> int:
    """
    获取今日积分，达到目标得到 1 积分，没达到目标按实际数量除以目标数量再乘以 0.6 计算
    :param target_new_words: 目标新词数
    :param target_old_words: 目标复习数
    :param target_all_words: 目标总词数
    :param today_new_words: 今日新词数
    :param today_old_words: 今日复习数
    :param today_all_words: 今日总词数
    :return: 今日积分
    """
    if not target_all_words:
        # 目标格式一：每日新词数 + 每日复习数
        if today_new_words >= target_new_words and today_old_words >= target_old_words:
            today_score = 1
        else:
            if target_old_words:
                today_score = 0.6 * today_all_words / (target_new_words + target_old_words)
            else:
                today_score = 0.6 * today_new_words / target_new_words
    else:
        # 目标格式二：每日新旧单词总数
        if today_all_words >= target_all_words:
            today_score = 1
        else:
            today_score = 0.6 * today_all_words / target_all_words

    return today_score


def learn_more(today_new_words: int, today_old_words: int,
               t_new_words: int, t_old_words: int) -> bool:
    """
    判断是否比当日上次打卡多学了
    :param today_new_words: 上次打卡新词数
    :param today_old_words: 上次打卡复习数
    :param t_new_words: 本次打卡新词数
    :param t_old_words: 本次打卡复习数
    :return: 是否多学了
    """
    if t_new_words > today_new_words or t_old_words > today_old_words:
        return True
    else:
        return False
