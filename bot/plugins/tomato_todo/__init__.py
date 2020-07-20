#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from nonebot import CommandSession, IntentCommand, NLPSession, on_command, on_natural_language
from nonebot.argparse import ArgumentParser

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))))
from utils import database
from private_config import coolq

ADMIN_USAGE = '''
番茄 Todo 管理

使用方法：
    tom | tomato_todo_admin | 番茄 | 番茄 Todo 管理 [OPTIONS]

OPTIONS：
    -h, --help  显示本使用帮助
    -a, --add  向「番茄 Todo」添加一个 QQ 群，需要 -g 参数
    -d, --delete  从「番茄 Todo」删除一个 QQ 群，需要 -g 参数
    -l, --list  列出所有「背单词打卡」里的 QQ 群信息
    -g GROUP_ID, --group-id GROUP_ID  QQ 群号
    -u PASSWORD, --update PASSWORD  更新自习室密码

注意：
    -a, -d, -l, -u 参数一次只能使用一个。
'''.strip()


@on_command('tom', aliases=('tomato_todo_admin', '番茄', '番茄 Todo 管理'), shell_like=True)
async def admin(session: CommandSession):
    """
    番茄管理，详见 ADMIN_USAGE
    :param session: 当前会话
    :return: 无
    """

    # 只对「番茄」管理员起作用
    user_id = session.ctx['sender']['user_id']
    if user_id not in coolq['tomato_todo_superusers']:
        return

    parser = ArgumentParser(session=session, usage=ADMIN_USAGE)
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-g', '--group-id')
    parser.add_argument('-u', '--update')

    args = parser.parse_args(session.argv)

    # 列出所有「番茄」里的 QQ 群信息
    if args.list:
        groups = database.retrieve('select group_id from tomato_todo_group;')
        result = [f'群号：{row[0]}' for row in groups]
        if not result:
            message = '「番茄 Todo」当前没有 QQ 群'
        else:
            message = '「番茄 Todo」的所有 QQ 群：\n' + '\n'.join(result)
        result = database.retrieve('select password from tomato_todo_info;')
        if not result:
            message += '\n当前尚未设置自习室密码'
        else:
            message += f'\n自习室密码：{result[0][0]}'
        await session.send(message)
        return

    # 向「番茄」添加一个 QQ 群，需要 -g 参数
    if args.add:
        if not args.group_id:
            await session.send('缺少 -g 参数')
            return
        rowcount = database.run(f"insert into tomato_todo_group (group_id) values ({args.group_id});")
        if rowcount == 1:
            await session.send('添加成功')
        return

    # 从「番茄」删除一个 QQ 群，需要 -g 参数
    if args.delete:
        if not args.group_id:
            await session.send('缺少 -g 参数')
            return
        rowcount = database.run(f'delete from tomato_todo_group where group_id={args.group_id};')
        if not rowcount:
            await session.send(f'「番茄」里没有 {args.group_id}')
        elif rowcount == 1:
            await session.send('删除成功')
        return

    if args.update:
        result = database.retrieve('select password from tomato_todo_info;')
        if not result:
            rowcount = database.run(f'insert into tomato_todo_info (password) values ({args.update});')
            if rowcount == 1:
                await session.send('设置成功')
        else:
            rowcount = database.run(f'update tomato_todo_info set password={args.update} where password is not null;')
            if rowcount == 1:
                await session.send('更新成功')


@on_command('password', aliases=('pass', '密码'), only_to_me=False)
async def password(session: CommandSession):
    """
    答复密码
    :param session: 当前会话
    :return: 无
    """
    user_id = session.ctx['sender']['user_id']
    result = database.retrieve('select password from tomato_todo_info;')
    if result:
        await session.send(f'[CQ:at,qq={user_id}] 自习室密码：{result[0][0]}，要加油噢~')


@on_natural_language(keywords={'密码'}, only_to_me=False)
async def _(session: NLPSession):
    """
    识别密码命令
    :param session: 当前会话
    :return: 如果是「番茄」里的群聊的「密码」命令，调用 password 命令，否则不处理
    """

    groups = database.retrieve('select group_id from tomato_todo_group;')
    # 1. 不处理私聊消息
    if 'group_id' not in session.ctx:
        return
    # 2. 不处理未注册的群聊中的消息
    if (session.ctx['group_id'],) not in groups:
        return

    return IntentCommand(90.0, 'password')
