#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nonebot import CommandSession, on_command, permission as perm


@on_command('face', aliases=('表情',), permission=perm.SUPERUSER)
async def face(session: CommandSession):
    face_id = session.get('face_id')
    await session.send(f'[CQ:face,id={face_id}]')


@face.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['face_id'] = stripped_arg
        return
