# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Usurer
#
# Created:     09/06/2013
# Copyright:   (c) Usurer 2013
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import requests  ## http crawler
import re  ##regexp
import os  ## filesystem
import sys

import utils


# As a result I'll have the HTML of archives page
def get_archives_page(archive_url, index):
    if index > 1:
        archive_url = archive_url + '?page=' + str(index) + '&month=None'

    print ('Getting archive page ' + archive_url)
    archive_page = requests.get(archive_url)

    return archive_page


# As a result I'll have a list of photo pages' urls for photos located on the first page of Archive
def get_links_to_photo_pages(archivePageContent):
    result = []

    # Adding ? after * makes it non-greedy
    # DOTALL makes a newline be matched by *
    wrapper_pattern = re.compile('(<div class="photo_info".*?</div>)', re.MULTILINE | re.DOTALL)

    # Use findall instead of search to get all matches
    match_result = re.findall(wrapper_pattern, archivePageContent.text)

    if not match_result:
        return

    link_pattern = re.compile('<a href=".*"')

    for photoTeaserContent in match_result:
        photo_link_match = re.search(link_pattern, photoTeaserContent)
        link_content = photo_link_match.group(0)
        href_pattern = re.compile('".*"')
        href_match_result = re.search(href_pattern, link_content)
        url = href_match_result.group(0)
        url = url.strip('"/')
        result.append(url)

    return result


# As a result I'll have an url for the photo
def get_link_to_photo(photoPageUrl):
    page_contents = requests.get(photoPageUrl).text
    twitter_regex = re.compile('<meta property="og:image" content="(?P<url>.*?)"/>', re.MULTILINE | re.DOTALL)
    match = re.search(twitter_regex, page_contents)
    if not match:
        return ''

    result = match.groupdict()['url']
    response = requests.get(result)
    if response.status_code == 200:
        return result
    else:
        print(result + ' code ' + response.status_code)


# As a result I'll have photo name
def get_photo_name(pageContents):
    twitter_meta_regex = re.compile('<meta name="twitter:title" content="(?P<title>.*?)">', re.MULTILINE | re.DOTALL)
    match = re.search(twitter_meta_regex, pageContents)
    if not match:
        return ''

    return match.groupdict()['title']


def get_photo_timestamp(pageContents):
    twitter_meta_regex = re.compile('<meta property="article:published_time" content="(?P<date>.*?)T',
                                  re.MULTILINE | re.DOTALL)
    match = re.search(twitter_meta_regex, pageContents)
    if not match:
        return ''

    return match.groupdict()['date']


def download_url_with_caption(url, caption):
    images_directory = 'images_2'
    utils.CreateDirectoryIfNotExists(images_directory)
    path = images_directory + '/' + caption + '.jpg'

    if not os.path.exists(path):
        local_file = open(path, 'wb')
        local_file.write(requests.get(url).content)
        local_file.close()


def download_photos_from_archive_page(archivePageIndex):
    photography_root_url = "http://photography.nationalgeographic.com/"
    archive_url = photography_root_url + "photography/photo-of-the-day/archive/"
    archive_page = get_archives_page(archive_url, archivePageIndex)
    photo_pages_urls = get_links_to_photo_pages(archive_page)

    for url in photo_pages_urls:
        photo_url = get_link_to_photo(photography_root_url + url)
        photo_page_content = requests.get(photography_root_url + url).text
        photo_name = get_photo_name(photo_page_content)
        photo_name = utils.RemoveSpecialCharacters(photo_name)
        photo_timestamp = get_photo_timestamp(photo_page_content)
        photo_caption = photo_timestamp + '_' + photo_name

        if len(photo_url) > 0 and len(photo_caption) > 0:
            print ('Downloading ' + photo_caption + ' from ' + photo_url)
            download_url_with_caption(photo_url, photo_caption)

    return


def main():
    for i in range(1, 100, 1):
        download_photos_from_archive_page(i)


if __name__ == '__main__':
    main()
