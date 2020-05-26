#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys

from nonebot import CommandSession, on_command

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))))
from bot.plugins.leetcode.get_image import get_image


@on_command('leetcode', aliases=('算法',))
async def leetcode(session: CommandSession):
    question_id = session.get('question_id')
    image = await get_image(question_id)
    await session.send(image)


@leetcode.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if not stripped_arg:
        session.pause('想看哪一题呢？')
    else:
        if re.match(r'^\d{1,4}$', stripped_arg):
            session.state['question_id'] = stripped_arg
        else:
            session.pause('题号不正确哦，应该是 1-4 位数字，0 表示随机一题')

    session.state[session.current_key] = stripped_arg
