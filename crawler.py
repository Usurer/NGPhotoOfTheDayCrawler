#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Usurer
#
# Created:     09/06/2013
# Copyright:   (c) Usurer 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import requests ## http crawler
import re ##regexp
import os ## filesystem
from bs4 import BeautifulSoup
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
    twitterMetaRegex = re.compile('<meta property="article:published_time" content="(?P<date>.*?)T', re.MULTILINE | re.DOTALL)
    match = re.search(twitterMetaRegex, pageContents)
    if not match:
        return ''

    return match.groupdict()['date']

# END NEW

def GetDownloadUrl(currentPageUlr):
    url = currentPageUlr
    urlBase = "http://photography.nationalgeographic.com"
    linkFounded = False
    r = requests.get(urlBase + currentPageUlr)
    pattern = re.compile('<div class="download_link".*</div>')
    matchResult = re.search(pattern, r.text)
    linkFounded = False

    if matchResult:
        g =  matchResult.group(0)
        innerPattern = re.compile('<a href=".*"')
        matchResult = re.search(innerPattern, g)

        if matchResult:
            g =  matchResult.group(0)
            innerPattern = re.compile('".*"')
            matchResult = re.search(innerPattern, g)
            if matchResult:
                url = matchResult.group(0)
                url = url[1:-1]
                print(url)
                linkFounded = True
    if linkFounded:
        return [True, url]
    else:
        print("Download link not found " + url)
        return [False, ""]

def GetPreviousPageUrl(currentPageUlr):
    url = currentPageUlr
    urlBase = "http://photography.nationalgeographic.com"
    prevFounded = False
    r = requests.get(urlBase + currentPageUlr)
    pattern = re.compile('class="prev .*</p>')
    matchResult = re.search(pattern, r.text)
    prevFounded = False

    if matchResult:
        g =  matchResult.group(0)
        innerPattern = re.compile('<a href=".*"')
        matchResult = re.search(innerPattern, g)

        if matchResult:
            g =  matchResult.group(0)
            innerPattern = re.compile('".*"')
            matchResult = re.search(innerPattern, g)

            if matchResult:
                url = matchResult.group(0)
                url = url[1:-1]
                prevFounded = True
    if prevFounded:
        return [True, url]
    else:
        print("Prev url not found for " + url)
        return [False, ""]

def CrawlNatGeo(i):
    iterator = 0
    url = '/photography/photo-of-the-day/'

    while iterator < i:
        res = GetDownloadUrl(url)
        if res[0]:
            print('Downloading ' + res[1])
            print('Looking for caption')
            caption = SoupCaption(url)

            if len(caption) > 0:
                caption = caption[4:-5]
                caption = caption.replace(', ', '-')
                caption = caption.replace(' ', '')
            else:
                caption = str(iterator)

            date = SoupDate(url)
            if len(date) > 0:
                date = date.replace(' ', '_')
                date = date.replace(',', '')
            else:
                date = ''

            path = 'images_2/' + caption + '-' + date + '.jpg'
            if not os.path.exists(path):
                localFile = open(path, 'wb')
                localFile.write(requests.get(res[1]).content)
                localFile.close()
                iterator = iterator + 1
            else:
                print(caption + '.jpg' + ' exists')
        else:
            print('No download link. Looking for previoius page.')

        print('Looking for previous page')
        res = GetPreviousPageUrl(url)
        if res[0]:
            print('Prev found: ' + res[1])
            url = res[1]
        else:
            print('Breaking!')
            break

    print('End')


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