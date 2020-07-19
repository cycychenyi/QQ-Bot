#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from typing import List, Tuple

database_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'qq_bot.sqlite')


def retrieve(statement: str) -> List[Tuple]:
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute(statement)
    result = cursor.fetchall()
    return result


def run(statement: str) -> int:
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()
    cursor.execute(statement)
    rowcount = cursor.rowcount
    cursor.close()
    connection.commit()
    connection.close()
    return rowcount
