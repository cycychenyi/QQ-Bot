#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform

# CoolQ
if 'Windows' in platform.platform():
    coolq_image_dir = '***/酷Q Pro/data/image'
else:
    coolq_image_dir = '***/coolq/data/image'
coolq = {
    'superusers': {123456},
    'tomato_todo_superusers': {123456},
    'test_users': {123456},
    'image_dir': coolq_image_dir
}

# LeetCode
leetcode = {
    'leetcode_username': '***',
    'leetcode_password': '***'
}

# 百度文字识别
baidu_ocr = {
    'app_id': '***',
    'api_key': '***',
    'secret_key': '***'
}

# 背单词打卡 iOCR 模板
iocr_templates = {
    '墨墨': '***',
    '欧路': '***'
}

# Redis
redis = {
    'password': '***'
}
