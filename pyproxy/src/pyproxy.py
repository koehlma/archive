# -*- coding:utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ssl import wrap_socket, SSLError
from socketserver import ThreadingMixIn
from urllib.request import Request, urlopen, URLError
from http.client import BadStatusLine
from http.server import HTTPServer, BaseHTTPRequestHandler

KEYFILE = 'certs/example.key'
CERTFILE = 'certs/example.crt'
BLOCKSIZE = 2048

class Proxy(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, host=False):
        self.host = host
        super().__init__(request, client_address, server)
        
    def _proxy(self):
        self.server.manipulate('started', None, self)
        if self.host:
            self.path = 'https://{host}{path}'.format(host=self.host, path=self.path)
        self.path = self.server.manipulate('request_path', self.path, self)
        self.headers = self.server.manipulate('request_headers', self.headers, self)
        request = Request(self.path, headers=self.headers)
        request.get_method = lambda: self.command
        if 'Content-Length' in self.headers:
            post_data = self.rfile.read(int(self.headers['Content-Length']))
            request.add_data(self.server.manipulate('request_data', post_data, self))
        try:
            response = urlopen(request)
            self.send_response(200)
            headers = self.server.manipulate('response_headers', response.info(), self)
            for keyword, value in headers.items():
                self.send_header(keyword, value)
            self.end_headers()
            blocksize = self.server.manipulate('blocksize', BLOCKSIZE, self)
            if blocksize:
                data = self.server.manipulate('response_data', response.read(blocksize), self)
                while data:
                    self.wfile.write(data)
                    data = self.server.manipulate('response_data', response.read(blocksize), self)
            else:
                self.wfile.write(self.server.manipulate('response_data', response.read(), self))
        except URLError as error:
            code = self.server.manipulate('error_code', error.getcode(), self)
            msg = self.server.manipulate('error_msg', error.msg, self)
            self.send_response(code, msg)
            headers = self.server.manipulate('error_headers', error.headers, self)
            for keyword, value in headers.items():
                self.send_header(keyword, value)
            self.end_headers()
        except BadStatusLine as error:
            pass
        self.server.manipulate('finished', None, self)
        
    def do_CONNECT(self):
        self.send_response(200)
        self.end_headers()
        try:
            connection = wrap_socket(self.connection, keyfile=KEYFILE, certfile=CERTFILE, server_side=True)
            Proxy(connection, self.client_address, self.server, self.headers['Host'])
        except SSLError:
            pass
        
    do_GET = _proxy
    do_POST = _proxy
    do_OPTIONS = _proxy
    do_HEAD = _proxy
    do_PUT = _proxy
    do_DELETE = _proxy
    do_TRACE = _proxy

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer): pass

class Manipulator():
    def __init__(self):
        self._manipulators = []
    
    def load(self, manipulator):
        self._manipulators.append(manipulator)
    
    def manipulate(self, function, value, handler):
        for manipulator in sorted(self._manipulators, key=lambda manipulator: manipulator.priority):
            if hasattr(manipulator, function):
                value = getattr(manipulator, function)(value, handler)
        return value

if __name__ == '__main__':
    import os.path
    import subprocess
    if not os.path.exists(KEYFILE):
        print('---- create certificate ----')
        subprocess.call(['openssl', 'req', '-new', '-x509', '-days', '365', '-nodes', '-out', CERTFILE, '-keyout', KEYFILE])
        print('---- certificate created ----')
    print('---- starting proxy ----')
    manipulator = Manipulator()
    from manipulators.gzip import Unzip, Zip
    manipulator.load(Unzip())
    manipulator.load(Zip())
    from manipulators.grooveshark import Grooveshark
    manipulator.load(Grooveshark())
    server = ThreadingHTTPServer(('127.0.0.1', 8080), Proxy)
    server.manipulate = manipulator.manipulate
    server.serve_forever()