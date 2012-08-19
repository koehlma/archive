# -*- coding:utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import time

import ctypes
import ctypes.util

_library = ctypes.util.find_library('fluidsynth')
if not _library:
    raise ImportError('No library named fluidsynth')

_fluidsynth = ctypes.CDLL(_library)

class InitError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SimpleSynth(object):
    def __init__(self, font_file, gain=0.2, samplerate=44100):
        self._settings = Settings()
        self._settings.set_num('synth.gain', gain)
        self._settings.set_num('synth.sample-rate', samplerate)
        self._settings.set_int('synth.midi-channels', 256)
        self._samplerate = samplerate
        self._synth = Synth(self._settings)
        self._font = self._synth.sfload(font_file)
        self._driver = None
        self._file = None
    
    def init_audio(self, driver=None):
        if not self._file and not self._driver:
            if driver in ('jack', 'alsa', 'oss', 'pulseaudio', 'coreaudio', 'dsound', 'portaudio', 'sndman', 'dart', 'file'):
                self._settings.set_str('audio.driver', driver)
                self._driver = Driver(self._settings, self._synth)
            else:
                raise ValueError('invalid driver: %s' % (driver))
        else:
            raise InitError('already initialized')
    
    def init_file(self, filename, filetype='auto'):
        if not self._file and not self._driver:
            self._settings.set_str('audio.file.name', filename)
            self._settings.set_str('audio.file.type', filetype)
            self._settings.set_int('audio.period-size', 128)
            self._settings.set_int('audio.periods', 2)
            self._file = File(self._synth)
        else:
            raise InitError('already initialized')
    
    def sleep_write(self, seconds):
        if self._driver:
            time.sleep(seconds)
        elif self._file:
            for i in range(0, int(self._samplerate / 128.0 * seconds)):
                self._file.process_block()
        else:
            raise InitError('not initialized')

    def select(self, chan, bank, preset):
        self._synth.program_select(chan, self._font, bank, preset)

    def program_reset(self):
        self._synth.program_reset()
        
    def system_reset(self):
        self._synth.system_reset()

    def cc(self, chan, ctrl, val):
        self._synth.cc(chan, ctrl, val)

    def noteon(self, chan, key, vel):
        self._synth.noteon(chan, key, vel)
    
    def noteoff(self, chan, key):
        self._synth.noteoff(chan, key)
    
    def destroy(self):
        self._settings.delete()
        self._synth.delete()
        if self._driver:
            self._driver.delete()
        if self._file:
            self._file.delete()

class Settings(object):
    def __init__(self):
        self._settings = _new_fluid_settings()
    
    def set_str(self, key, value):
        _fluid_settings_setstr(self, key, value)
    
    def set_num(self, key, value):
        _fluid_settings_setnum(self, key, value)
    
    def set_int(self, key, value):
        _fluid_settings_setint(self, key, value)
    
    def delete(self):
        _delete_fluid_settings(self)
    
    def from_param(self):
        return self._settings

class Synth(object):
    def __init__(self, settings):
        self._settings = settings
        self._synth = _new_fluid_synth(self._settings)
    
    def delete(self):
        _delete_fluid_synth(self)
    
    def sfload(self, filename, update_midi_preset=0):
        return _fluid_synth_sfload(self, filename, update_midi_preset)
    
    def sfunload(self, font_id, update_midi_preset=0):
        return _fluid_synth_sfunload(self, font_id, update_midi_preset)

    def program_select(self, chan, font_id, bank, preset):
        return _fluid_synth_program_select(self, chan, font_id, bank, preset)

    def noteon(self, chan, key, vel):
        return _fluid_synth_noteon(self, chan, key, vel)

    def noteoff(self, chan, key):
        return _fluid_synth_noteoff(self, chan, key)
    
    def pitch_bend(self, chan, val):
        return _fluid_synth_pitch_bend(self, chan, val + 8192)

    def cc(self, chan, ctrl, val):
        return _fluid_synth_cc(self, chan, ctrl, val)

    def program_change(self, chan, prg):
        return _fluid_synth_program_change(self, chan, prg)

    def bank_select(self, chan, bank):
        return _fluid_synth_bank_select(self, chan, bank)

    def sfont_select(self, chan, font_id):
        return _fluid_synth_sfont_select(self, chan, font_id)

    def program_reset(self):
        return _fluid_synth_program_reset(self)

    def system_reset(self):
        return _fluid_synth_system_reset(self)
    
    def from_param(self):
        return self._synth

