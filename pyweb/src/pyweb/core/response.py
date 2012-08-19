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

class Headers(HTTPMessage):
    def __init__(self, headers=None):
        super().__init__()
        if headers:
            for name, value in headers:
                self[name] = value
    
    def response(self):
        return list(self.items())
    
class Response():
    def __init__(self, application, body=None, headers=None):
        self.application = application
        self.status = 200
        self.message = 'OK'
        if body is None:
            body = []
        self.body = body
        self.headers = Headers(headers)
    
    @property
    def start_response(self):
        return '{} {}'.format(self.status, self.message), self.headers.response()
        

    