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

_country_prefix = re.compile('^(00([0-9]{2})|\+([0-9]{2}))([0-9]*)$')

class NumberConverter():
    def __init__(self, area_code, country_code):
        self._country_code = country_code
        self._area_code = area_code
        self._area_number = re.compile('^%s?([0-9]*)$' % (area_code))
        
    def __call__(self, number):
        country_prefix = _country_prefix.match(number)
        if country_prefix.group(2):
            country = country_prefix.group(2)
        else:
            country = country_prefix.group(3)
        if country == self._country_code:
            area_number = self._area_number.match(country_prefix.group(4))
            if area_number:
                return re.compile('^((\+%s|00%s|0)%s)?%s$' % (country,
                                                              country,
                                                              self._area_code,
                                                              area_number.group(1)))
            else:
                return re.compile('^(\+%s|00%s|0)%s$' % (country,
                                                         country,
                                                         country_prefix.group(4)))            
        else:
            return re.compile('^(\+%s|00%s)%s$' % (country,
                                                   country,
                                                   country_prefix.group(4)))

class Contacts(object):
    def __init__(self):
        self._converter = None
        self._database = {}
        
    def set_region(self, area_code, country_code):
        self._converter = NumberConverter(area_code, country_code)
    
    def set_converter(self, converter):
        self._converter = converter
    
    def read_from_csv(self, filename):
        with open(filename, 'r') as csv:
            for line in csv.readlines():
                data = line[:-1].split(';')
                for number in data[1:]:
                    self._database[self._converter(number)] = data[0]
    
    def resolve(self, number):        
        for num, name in self._database.iteritems():
            if num.match(number):
                return name
        return None