#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import os
import shutil
import time
from typing import Dict
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

from private_config import leetcode
from leetcode.merge_image import MergeImage

problems_all_url = 'https://leetcode.com/api/problems/all/'
problems_base_url = 'https://leetcode.com/problems/'
login_url = 'https://leetcode.com/accounts/login'
screenshots_dir = 'screenshots'
images_dir = 'images'


def log(message: str) -> None:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{now}]: {message}')


def get_title_slugs() -> Dict[int, str]:
    # 获取所有题目的 title slug，拼接成 url
    log('正在获取所有图片的 title slug...')
    response = requests.get(problems_all_url)
    data = json.loads(response.text)
    questions = data['stat_status_pairs']
    question_urls = {}
    for question in questions:
        paid_only = question['paid_only']
        if not paid_only:
            question_id = question['stat']['frontend_question_id']
            question__title_slug = question['stat']['question__title_slug']
            question_urls[question_id] = question__title_slug
    log('成功获取所有图片的 title slug')
    return question_urls


def init_driver() -> webdriver.Chrome:
    # 初始化 driver
    log('正在初始化 driver...')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    driver.implicitly_wait(3)
    log('成功初始化 driver')
    return driver


def login(driver: webdriver.Chrome) -> None:
    # 登录
    log('尝试登录 LeetCode...')
    driver.get(login_url)
    username = driver.find_element_by_xpath('//*[@id="id_login"]')
    username.send_keys(leetcode['leetcode_username'])
    password = driver.find_element_by_xpath('//*[@id="id_password"]')
    password.send_keys(leetcode['leetcode_password'])
    sign_in = driver.find_element_by_xpath('//*[@id="signin_btn"]')
    driver.execute_script('arguments[0].click();', sign_in)
    log('成功登录 LeetCode')
    time.sleep(1)


def get_screenshots(driver: webdriver.Chrome, question_url: str) -> None:
    # 获取一个题目的所有截图
    driver.get(question_url)
    # time.sleep(1)
    split_bar = driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/div[1]/div/div[2]/div')
    ActionChains(driver).drag_and_drop_by_offset(split_bar, 100, 0).perform()
    # time.sleep(1)
    related_topics = driver.find_element_by_class_name('header__2RZv')
    related_topics.click()
    question_description = driver.find_element_by_xpath(
        '//*[@id="app"]/div/div[3]/div[1]/div/div[1]/div/div[1]/div[1]/div/div[2]/div'
    )
    # time.sleep(1)
    images = []
    index = 0
    while True:
        script = f"document.getElementsByClassName('description__24sA')[0].scrollTop = {300 * index};"
        driver.execute_script(script)
        image = question_description.screenshot_as_png
        if images and image == images[-1]:
            break
        else:
            images.append(image)
            index += 1

    # 新建文件夹，存放截图
    if not os.path.exists(screenshots_dir):
        os.mkdir(screenshots_dir)
    for i in range(len(images)):
        with open(os.path.join(screenshots_dir, f'{i}.png'), 'wb') as f:
            f.write(images[i])


def get_image(driver: webdriver.Chrome, question_id: int, question__title_slug: str) -> None:
    # 获取一个题目的图片
    log(f'正在获取 {question_id} {question__title_slug} 的图片...')
    question_url = problems_base_url + question__title_slug
    log(f'题目地址为 {question_url}')
    while True:
        try:
            log(f'正在获取 {question_id} {question__title_slug} 的截图...')
            get_screenshots(driver, question_url)
            log(f'成功获取 {question_id} {question__title_slug} 的截图')
            break
        except NoSuchElementException as e:
            log('可能是跳转到中文网站，导致没有分割条')
            log(str(e))
        except WebDriverException as e:
            log('可能是还没加载完，导致 relate_topics 还无法点击')
            log(str(e))

    log('正在拼接图片...')
    merge_image = MergeImage()
    image_path = os.path.join(images_dir, '{:0>4d}-{}.png'.format(question_id, question__title_slug))
    merge_image.merge(screenshots_dir, image_path)
    log('成功拼接图片')

    # 删除截图文件夹
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    log(f'成功获取 {question_id} {question__title_slug} 的图片')


def get_images():
    # 获取所有题目的 title slug
    question_title_slugs = get_title_slugs()
    # 初始化 driver
    driver = init_driver()
    # 登录
    login(driver)

    # 为所有题目截图
    for question_id, question__title_slug in question_title_slugs.items():
        get_image(driver, question_id, question__title_slug)


if __name__ == '__main__':
    get_images()
