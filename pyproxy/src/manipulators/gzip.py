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

import zlib

class Unzip():
    priority = 0
    def response_data(self, data, handler):
        if 'Content-Encoding' in handler.headers:
            if handler.headers['Content-Encoding'] == 'gzip':
                return zlib.decompress(data)
        return data
    
class Zip():
    priority = 100
    def response_data(self, data, handler):
        if 'Content-Encoding' in handler.headers:
            if handler.headers['Content-Encoding'] == 'gzip':
                return zlib.compress(data)
        return data
        