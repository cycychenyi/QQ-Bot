#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
import sys
from typing import Dict
from urllib.parse import quote

import requests

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))))
from private_config import baidu_ocr, iocr_templates


def auth() -> str:
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&' \
           f'client_id={baidu_ocr["api_key"]}&client_secret={baidu_ocr["secret_key"]}'
    response = requests.get(host).json()
    return response['access_token']


def iocr(image_url: str, template: str) -> Dict:
    result = {
        'match': False,
        'new_words': -1,
        'old_words': -1
    }
    access_token = auth()

    recognise_api_url = 'https://aip.baidubce.com/rest/2.0/solution/v1/iocr/recognise'
    template_sign = iocr_templates[template]
    image_data = requests.get(image_url).content
    image_b64 = base64.b64encode(image_data).decode().replace('\r', '')
    recognise_body = f'access_token={access_token}&templateSign={template_sign}&' \
                     f'image={quote(image_b64.encode("utf8"))}'
    response = requests.post(recognise_api_url, data=recognise_body).json()
    if not response['error_code']:
        ret = response['data']['ret']
        for each in ret:
            if each['word_name'] == 'new_words':
                result['new_words'] = each['word']
            elif each['word_name'] == 'old_words':
                result['old_words'] = each['word']
        if result['new_words'] and result['old_words']:
            result['match'] = True

    return result
