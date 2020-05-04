#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nonebot import on_command, CommandSession, permission as perm


@on_command('face', aliases=('表情',), permission=perm.SUPERUSER)
async def weather(session: CommandSession):
    face_id = session.get('face_id')
    await session.send(f'[CQ:face,id={face_id}]')


@weather.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['face_id'] = stripped_arg
        return
