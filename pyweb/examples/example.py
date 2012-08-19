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

from pyweb.core.application import Application
from pyweb.core.server import simple_server
from pyweb.handlers.htmlpage import HtmlPage
from pyweb.handlers.directory import Directory
from pyweb.handlers.file import File

class Example(Application):
    __URLS__ = {'/|/index\.html' : 'home',
                '/data/.*' : 'data',
                '/source.py' : 'source',
                '/custom' : 'custom'}
    home = HtmlPage('<html>'
                        '<head>'
                            '<title>Example</title>'
                        '</head>'
                        '<body>'
                            '<span style="font-size:30px">Example</span></br>'
                            '<a href="data/test1">Test 1</a></br>'
                            '<a href="data/test2">Test 2</a></br>'
                            '<a href="data/test3">Test 3</a></br>'
                            '<a href="custom">Custom</a></br>'
                            '<a href="source.py">Source</a>'
                        '</body>'
                    '</html>')
    data = Directory(os.path.join(os.path.dirname(__file__), 'data'))
    data.update_path = lambda path: path.replace('/data/', '')
    source = File(__file__)
    def custom(self, request, response):
        response.body.append('Custom...'.encode('utf-8'))

if __name__ == '__main__':
    simple_server(Example())