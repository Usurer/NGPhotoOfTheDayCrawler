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
def GetArchivesPage(archiveUrl, index):
    if index > 1:
        archiveUrl = archiveUrl + '?page=' + str(index) + '&month=None'

    print ('Getting archive page ' + archiveUrl)
    archivePage = requests.get(archiveUrl)

    return archivePage


# As a result I'll have a list of photo pages' urls for photos located on the first page of Archive
def GetLinksToPhotoPages(archivePageContent):
    result = []

    # Addinf ? after * makes it non-greedy
    # DOTALL makes a newline be matched by *
    wrapperPattern = re.compile('(<div class="photo_info".*?</div>)', re.MULTILINE | re.DOTALL)

    # Use findall instead of search to get all matches
    matchResult = re.findall(wrapperPattern, archivePageContent.text)

    if not matchResult:
        return

    linkPattern = re.compile('<a href=".*"')

    for photoTeaserContent in matchResult:
        photoLinkMatch = re.search(linkPattern, photoTeaserContent)
        linkContent = photoLinkMatch.group(0)
        hrefPattern = re.compile('".*"')
        hrefMatchResult = re.search(hrefPattern, linkContent)
        url = hrefMatchResult.group(0)
        url = url.strip('"/')
        result.append(url)

    return result


# As a result I'll have an url for the photo
def GetLinkToPhoto(photoPageUrl):
    pageContents = requests.get(photoPageUrl).text
    twitterRegex = re.compile('<meta property="og:image" content="(?P<url>.*?)"/>', re.MULTILINE | re.DOTALL)
    match = re.search(twitterRegex, pageContents)
    if not match:
        return ''

    result = match.groupdict()['url']
    response = requests.get(result)
    if response.status_code == 200:
        return result
    else:
        print(result + ' code ' + response.status_code)


# As a result I'll have photo name
def GetPhotoName(pageContents):
    twitterMetaRegex = re.compile('<meta name="twitter:title" content="(?P<title>.*?)">', re.MULTILINE | re.DOTALL)
    match = re.search(twitterMetaRegex, pageContents)
    if not match:
        return ''

    return match.groupdict()['title']


def GetPhotoTimestamp(pageContents):
    twitterMetaRegex = re.compile('<meta property="article:published_time" content="(?P<date>.*?)T',
                                  re.MULTILINE | re.DOTALL)
    match = re.search(twitterMetaRegex, pageContents)
    if not match:
        return ''

    return match.groupdict()['date']


def DownloadUrlWithCaption(url, caption):
    imagesDirectory = 'images_2'
    utils.CreateDirectoryIfNotExists(imagesDirectory)
    path = imagesDirectory + '/' + caption + '.jpg'

    if not os.path.exists(path):
        localFile = open(path, 'wb')
        localFile.write(requests.get(url).content)
        localFile.close()


def DownloadPhotosFromArchivePage(archivePageIndex):
    photographyRootUrl = "http://photography.nationalgeographic.com/"
    archiveUrl = photographyRootUrl + "photography/photo-of-the-day/archive/"
    archivePage = GetArchivesPage(archiveUrl, archivePageIndex)
    photoPagesUrls = GetLinksToPhotoPages(archivePage)

    for url in photoPagesUrls:
        photoUrl = GetLinkToPhoto(photographyRootUrl + url)
        photoPageContent = requests.get(photographyRootUrl + url).text
        photoName = GetPhotoName(photoPageContent)
        photoName = utils.RemoveSpecialCharacters(photoName)
        photoTimestamp = GetPhotoTimestamp(photoPageContent)
        photoCaption = photoTimestamp + '_' + photoName

        if len(photoUrl) > 0 and len(photoCaption) > 0:
            print ('Downloading ' + photoCaption + ' from ' + photoUrl)
            DownloadUrlWithCaption(photoUrl, photoCaption)

    return


def main():
    for i in range(1, 100, 1):
        DownloadPhotosFromArchivePage(i)


if __name__ == '__main__':
    main()
