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

STREAM_MATCH = re.compile('.*grooveshark\.com\/stream\.php')

class Grooveshark():
    priority = 50
    def __init__(self):
        self._streams = {}
        
    def response_data(self, data, handler):
        if STREAM_MATCH.match(handler.path):
            if not handler in self._streams:
                print('Grooveshark - Stream')
                self._streams[handler] = open(input('Filename: '), 'wb')
            self._streams[handler].write(data)    
        return data
    
    def finished(self, none, handler):
        if handler in self._streams:
            self._streams[handler].close()