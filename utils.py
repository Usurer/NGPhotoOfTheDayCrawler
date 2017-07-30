import requests ## http crawler
import re ##regexp
import os ## filesystem
import sys


def RemoveSpecialCharacters(text):
    result = re.sub(r'(&#039;)', '', text)
    result = re.sub(r'[^\w]', '', result)
    return result


def CreateDirectoryIfNotExists(path):
    if not os.path.isdir(path):
        os.mkdir(path)