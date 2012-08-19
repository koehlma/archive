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

import os.path
import mimetypes
from wsgiref.util import FileWrapper

class File():
    def __init__(self, path, type=None):
        self.type = type
        self.path = path
            
    def __call__(self, request, response):
        wrap_file(self.path, response, self.type)
        
def wrap_file(path, response, type=None):
    response.headers['Content-Type'] = mimetypes.guess_type(path)[0] if type is None else type
    response.headers['Content-Length'] = str(os.path.getsize(path))
    response.body = FileWrapper(open(path, 'rb'))