#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil
import time
from typing import Dict

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

from private_config import leetcode
from leetcode.merge_image import MergeImage

problems_all_url = 'https://leetcode.com/api/problems/all/'
problems_base_url = 'https://leetcode.com/problems/'
login_url = 'https://leetcode.com/accounts/login'
screenshots_dir = 'screenshots'
images_dir = 'images'


def get_urls() -> Dict[int, str]:
    # 获取所有题目的 title slug，拼接成 url
    # response = requests.get(problems_all_url)
    with open('temp.txt', 'r') as f:
        text = f.read()
    data = json.loads(text)
    questions = data['stat_status_pairs']
    question_urls = {}
    for question in questions:
        paid_only = question['paid_only']
        if not paid_only:
            question_id = question['stat']['question_id']
            question__title_slug = question['stat']['question__title_slug']
            question_urls[question_id] = question__title_slug
    return question_urls


def init_driver() -> webdriver.Chrome:
    # 初始化 driver
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=http://202.20.16.82:10152')
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    driver.implicitly_wait(3)
    return driver


def login(driver: webdriver.Chrome) -> None:
    # 登录
    driver.get(login_url)
    username = driver.find_element_by_xpath('//*[@id="id_login"]')
    username.send_keys(leetcode['leetcode_username'])
    password = driver.find_element_by_xpath('//*[@id="id_password"]')
    password.send_keys(leetcode['leetcode_password'])
    sign_in = driver.find_element_by_xpath('//*[@id="signin_btn"]')
    driver.execute_script('arguments[0].click();', sign_in)
    time.sleep(1)


def get_screenshots(driver: webdriver.Chrome, question_url: str) -> None:
    driver.get(question_url)
    time.sleep(1)
    split_bar = driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/div[1]/div/div[2]/div')
    ActionChains(driver).drag_and_drop_by_offset(split_bar, 100, 0).perform()
    time.sleep(1)
    # try:
    #     # 关闭弹窗
    #     close = driver.find_element_by_xpath('//*[@id="rcDialogTitle0"]/div/svg')
    #     close.click()
    # except NoSuchElementException as e:
    #     print('没有弹窗')
    #     print(e)
    ActionChains(driver).move_by_offset(600, 400).click().perform()
    time.sleep(3)
    editor = driver.find_element_by_xpath(
        '//*[@id="app"]/div/div[3]/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[6]/div[1]/div/div/div/div[5]'
    )
    editor.click()
    related_topics = driver.find_element_by_xpath(
        '//*[@id="app"]/div/div[3]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[6]/div[1]/div/div'
    )
    related_topics.click()
    question_description = driver.find_element_by_xpath(
        '//*[@id="app"]/div/div[3]/div[1]/div/div[1]/div/div[1]/div[1]/div/div[2]/div'
    )
    time.sleep(1)
    images = []
    index = 0
    while True:
        script = f"document.getElementsByClassName('description__24sA')[0].scrollTop = {300 * index};"
        driver.execute_script(script)
        image = question_description.screenshot_as_png
        if image == images[-1]:
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


def get_image(driver: webdriver.Chrome, question__title_slug: str) -> None:
    question_url = problems_base_url + question__title_slug
    print(question_url)
    while True:
        try:
            get_screenshots(driver, question_url)
            break
        except NoSuchElementException as e:
            print('可能是没有分割条')
            print(e)
    merge_image = MergeImage()
    image_path = os.path.join(images_dir, '{:0>4d}-{}.png'.format(question_id, question__title_slug))
    merge_image.merge(screenshots_dir, image_path)
    # # 删除截图文件夹
    # if os.path.exists(screenshots_dir):
    #     shutil.rmtree(screenshots_dir)


def get_images():
    # 获取所有题目的 title slug，拼接成 url
    question_urls = get_urls()
    # 初始化 driver
    driver = init_driver()
    # 登录
    login(driver)

    # 为所有题目截图
    for question_id, question__title_slug in question_urls.items():
        get_image(driver, question__title_slug)


if __name__ == '__main__':
    get_images()
