import re  #regexp
import os  # filesystem


# Returns a string without non-letter characters
def remove_special_characters(text):
    result = re.sub(r'(&#039;)', '', text)
    result = re.sub(r'[^\w]', '', result)
    return result


def create_directory_if_not_exists(path):
    if not os.path.isdir(path):
        os.mkdir(path)