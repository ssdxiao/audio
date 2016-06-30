#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
import threading
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os
import sys
import time
from datetime import datetime
from moviepy.editor import AudioFileClip, concatenate_audioclips
try:
    import simplejson as json
except ImportError:
    import json
import shutil

LISTENERS = []
AUDIO_PATH = "/tmp/audio"

class RealtimeHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        print "open"
        LISTENERS.append(self)

    def on_message(self, message):
        
        if message.startswith("start"):
            print "now start"
            self.current = "start"
            if os.path.exists(AUDIO_PATH):
                shutil.rmtree(AUDIO_PATH)
            os.mkdir(AUDIO_PATH) 
            self.i = 0
        elif message.startswith("stop"):
            print "now close"
            self.current = "stop"
            self.clips()
            if os.path.exists(AUDIO_PATH):
                shutil.rmtree(AUDIO_PATH)
        elif message.startswith("analyze"):
            pass
        else :
            self.save(message)

    def clips(self):
        print "clips start"
        filelist = os.listdir(AUDIO_PATH)
        audiolist=[]
        if filelist == []:
            print "no audio file find"
            return
        print filelist
        for file_temp in filelist:
             audiolist.append(AudioFileClip("%s/%s"%(AUDIO_PATH,file_temp)))
       
        final_clip = concatenate_audioclips(audiolist)
        final_clip.write_audiofile("static/abc.wav")
        self.write_message("/static/abc.wav")
        print "clips end"

    def save(self, message):
        try:
            self.i += 1;
            self.File = open("%s/temp%d.wav"%(AUDIO_PATH,self.i), "w")
            self.File.write(message)
        finally:
            self.File.close()

    def on_close(self):
        print "close"
        LISTENERS.remove(self)


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'auto_reload': True,
    }

application = tornado.web.Application(
    [('/record',RealtimeHandler),],
    **settings)


#usage from http://stackoverflow.com/questions/8045698/https-python-client
#openssl genrsa -out privatekey.pem 2048
#openssl req -new -key privatekey.pem -out certrequest.csr
#openssl x509 -req -in certrequest.csr -signkey privatekey.pem -out certificate.pem
http_server = tornado.httpserver.HTTPServer(
            application,
            ssl_options={
                "certfile": os.path.join("./", "certificate.pem"),
                "keyfile": os.path.join("./", "privatekey.pem"),
                }
        )
http_server.listen(443)
tornado.ioloop.IOLoop.instance().start()