class Driver(object):
    def __init__(self, settings, synth):
        self._driver = _new_fluid_audio_driver(settings, synth)
    
    def delete(self):
        _delete_fluid_audio_driver(self)
    
    def from_param(self):
        return self._driver

class File(object):
    def __init__(self, synth):
        self._file = _new_fluid_file_renderer(synth)
    
    def process_block(self):
        _fluid_file_renderer_process_block(self)
    
    def delete(self):
        _delete_fluid_file_renderer(self)
    
    def from_param(self):
        return self._file

def _function(name, result, args):
    func = getattr(_fluidsynth, name)
    func.restype = result
    func.argtypes = args
    return func

''' Settings '''    
_new_fluid_settings =  _function('new_fluid_settings', ctypes.c_void_p, [])
_delete_fluid_settings = _function('delete_fluid_settings',ctypes.c_void_p, [Settings])
_fluid_settings_setstr = _function('fluid_settings_setstr', ctypes.c_int, [Settings,
                                                                           ctypes.c_char_p,
                                                                           ctypes.c_char_p])
_fluid_settings_setnum = _function('fluid_settings_setnum', ctypes.c_int, [Settings,
                                                                           ctypes.c_char_p,
                                                                           ctypes.c_double])
_fluid_settings_setint = _function('fluid_settings_setint', ctypes.c_int, [Settings,
                                                                           ctypes.c_char_p,
                                                                           ctypes.c_int])

''' Synth '''
_new_fluid_synth = _function('new_fluid_synth', ctypes.c_void_p, [Settings])
_delete_fluid_synth = _function('delete_fluid_synth',  ctypes.c_void_p, [Synth])
_fluid_synth_sfload = _function('fluid_synth_sfload', ctypes.c_int, [Synth, ctypes.c_char_p, ctypes.c_int])
_fluid_synth_sfunload = _function('fluid_synth_sfunload', ctypes.c_int, [Synth, ctypes.c_int, ctypes.c_int])
_fluid_synth_program_select = _function('fluid_synth_program_select', ctypes.c_int, [Synth,
                                                                                     ctypes.c_int,
                                                                                     ctypes.c_int,
                                                                                     ctypes.c_int,
                                                                                     ctypes.c_int])
_fluid_synth_noteon = _function('fluid_synth_noteon', ctypes.c_int, [Synth,
                                                                     ctypes.c_int,
                                                                     ctypes.c_int,
                                                                     ctypes.c_int])
_fluid_synth_noteoff = _function('fluid_synth_noteoff', ctypes.c_int, [Synth,
                                                                       ctypes.c_int,
                                                                       ctypes.c_int])
_fluid_synth_pitch_bend = _function('fluid_synth_pitch_bend', ctypes.c_int, [Synth,
                                                                             ctypes.c_int,
                                                                             ctypes.c_int])
_fluid_synth_cc = _function('fluid_synth_cc', ctypes.c_int, [Synth,
                                                             ctypes.c_int,
                                                             ctypes.c_int,
                                                             ctypes.c_int])
_fluid_synth_program_change = _function('fluid_synth_program_change', ctypes.c_int, [Synth,
                                                                                     ctypes.c_int,
                                                                                     ctypes.c_int])
_fluid_synth_bank_select = _function('fluid_synth_bank_select', ctypes.c_int, [Synth,
                                                                               ctypes.c_int,
                                                                               ctypes.c_int])
_fluid_synth_sfont_select = _function('fluid_synth_sfont_select', ctypes.c_int, [Synth,
                                                                                 ctypes.c_int,
                                                                                 ctypes.c_int])
_fluid_synth_program_reset = _function('fluid_synth_program_reset', ctypes.c_int, [Synth])
_fluid_synth_system_reset = _function('fluid_synth_system_reset', ctypes.c_int, [Synth])

''' Driver '''
_new_fluid_audio_driver = _function('new_fluid_audio_driver', ctypes.c_void_p, [Settings, Synth])
_delete_fluid_audio_driver = _function('delete_fluid_audio_driver', ctypes.c_void_p, [Driver])

''' File '''
_new_fluid_file_renderer = _function('new_fluid_file_renderer', ctypes.c_void_p, [Synth])
_fluid_file_renderer_process_block = _function('fluid_file_renderer_process_block', ctypes.c_int, [File])
_delete_fluid_file_renderer = _function('delete_fluid_file_renderer', ctypes.c_void_p, [File])