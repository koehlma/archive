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

class HtmlPage():
    def __init__(self, html):
        self.html = html.encode('utf-8')
        self.lenght = str(len(self.html))
    
    def __call__(self, request, response):
        response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        response.headers['Content-Length'] = self.lenght
        response.body.append(self.html)