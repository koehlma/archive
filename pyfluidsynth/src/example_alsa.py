#!/usr/bin/env python
# -*- coding:utf-8 -*-

import fluidsynth

synth = fluidsynth.SimpleSynth('/usr/share/soundfonts/fluidr3/FluidR3GM.SF2')
synth.init_audio('alsa')
synth.select(0, 0, 30)

for note in (50, 52, 54, 55, 57, 59, 61, 62):
	synth.noteon(0, note, 100)
	synth.sleep_write(0.7)
	synth.noteoff(0, note)

synth.destroy()
