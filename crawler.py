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

# Yes - there are global variables and I don't fuckin' care!
photosToDownload = 0
folderToStore = 'images'
formats = ['NG_YYYYMMDD_[NAME]', 'YYYYMMDD_[NAME]']
selectedFormat = formats[0]

def SoupCaption(currentPageUlr):
    caption = ''
    urlBase = "http://photography.nationalgeographic.com"
    captionFounded = False
    r = requests.get(urlBase + currentPageUlr)
    soup = BeautifulSoup(r.text)
    return str(soup.find(id="caption").find('h2'))

def SoupDate(currentPageUlr):
    caption = ''
    urlBase = "http://photography.nationalgeographic.com"
    captionFounded = False
    r = requests.get(urlBase + currentPageUlr)
    soup = BeautifulSoup(r.text)
    return str(soup.find(id="caption").find(class_='publication_time').get_text())

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
        
def getDateFromString(dateString):
    regDay = re.compile('[^0-9]{1,}[0-9]{1,2}[^0-9]{1}')
    regYear = re.compile('[0-9]{4}')
    regMonth = re.compile('[a-zA-Z]{3,}')
    day = re.search(regDay, dateString).group(0)
    year = re.search(regYear, dateString).group(0)
    month = re.search(regMonth, dateString).group(0)
    if month.lower() == 'january':
        month = '01'    
    elif month.lower() == 'february':
        month = '02'
    elif month.lower() == 'march':
        month = '03'
    elif month.lower() == 'april':
        month = '04'
    elif month.lower() == 'may':
        month = '05'
    elif month.lower() == 'june':
        month = '06'
    elif month.lower() == 'july':
        month = '07'
    elif month.lower() == 'august':
        month = '08'
    elif month.lower() == 'september':
        month = '09'
    elif month.lower() == 'october':
        month = '10'
    elif month.lower() == 'november':
        month = '11'
    elif month.lower() == 'december':
        month = '12'
    return str(day) + str(month) + str(year)

def CrawlNatGeo():
    iterator = 0
    url = '/photography/photo-of-the-day/'

    while iterator < photosToDownload:
        res = GetDownloadUrl(url)
        if res[0]:
            print 'Downloading ' + res[1]
            print 'Looking for caption'
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

            path = folder + caption + '-' + date + '.jpg'
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
    if len(sys.argv) > 1:
        photosToDownload = int(sys.argv[1])
    else:
        print 'Downloading default amount of 10 phothos'
        photosToDownload = 10
    if len(sys.argv) > 2 and isinstance(sys.argv[2], str):
        folderToStore = sys.argv[2]
        
    if (len(sys.argv) > 3 
        and isinstance(sys.argv[3], int)
        and sys.argv[3] in range(0,2)):
            selectedFormat = formats[sys.argv[3]]
        

    if photosToDownload in range(1, 100):
        CrawlNatGeo()
    else:
        print str(photosToDownload) + 'Is not a valid amount of photos. ' 
        + 'Use a number from range 1 to 99.'



if __name__ == '__main__':
    main()


##GetPreviousPageUrl('/photography/photo-of-the-day/')
##        GetDownloadUrl('/photography/photo-of-the-day/bixby-bridge-california/')
##        localFile = open(iterator + '.jpg', 'wb')
##        localFile.write(requests.get('http://images.nationalgeographic.com/wpf/media-live/photos/000/679/cache/bixby-bridge-california_67923_990x742.jpg').content)
##        localFile.close()