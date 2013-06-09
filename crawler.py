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

def SoupCaption(currentPageUlr):
    caption = ''
    urlBase = "http://photography.nationalgeographic.com"
    captionFounded = False
    r = requests.get(urlBase + currentPageUlr)
    soup = BeautifulSoup(r.text)
    return str(soup.find(id="caption").find('h2'))


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
                print url
                linkFounded = True
    if linkFounded:
        return [True, url]
    else:
        print "Download link not found " + url
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
        print "Prev url not found for " + url
        return [False, ""]

def CrawlNatGeo(i):
    iterator = 0
    url = '/photography/photo-of-the-day/'

    while iterator < i:
        res = GetDownloadUrl(url)
        if res[0]:
            print 'Downloading ' + res[1]
            print 'Looking for caption'
            caption = SoupCaption(url)

            if len(caption) > 0:
                caption = caption[4:-5]
                caption = caption.replace(', ', '-')
                caption = caption.replace(' ', '_')
            else:
                caption = str(iterator)

            path = 'images/' + caption + '.jpg'
            if not os.path.exists(path):
                localFile = open(path, 'wb')
                localFile.write(requests.get(res[1]).content)
                localFile.close()
                iterator = iterator + 1
            else:
                print caption + '.jpg' + ' exists'
        else:
            print 'No download link. Looking for previoius page.'

        print 'Looking for previous page'
        res = GetPreviousPageUrl(url)
        if res[0]:
            print 'Prev found: ' + res[1]
            url = res[1]
        else:
            print 'Breaking!'
            break

    print 'End'



def main():
##    r = requests.get('https://github.com/timeline.json')
##    print(r.text)
    i = 0
    if len(sys.argv) > 1:
        i = int(sys.argv[1])
    else:
        i = 10

    if i < 100 and i > 0:
        CrawlNatGeo(i)
    else:
        print i



if __name__ == '__main__':
    main()


##GetPreviousPageUrl('/photography/photo-of-the-day/')
##        GetDownloadUrl('/photography/photo-of-the-day/bixby-bridge-california/')
##        localFile = open(iterator + '.jpg', 'wb')
##        localFile.write(requests.get('http://images.nationalgeographic.com/wpf/media-live/photos/000/679/cache/bixby-bridge-california_67923_990x742.jpg').content)
##        localFile.close()