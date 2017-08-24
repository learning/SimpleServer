# ------------------------------------------------------------------------------
# SimpleServer
# ------------------------------------------------------------------------------
__VERSION__ = "0.1.0"

import sublime
import sublime_plugin
import io
import threading
import socket
import shutil

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn, TCPServer

server_thread = None

class SimpleServerHandler(BaseHTTPRequestHandler):
    output = '<html><body><h1>SimpleServer</h1></body></html>'

    def version_string(self):
        '''overwrite server's version string'''
        return 'SimpleServer/%s Sublime/%s' % (__VERSION__, sublime.version())

    def send_head(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header("Content-Length", len(self.output))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()

    def do_GET(self):
        """Serve a GET request."""
        self.send_head()
        f = io.BytesIO()
        f.write(self.output.encode())
        f.seek(0)
        shutil.copyfileobj(f, self.wfile)
        f.close()

class SimpleServerThreadMixIn(ThreadingMixIn, TCPServer):
    pass

class SimpleServerThread(threading.Thread):
    httpd = None

    def __init__(self):
        super(SimpleServerThread, self).__init__()
        self.httpd = SimpleServerThreadMixIn(('', 8080), SimpleServerHandler)

    def run(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()

class SimpleserverStartCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        global server_thread
        if server_thread is not None and server_thread.is_alive():
            return sublime.message_dialog('SimpleServer is already started!')
        try:
            server_thread = SimpleServerThread()
            server_thread.start()
            sublime.status_message('SimpleServer is started!')
        except socket.error as error:
            print(error)
            sublime.message_dialog(error)

class SimpleserverStopCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        global thread
        if thread is not None and thread.is_alive():
            thread.stop()
            thread.join()
            thread = None
        sublime.status_message('SimpleServer is stopped!')
