#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import sys

from nonebot import CommandSession, IntentCommand, NLPSession, NoticeSession, on_command, on_natural_language, \
    on_notice, permission as perm
from nonebot.argparse import ArgumentParser

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))))
from utils import database
from bot.plugins.vocabulary_dk.iocr import iocr
from bot.plugins.vocabulary_dk.vocabulary_dk_utils import read_card, add_user, update_user, check_user, \
    get_today_expire, get_today_score, learn_more

ADMIN_USAGE = '''
背单词打卡管理

使用方法：
    voc | vocabulary_dk_admin | 背单词 | 背单词打卡管理 [OPTIONS]

OPTIONS：
    -h, --help  显示本使用帮助
    -a, --add  向「背单词打卡」添加一个 QQ 群，需要 -g 和 -e 参数
    -d, --delete  从「背单词打卡」删除一个 QQ 群，需要 -g 参数
    -l, --list  列出所有「背单词打卡」里的 QQ 群信息
    -g GROUP_ID, --group-id GROUP_ID  QQ 群号
    -e EXPIRE_TIME, --expire EXPIRE_TIME  该周期结束时间，格式为 %Y-%m-%dT%H:%M:%S

注意：
    -a, -d, -l 参数一次只能使用一个。
'''.strip()
INFO_USAGE = '''
背单词打卡 > 个人信息

使用方法：
    info | information | 信息 | 个人信息 [OPTIONS]

OPTIONS：
    <无>  查看积分、总词数、连续天数
    help, 帮助  显示本使用帮助
    all, 完整  显示完整个人信息
    <字段名>  查看指定字段

注意：
    字段包括：
        QQ（user_id）
        称呼（name）
        软件（software）
        目标新词数（target_new_words）
        目标复习数（target_old_words）
        目标总词数（target_all_words）
        积分（score）
        总词数（all_words）
        连续天数（days）
        目标过期时间（target_expire）
'''.strip()


@on_command('voc', aliases=('vocabulary_dk_admin', '背单词', '背单词打卡管理'),
            permission=perm.SUPERUSER, shell_like=True)
