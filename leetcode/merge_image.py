#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np


class MergeImage(object):
    def __init__(self) -> None:
        self.__images_dir = ''
        self.__images = []
        self.__width = 0
        self.__height = 0
        self.__new_image_data = bytes()

    def __read_images(self) -> None:
        first_image = os.path.join(self.__images_dir, os.listdir(self.__images_dir)[0])
        image = cv2.imread(first_image)[:, :-10]
        self.__height, self.__width = image.shape[0], image.shape[1]
        print(self.__height, self.__width)
        for filename in os.listdir(self.__images_dir):
            file_path = os.path.join(self.__images_dir, filename)
            image = cv2.imread(file_path)[:, :-10]
            self.__images.append(image)

    def __find_first_different_line(self, first_image: bytes, second_image: bytes) -> int:
        head = second_image[:200, :]
        for i in range(self.__height - 200):
            tail = first_image[i:(i + 200), :]
            if (tail == head).all():
                return self.__height - i
        return 0

    def __merge_images(self) -> None:
        self.__new_image_data = self.__images[0]
        for i in range(len(self.__images) - 1):
            first_image = self.__images[i]
            second_image = self.__images[i + 1]
            start = self.__find_first_different_line(first_image, second_image)
            print(i + 1, start)
            self.__new_image_data = np.append(self.__new_image_data, self.__images[i + 1][start:, :], axis=0)

    def merge(self, images_dir: str, new_image_path: str) -> None:
        self.__images_dir = images_dir
        self.__read_images()
        self.__merge_images()
        cv2.imwrite(new_image_path, self.__new_image_data)
