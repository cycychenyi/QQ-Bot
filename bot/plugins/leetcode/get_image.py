#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random

from private_config import coolq


async def get_image(question_id: str) -> str:
    images_dir = os.path.join(coolq['image_dir'], 'leetcode')
    if not int(question_id):
        image = random.sample(os.listdir(images_dir), 1)[0]
        file_path = os.path.join('leetcode', image)
        return f'[CQ:image,file={file_path}]'
    for image in os.listdir(images_dir):
        if int(question_id) == int(image[:4]):
            file_path = os.path.join('leetcode', image)
            return f'[CQ:image,file={file_path}]'
    else:
        return '[CQ:face,id=37] 没获取到题目，可能题号超出范围了，也可能这题是付费的'
