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

class Directory():
    def __init__(self, root):
        self.root = os.path.abspath(root)
    
    def __call__(self, request, response):
        document = os.path.abspath(os.path.join(self.root, self.update_path(request.path)))
        if os.path.isdir(document):
            document = os.path.join(document, 'index.html')
        if document.startswith(self.root) and os.path.isfile(document):
            mimetype = mimetypes.guess_type(document)[0]
            if mimetype:
                response.headers['Content-Type'] = mimetype
            response.headers['Content-Length'] = str(os.path.getsize(document))
            response.body = FileWrapper(open(document, 'rb'))
        else:
            response.headers['Content-Type'] = 'text/html; charset=UTF-8'
            response.status = 404
            response.message = 'NOT FOUND'
            response.body.append('<span style="font-size:50px"><b>404 Not Found</b></span>'.encode('utf-8'))
    
    def update_path(self, path):
        return path[1:]