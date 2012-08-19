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

import socket
import re
import threading
import asyncore
import datetime

import contacts

class Action(object):  
    def ring(self, call):
        pass
    
    def call(self, call):
        pass
    
    def connect(self, call):
        pass
    
    def disconnect(self, call):
        pass

class Connection(dict):
    def __init__(self, time, id, event, contacts):
        self.time = datetime.datetime.strptime(time, "%d.%m.%y %H:%M:%S")
        self.id = id
        self.event = event
        self._contacts = contacts
    
    def ring(self, from_number, to_number, line):
        self['from'] = from_number
        self['to'] = to_number
        self['line'] = line
        self['number'] = to_number
        self['from_name'] = self._contacts.resolve(from_number)
        self['to_name'] = self._contacts.resolve(to_number)
    
    def call(self, extension, from_number, to_number, line):
        self['extension'] = extension
        self['from'] = from_number
        self['to'] = to_number
        self['line'] = line
        self['number'] = from_number
        self['from_name'] = self._contacts.resolve(from_number)
        self['to_name'] = self._contacts.resolve(to_number)
    
    def connect(self, extension, external):
        self['extension'] = extension
        self['external'] = external
    
    def disconnect(self, duration):
        minutes, seconds = divmod(int(duration), 60)
        hours, minutes = divmod(minutes, 60)
        self['duration'] = (hours, minutes, seconds, duration)
    
    def match(self, filter):
        for key in filter:
            if key in self:
                if hasattr(filter[key], 'match'):
                    if not filter[key].match(self[key]):
                        return False
                else:
                    if not filter[key] == self[key]:
                        return False
            else:
                return False
        return True
    
    @property
    def human_readable_duration(self):
        hours, minutes, seconds, total = self['duration']
        format = []
        if hours:
            format.append('%ih' % (hours))
        if minutes:
            format.append('%im' % (minutes))
        if seconds:
            format.append('%is' % (seconds))
        if format:
            return ' '.join(format)
        return None
    
    @property
    def name_or_number(self):
        if self['from_name']:
            from_ = self['from_name']
        else:
            from_ = self['from']
        if self['to_name']:
            to = self['to_name']
        else:
            to = self['to']
        return (from_, to)
    
class Callmonitor(asyncore.dispatcher):
    def __init__(self, host='fritz.box', port=1012, contacts=contacts.Contacts()):
        asyncore.dispatcher.__init__(self)
        self._host = host
        self._port = port
        self._contacts = contacts
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self._connections = {}
        self._buffer = ''
        self._callbacks = []        
    
    def main(self):
        asyncore.loop()       

    def main_quit(self):
        self.close()

    def handle_read(self):
        self._buffer += self.recv(1024).decode('utf-8')
        if self._buffer.endswith('\r\n'):
            for line in self._buffer[:-2].split('\r\n'):
                data = line.split(';')[:-1]
                time = data.pop(0)
                event = data.pop(0).lower()
                id = int(data.pop(0))
                if not id in self._connections:
                    self._connections[id] = Connection(time, id, event, self._contacts)
                getattr(self._connections[id], event)(*data)
                self._invoke_callbacks(event, id)
                if event == 'disconnect':
                    del self._connections[id]       
            self._buffer = ''
    
    def handle_close(self):
        self.close()
    
    def add_callbacks(self, filter, ring, call, connect, disconnect):
        for key in filter:
            if isinstance(filter[key], str):
                filter[key] = re.compile(filter[key])
        self._callbacks.append({'filter' : filter,
                                'ring' : ring,
                                'call' : call,
                                'connect' : connect,
                                'disconnect' : disconnect})
    
    def add_action(self, filter, action):
        self.add_callbacks(filter, action.ring, action.call, action.connect, action.disconnect)
    
    def _invoke_callbacks(self, event, id):
        connection = self._connections[id]
        for callback in self._callbacks:
            if connection.match(callback['filter']):
                thread = threading.Thread(target = callback[event], args = (connection,))
                thread.start()