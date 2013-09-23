#!/bin/env python
#coding:utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.concurrent
import tornado.ioloop
import os,sys,subprocess,shlex
import time
from tornado import gen

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

def call_subprocess(context, command, callback=None):
    context.ioloop = tornado.ioloop.IOLoop.instance()
#    context.pipe = p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    context.pipe = p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    context.ioloop.add_handler(p.stdout.fileno(), context.async_callback(on_subprocess_result, context, callback), context.ioloop.READ)

def on_subprocess_result(context, callback, fd, result):
    try:
        if callback:
            callback(context.pipe.stdout)
    except Exception, e:
        logging.error(e)
    finally:
        context.ioloop.remove_handler(fd)

def cmd(b):
    a=os.popen('free -m').read()
    print '111111111111111'
    return a

class SleepHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        a = yield tornado.gen.Task(call_subprocess,self, "sleep 10")
        print '111',a.read()
        self.write("when i sleep 5s")

class ShellHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        self.write("Before sleep<br />")
        self.flush()
        response = yield gen.Task(call_subprocess, self, "ls /")
        self.write("Output is:\n%s" % (response.read(),))
        self.finish()

#测试
class go(tornado.web.RequestHandler):
    def get(self):
        self.write("when i sleep 5s"+cmd('b'))


class JustNowHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("i hope just now see you")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
            (r"/nima",ShellHandler),(r"/sleep", SleepHandler), (r"/justnow", JustNowHandler),(r"/go", go)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
