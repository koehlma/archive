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

import re

from collections import OrderedDict

from pyweb.core.request import Request
from pyweb.core.response import Response

class Application():
    __URLS__ = {}
    def __init__(self):
        self._urls = OrderedDict()
        for url, handle in self.__URLS__.items():
            if hasattr(self, handle):
                self._urls[re.compile(r'^({})$'.format(url))] = getattr(self, handle)
    
    def handle(self, environ, start_response):
        request = Request(environ, self)
        response = Response(self)
        for url, handle in self._urls.items():
            if url.match(request.path):
                handle(request, response)  
                start_response(*response.start_response)
                return response.body
        self.error(request, response)
        start_response(*response.start_response)
        return response.body
    
    def error(self, request, response):
        response.status = 404
        response.message = 'NOT FOUND'
        response.body.append('404 Not Found...'.encode('utf-8'))