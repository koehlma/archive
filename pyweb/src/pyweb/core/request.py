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

from http.client import HTTPMessage
from urllib.parse import urlparse, parse_qs

class Headers(HTTPMessage):
    CGI_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH')
    def __init__(self, environ):
        super().__init__()
        self.environ = environ
        for key, value in self.environ.items():
            if key.startswith('HTTP_'):
                self['-'.join([part.capitalize() for part in key[5:].split('_')])] = value
            elif key in self.CGI_HEADERS:
                self['-'.join([part.capitalize() for part in key[5:].split('_')])] = value

class Request():
    def __init__(self, environ, application):
        self.environ = environ
        self.application = application
        self.headers = Headers(environ)
        self.path = self.environ.get('PATH_INFO', '/')
        self.query = parse_qs(self.environ.get('QUERY_STRING', ''))
        self.method = self.environ.get('REQUEST_METHOD', 'GET').upper()