async def admin(session: CommandSession):
    """
    背单词打卡管理，详见 ADMIN_USAGE
    :param session: 当前会话
    :return: 无
    """

    parser = ArgumentParser(session=session, usage=ADMIN_USAGE)
    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-g', '--group-id')
    parser.add_argument('-e', '--expire')

    args = parser.parse_args(session.argv)

    # 列出所有「背单词打卡」里的 QQ 群信息
    if args.list:
        groups = database.retrieve('select group_id, expire from vocabulary_dk_group;')
        result = [f'群号：{row[0]} 该周期结束时间：{row[1]}' for row in groups]
        if not result:
            await session.send('「背单词打卡」当前没有 QQ 群')
        else:
            await session.send('「背单词打卡」的所有 QQ 群：\n' + '\n'.join(result))
        return

    # 向「背单词打卡」添加一个 QQ 群，需要 -g 和 -e 参数
    if args.add:
        if not args.group_id:
            await session.send('缺少 -g 参数')
            return
        if not args.expire:
            await session.send('缺少 -e 参数')
            return
        try:
            datetime.datetime.strptime(args.expire, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            await session.send('-e 参数格式不正确，应为 %Y-%m-%dT%H:%M:%S')
            return
        expire = args.expire.replace('T', ' ')
        rowcount = database.run(f"insert into vocabulary_dk_group (group_id, expire) "
                                f"values ({args.group_id}, '{expire}');")
        if rowcount == 1:
            await session.send('添加成功')
        return

    # 从「背单词打卡」删除一个 QQ 群，需要 -g 参数
    if args.delete:
        if not args.group_id:
            await session.send('缺少 -g 参数')
            return
        rowcount = database.run(f'delete from vocabulary_dk_group where group_id={args.group_id};')
        if not rowcount:
            await session.send(f'「背单词打卡」里没有 {args.group_id}')
        elif rowcount == 1:
            await session.send('删除成功')
        return


@on_notice('group_increase')
async def group_increase(session: NoticeSession):
    """
    新人进群时提醒修改群名片
    :param session: 当前会话
    :return: 无
    """

    groups = database.retrieve('select group_id from vocabulary_dk_group;')
    if (session.ctx['group_id'],) not in groups:
        return
    await session.send(f'欢迎 [CQ:at,qq={session.ctx["user_id"]}] ！'
                       f'上一期成员请查看成员公告，新人请查看新人公告，记得修改群名片哈~')


@on_command('dk')
async def dk(session: CommandSession):
    """
    根据用户使用的软件模板，对图片进行匹配，如果匹配则返回积分等信息
    如果是表情包之类的非打卡图片则不返回任何信息
    一天内多次打卡取最高值
    :param session: 当前会话
    :return: 无
    """

    groups = database.retrieve('select group_id from vocabulary_dk_group;')
    # 1. 不处理私聊消息
    if 'group_id' not in session.ctx:
        return
    # 2. 不处理未注册的群聊中的消息
    if (session.ctx['group_id'],) not in groups:
        return

    group_id = session.ctx['group_id']
    user_id = session.ctx['sender']['user_id']
    card = session.ctx['sender']['card']
    image_url = session.get('image_url')

    result = check_user(user_id, group_id, card)
    if not result:
        await session.send(f'[CQ:at,qq={user_id}] 群名片格式不对哦，请修改后重新打卡')
        return

    (user_id, name, software, target_new_words, target_old_words, target_all_words, target_expire,
     today_new_words, today_old_words, today_all_words, today_expire, score, all_words, days) = result[0]

    if today_expire:
        today_expire = datetime.datetime.strptime(today_expire, '%Y-%m-%d %H:%M:%S')

    print(result[0])

    # 根据软件模板识别图片
    iocr_result = iocr(image_url, software)
    print(iocr_result)
    if iocr_result['match']:
        # 如果匹配，执行以下操作，否则忽略
        # 有些情况会多识别出句点，如把「52」识别为「52.」
        t_new_words = int(iocr_result['new_words'].replace('.', ''))
        t_old_words = int(iocr_result['old_words'].replace('.', ''))
        t_all_words = t_new_words + t_old_words

        if today_expire and today_expire > datetime.datetime.now() and \
                not learn_more(today_new_words, today_old_words, t_new_words, t_old_words):
            # 如果比当日上次打卡少，则忽略
            return

        if not today_expire or today_expire < datetime.datetime.now():
            # 如果 today_expire 未设置（从未打卡）或未过期（今日尚未打卡），则进行积分和总词数的累加
            # 该操作与后一种情况合并了
            pass

        if today_expire and today_expire > datetime.datetime.now() and \
                learn_more(today_new_words, today_old_words, t_new_words, t_old_words):
            # 如果比当日上次打卡多，则取最高值（扣掉上次，再加上本次）
            if (all_words - today_all_words) // 1000 < all_words // 1000:
                score -= 1
            all_words -= today_all_words
            old_score = get_today_score(target_new_words, target_old_words, target_all_words,
                                        today_new_words, today_old_words, today_all_words)
            score -= old_score

        # 总词数（新词数 + 复习数）每增加 1000 获得 1 分，每日上限 1 分
        if (all_words + t_all_words) // 1000 > all_words // 1000:
            score += 1
        all_words += t_all_words
        today_score = get_today_score(target_new_words, target_old_words, target_all_words,
                                      t_new_words, t_old_words, t_all_words)
        score += today_score
        today_expire = get_today_expire().strftime('%Y-%m-%d %H:%M:%S')

        # 更新数据库
        rowcount = database.run(f"update vocabulary_dk_user "
                                f"set score={score}, all_words={all_words}, "
                                f"today_new_words={t_new_words}, today_old_words={t_old_words}, "
                                f"today_all_words={t_all_words}, today_expire='{today_expire}'"
                                f"where user_id={user_id};")
        # 消息提示
        if rowcount:
            score = format(round(score, 2), ',')
            all_words = format(all_words, ',')
            await session.send(f'[CQ:at,qq={user_id}]\n当前积分：{score}\n总词数：{all_words}\n继续加油！')


@dk.args_parser
async def _(session: CommandSession):
    """
    dk 命令的参数解析器，将 image_url 设置为自然语言接口传过来的当前参数
    :param session: 当前会话
    :return: 无
    """

    session.state['image_url'] = session.current_arg_text


@on_command('info', aliases=('information', '信息', '个人信息'), only_to_me=False)
async def info(session: CommandSession):
    """
    个人信息，详见 INFO_USAGE
    :param session: 当前会话
    :return: 无
    """

    groups = database.retrieve('select group_id from vocabulary_dk_group;')
    # 1. 不处理私聊消息
    if 'group_id' not in session.ctx:
        return
    # 2. 不处理未注册的群聊中的消息
    if (session.ctx['group_id'],) not in groups:
        return

    user_id = session.ctx['sender']['user_id']
    field_name = session.current_arg_text.strip()

    result = check_user(user_id, session.ctx['group_id'], session.ctx['sender']['card'])
    if not result:
        await session.send(f'[CQ:at,qq={user_id}] 群名片格式不对哦，请修改后重新查询')
        return

    (user_id, name, software, target_new_words, target_old_words, target_all_words, target_expire,
     today_new_words, today_old_words, today_all_words, today_expire, score, all_words, days) = result[0]

    # 如果没有参数，则列出积分、总词数
    if not field_name:
        await session.send(f'[CQ:at,qq={user_id}]\n当前积分：{score}\n总词数：{all_words}\n')
        return

    # TODO: 今天背单词数，四个新字段
    if field_name in {'help', '帮助'}:
        message = '\n' + INFO_USAGE
    elif field_name in {'all', '完整'}:
        message = f'QQ：{user_id}\n' \
                  f'称呼：{name}\n' \
                  f'软件：{software}\n' \
                  f'目标新词数：{target_new_words}\n' \
                  f'目标复习数：{target_old_words}\n' \
                  f'目标总词数：{target_all_words}\n' \
                  f'积分：{score}\n' \
                  f'总词数：{all_words}\n' \
                  f'连续天数：{days}\n' \
                  f'目标过期时间：{target_expire}'
    elif field_name in {'user_id', 'QQ'}:
        message = f'QQ：{user_id}'
    elif field_name in {'name', '称呼'}:
        message = f'称呼：{name}'
    elif field_name in {'software', '软件'}:
        message = f'软件：{software}'
    elif field_name in {'target_new_words', '目标新词数'}:
        message = f'目标新词数：{target_new_words}'
    elif field_name in {'target_old_words', '目标复习数'}:
        message = f'目标复习数：{target_old_words}'
    elif field_name in {'target_all_words', '目标总词数'}:
        message = f'目标总词数：{target_all_words}'
    elif field_name in {'score', '积分'}:
        message = f'积分：{score}'
    elif field_name in {'all_words', '总词数'}:
        message = f'总词数：{all_words}'
    elif field_name in {'days', '连续天数'}:
        message = f'连续天数：{days}'
    elif field_name in {'target_expire', '目标过期时间'}:
        message = f'目标过期时间：{target_expire}'
    else:
        message = ''

    await session.send(f'[CQ:at,qq={user_id}]\n' + message)


@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    """
    将「背单词打卡」里的群聊的图片消息当作 dk 命令，dk 命令里进行识别
    :param session: 当前会话
    :return: 如果是「背单词打卡」里的群聊的图片消息，调用 dk 命令，否则不处理
    """

    groups = database.retrieve('select group_id from vocabulary_dk_group;')
    # 1. 不处理私聊消息
    if 'group_id' not in session.ctx:
        return
    # 2. 不处理未注册的群聊中的消息
    if (session.ctx['group_id'],) not in groups:
        return
    # 3. 不处理没有图片的消息
    if not session.msg_images:
        return

    return IntentCommand(90.0, 'dk', current_arg=session.msg_images[0])
