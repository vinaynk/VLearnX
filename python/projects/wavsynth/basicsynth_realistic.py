#!/usr/bin/env python

"""
Some changes of the basicssynth by vinaynk that are geared towards more realistically sounding music:
   * overtone spectrum now changes based on the volume of a note (louder note => stronger overtones)
   * random variations in volume and frequency
   * added modulation to the ADSR curvers 
   * added overtone spectrum of a real acoustic guitar

MIT License

Copyright (c) 2022 MrMho

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
   
"""


import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt
import random


FS  = 48000         # project sampling rate
F32 = np.float32    # useful alias


def iround(x):
    return int(round(x))


def getSinWav(freq, nsamp, amp=0.2):
    tx    = np.arange(nsamp)

    phase = 0
    wav   = np.sin(2 * np.pi * freq / FS * tx + phase) * amp
    return F32(wav)


def justSinWav():
    'just a simple sin wav (pure tone)'
    freq  = 800     # hz
    dur   = 1       # s
    nsamp = iround(FS * dur)
    wav   = getSinWav(freq, nsamp)
    wavfile.write('output.wav', FS, wav)


def seqManySinWavs():
    'multiple sin wavs of different freqs arranged sequentially'
    freq  = 200
    dur   = 0.5
    nsamp = iround(dur * FS)
    ratio = 7/5
    sil   = np.zeros(FS//10, dtype=F32)
    wavs  = [ sil ]
    for wid in range(5):
        wav = getSinWav(freq, nsamp)
        wavs.append(wav)
        wavs.append(sil)
        freq *= ratio
    wav = np.hstack(wavs)
    wavfile.write('output.wav', FS, wav)


def basicRampUpDownEnvelope(attack, release):
    env1 = np.linspace(0, 1, attack)   # up
    env2 = np.linspace(1, 0, release)  # down
    env  = np.hstack((env1, env2))
    return F32(env)


def adsrEnvelope(attack, decay, sustain, release, sustainAmp=0.4):
    'ADSR env'
    env = [
        np.linspace(0, 1, attack),
        np.linspace(1, sustainAmp, decay),
        np.zeros(sustain) + sustainAmp,
        np.linspace(sustainAmp, 0, release)
    ]
    env = np.hstack(env)
    return F32(env)


def adsrFadeEnvelope(attack, decay, sustain, release, sustainAmp=0.4, fade=4):
    '''
    similar to adsr, but with slow exponential decay during sustain.
    this captures behavior of a plucked string
    '''

    t = np.arange(sustain) / FS
    f_mod = 2
    mod_strength = 0.08

    # Amplitude modulation to be applied to the sustain part. Modulation strength decreases over time.
    modulator = 1 + mod_strength * np.linspace(1, 0.2, sustain) * \
                np.sin(2 * np.pi * f_mod * t)

    env = [
        np.linspace(0, 1, attack),
        np.linspace(1, sustainAmp, decay),
        np.exp(-np.linspace(0, fade, sustain)) * sustainAmp * modulator,
        np.linspace(np.exp(-fade) * sustainAmp, 0, release)
    ]
    env = np.hstack(env)
    return F32(env)


def seqManySinWavsWithEnv():
    'multiple sin wavs of different freqs arranged in seq (with env)'
    freq  = 400
    ratio = 6/5
    sil   = np.zeros(FS//10, dtype=F32)
    wavs  = [ sil ]
    envType = 3
    if envType == 1:        # 1 basic ramp env
        dur     = 1
        nsamp   = iround(dur * FS)
        attack  = iround(0.01 * FS)
        release = nsamp - attack
        env   = basicRampUpDownEnvelope(attack, release)
    elif envType == 2:      # 2 adsr env
        a, d, s, r =  (iround(0.01 * FS), iround(0.15 * FS),
                       iround(1 * FS),    iround(0.03 * FS))
        env = adsrEnvelope(a, d, s, r)
    elif envType == 3:      # 3 edsr env with fade during sustain
        a, d, s, r =  (iround(0.01 * FS), iround(0.15 * FS),
                       iround(1 * FS),    iround(0.03 * FS))
        env = adsrFadeEnvelope(a, d, s, r, sustainAmp=0.4, fade=4)
    plt.plot(env)
    plt.show()
    for wid in range(5):
        wav = getSinWav(freq, len(env))
        wav *= env
        wavs.append(wav)
        wavs.append(sil)
        freq *= ratio
    wav = np.hstack(wavs)
    wavfile.write('output.wav', FS, wav)


def get_overtone_amplitudes():

    # acoustic guitar (nylon string)
    har_amps = np.array([0.05623413, 0.05011872, 0.00562341, 0.00891251, 0.00316228,
       0.00223872, 0.00223872, 0.00035481, 0.00089125, 0.00070795,
       0.00079433, 0.00039811])

    return har_amps



def additiveSynth(freq, dur, vol):
    '''
    returns a synthesized sound by adding several partials
    freq : frequency of fundamental (in Hz)
    dur  : duration in seconds (only controls sustain)
    vol  : volume (linear)
    '''

    # Strength of the random variation for volume and frequency (set to 0 for no variation),
    # given as relative units (e.g., 0.15 is 15% deviation from the original value):
    rand_vol =  0.15
    rand_freq = 0.001

    harjump  = 1
  
    attack   = iround(0.0008 * FS)
    decay    = iround(0.03  * FS)
    sustain  = iround(dur   * FS)
    release  = iround(0.02  * FS)

    har_amps = get_overtone_amplitudes()
    harlim   = len(har_amps)


    # Random variation in volume
    vol *= 1 + random.gauss(0, rand_vol)

    # Random increases in frequency simulate accidental bendings of strings:
    freq_factor = 1 + abs(random.gauss(0, rand_freq))
    
    # attenuate overtones depending on volume
    har_amps *= np.logspace(0, np.log10(vol + 1e-10), harlim)

    combined   = 0

    for har in range(1, harlim, harjump):

        fhar = freq * har * freq_factor  # frequency for the partial
        if fhar > FS * 0.4:      # respect nyquist
            break
        fade = 2.5 + 0.4 * har      # fade depends on the partial har
        # amp  = (har+2) ** -2.5    # amplitude depends on partial har

        env  = adsrFadeEnvelope(attack, decay, sustain, release,
                                sustainAmp=0.8, fade=fade)

        partial = getSinWav(fhar, len(env), amp=har_amps[har-1]) * env
        combined = combined + partial
    correction = (110 / freq) ** 0.4
    ret = combined / abs(combined).max() * 0.5 * vol * correction

    return ret


def seqManyMuliHarmonicWav():
    'multiple additiveSynth output'
    freq  = 220
    ratio = 6/5
    sil   = np.zeros(FS//10, dtype=F32)
    wavs  = [ sil ]
    for wid in range(10):
        wav = additiveSynth(freq, 2, 1)
        wavs.append(wav)
        wavs.append(sil)
        freq *= ratio
    wav = np.hstack(wavs)
    wavfile.write('output.wav', FS, wav)


def main():
    #justSinWav()
    #seqManySinWavs()
    #seqManySinWavsWithEnv()
    seqManyMuliHarmonicWav()


if __name__ == '__main__':
    main()


# DISCLAIMER:
# -> Only very basic ideas are explored here
# -> I am not presenting anything new or original
# -> Consider this as a fairly good starting point
#    (rather than a `gold standard`)



#har_levels = [-25, -26, -45, -41, -50, -53, -53, -69, -61, -63, -62, -68]