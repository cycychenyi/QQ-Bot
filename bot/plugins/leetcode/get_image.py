#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from private_config import coolq_image_dir


async def get_image(question_id: str) -> str:
    images_dir = os.path.join(coolq_image_dir, 'leetcode')
    for image in os.listdir(images_dir):
        if int(question_id) == int(image[:4]):
            file_path = os.path.join('leetcode', image)
            return f'[CQ:image,file={file_path}]'
    else:
        return '[CQ:face,id=37] 没获取到题目，可能题号超出范围了，也可能这题是付费的'
