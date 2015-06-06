#!/usr/bin/python
# _*_ coding:utf8 _*_

from urllib2 import Request, urlopen
from urllib import urlencode, urlretrieve
from hashlib import md5
import os, sys
import json


def get_size(fhandler):
    fhandler.seek(0, 2)
    return fhandler.tell()

def video_md5(fhandler, pos, size):
    fhandler.seek(pos, 0)
    return md5(fhandler.read(size)).hexdigest()

def hash_video(filename):
    block = 4096
    res = ""
    with open(filename, 'rb') as video:
        size = get_size(video)
        if size >= 2 * block:
            offset = [block, size / 3 * 2, size / 3, size - 2 * block]
            res = ";".join(map(lambda x:video_md5(video, x, block), offset))
    return res

class Splayer_subtitle(object):
    __url = "https://www.shooter.cn/api/subapi.php"
    __path = None
    def __init__(self, url = None, path = None, format = "json", lang = "Chn", hash_func = hash_video):
        self.url = self.__url if url is None else url
        self.path = self.__path if path is None else path
        self.hash_func = hash_func
        self.filename = None
        self.subtitles = []
        self.params = {"filehash": None, "pathinfo": None, "format": format, "lang":lang}

    def setfile(self, filename):
        self.filename = filename
        if self.path is None:
            self.path = os.path.dirname(filename)
        self.params['pathinfo'] = os.path.basename(filename)

    def hash_video(self):
        return self.hash_func(self.filename)

    def make_request(self):
        self.params['filehash'] = self.hash_video()
        self.request = Request(self.url, data=urlencode(self.params))

    def check_filename(self):
        if not os.path.exists(str(self.filename)):
            print "Warning:: Please set correct filename"
            sys.exit(1)

    def fetch_subtitle_list(self):
        self.subtitles = json.loads(urlopen(self.request).readlines()[0])

    def fetch_subtitle_cand(self, index = 0):
        if len(self.subtitles) <= index:
            print "No subtitle candidate"
            sys.exit(2)
        subtitle = self.subtitles[index]
        if len(subtitle[u'Files']) > 1:
            print "Not supported yet"
            sys.exit(3)
        subinfo = {}
        for i in ['Desc', 'Delay']:
            subinfo[i] = subtitle[i]
        subinfo['filename'] = os.path.join(self.path, self.params['pathinfo'] + "." + subtitle['Files'][0]['Ext'])
        try:
            print "try fetching Subtle file to "+subinfo['filename']
            print 'target url:: ' + subtitle['Files'][0]['Link']
            urlretrieve(subtitle['Files'][0]['Link'], subinfo['filename'])
        except Exception as e:
            print e
            sys.exit(4)
        print "Successfully downloaded subtitle file: " + subinfo['filename']
        return subinfo

def fetch_subtitle(filename, index = 0):
    splayer_subtitle = Splayer_subtitle()
    splayer_subtitle.setfile(filename)
    splayer_subtitle.make_request()
    splayer_subtitle.fetch_subtitle_list()
    return splayer_subtitle.fetch_subtitle_cand(index)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Please provide at least exactly 1 video file"
        sys.exit(6)
    subtitle = fetch_subtitle(sys.argv[1])
