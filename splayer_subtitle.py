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

class Splayer_subtle(object):
    __url = "https://www.shooter.cn/api/subapi.php"
    __path = "/tmp"
    def __init__(self, url = None, path = None, format = "json", lang = "Chn", hash_func = hash_video):
        self.url = self.__url if url is None else url
        self.path = self.__path if path is None else path
        self.hash_func = hash_func
        self.filename = None
        self.subtles = []
        self.params = {"filehash": None, "pathinfo": None, "format": format, "lang":lang}

    def setfile(self, filename):
        self.filename = filename
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

    def fetch_subtle_list(self):
        self.subtles = json.loads(urlopen(self.request).readlines()[0])

    def fetch_subtle_cand(self, index = 0):
        if len(self.subtles) <= index:
            print "No subtle candidate"
            sys.exit(2)
        subtle = self.subtles[index]
        if len(subtle[u'Files']) > 1:
            print "Not supported yet"
            sys.exit(3)
        subinfo = {}
        for i in ['Desc', 'Delay']:
            subinfo[i] = subtle[i]
        subinfo['filename'] = os.path.join(self.path, self.params['pathinfo'] + "." + subtle['Files'][0]['Ext'])
        try:
            print "try fetching Subtle file to "+subinfo['filename']
            print 'target url:: ' + subtle['Files'][0]['Link']
            urlretrieve(subtle['Files'][0]['Link'], subinfo['filename'])
        except Exception as e:
            print e
            sys.exit(4)
        print "Successfully downloaded subtle file: " + subinfo['filename']
        return subinfo

def fetch_subtle(filename, index = 0):
    splayer_subtle = Splayer_subtle()
    splayer_subtle.setfile(filename)
    splayer_subtle.make_request()
    splayer_subtle.fetch_subtle_list()
    return splayer_subtle.fetch_subtle_cand(index)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Please provide at least 1 video file"
        sys.exit(6)
    for i in range(1, len(sys.argv)):
        print fetch_subtle(sys.argv[i])
