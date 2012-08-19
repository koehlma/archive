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

import monitor

def _fallback(message):
    class Fallback(monitor.Action):
        def __init__(self, *args):
            print message
    return Fallback

class _Banshee(monitor.Action):
    def __init__(self):
        self._state = None
        self._banshee = None
        
    def ring(self, connection):
        self._volume()
        
    def call(self, connection):
        self._volume()
        
    def connect(self, connection):
        self._check()
        if self._banshee:
            self._banshee.Pause()
            
    def disconnect(self, connection):
        self._check()
        if self._banshee and self._state == 'playing':
            self._banshee.Play()
            self._banshee.SetVolume(dbus.UInt16(self._volume))
        
    def _volume(self):
        self._check()
        if self._banshee:
            self._state = str(self._banshee.GetCurrentState())
            self._volume = int(self._banshee.GetVolume())
            if self._state == 'playing':
                self._banshee.SetVolume(dbus.UInt16(self._volume / 2))
        
    def _check(self):
        if SESSION_BUS.name_has_owner('org.bansheeproject.Banshee'):
            if not self._banshee:
                self._banshee = SESSION_BUS.get_object('org.bansheeproject.Banshee', '/org/bansheeproject/Banshee/PlayerEngine')
        else:
            self._banshee = None

try:
    import dbus
    SESSION_BUS = dbus.SessionBus()
    Banshee = _Banshee
except ImportError:
    Banshee = _fallback('You have to install python bindings for dbus to use Benshee.')
            
class _NotifyDE(monitor.Action):       
    def _notify(self, summary, connection):
        from_, to = connection.name_or_number()
        self._notification.update(summary, ('von %s zu %s' % (from_, to)).encode('utf-8'), self._icon)
        self._notification.show()
        
    def ring(self, connection):
        self._notify('Eingehender Anruf', connection)

    def call(self, connection):
        self._notify('Ausgehender Anruf', connection)

    def connect(self, connection):
        self._notify('Angenommen', connection)

    def disconnect(self, connection):
        from_, to = connection.name_or_number
        message = ['von %s zu %s' % (from_, to)]
        duration = connection.human_readable_duration
        if duration:
            message.append('über')
            message.append(duration)
        self._notification.update('Anfgelegt', (' '.join(message)).encode('utf-8'), self._icon)
        self._notification.show()

class _NotifyDE_GI(_NotifyDE):
    def __init__(self, title='Callmonitor', icon=None):
        if not _notify.is_initted():
            _notify.init(title)
        self._notification = _notify.Notification.new('', '', icon)
        self._icon = icon

class _NotifyDE_PY(_NotifyDE):
    def __init__(self, title='Callmonitor', icon=None):
        if not pynotify.is_initted():
            pynotify.init(title)
        self._notification = pynotify.Notification('', '', icon)
        self._icon = icon

try:
    from gi.repository import Notify as _notify
    NotifyDE = _NotifyDE_GI
except ImportError:
    try:
        import pynotify
        NotifyDE = _NotifyDE_PY
    except ImportError:
        NotifyDE = _fallback('To use NotifyDE you have to install libnotify with GObject Introspection bindings or pynotify.')   