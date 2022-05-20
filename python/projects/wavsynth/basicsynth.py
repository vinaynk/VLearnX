#!/usr/bin/env python

import numpy as np
import re
from scipy.io import wavfile
from matplotlib import pyplot as plt

from functools import lru_cache
import soundfile as sf


FS  = 48000         # project sampling rate
F32 = np.float32    # useful alias


def iround(x):
    return int(round(x))


@lru_cache(maxsize=None)
def getSinWav(freq, nsamp, amp=0.2):
    tx    = np.arange(nsamp)
    wav   = np.sin(2 * np.pi * freq / FS * tx) * amp
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
    env = [
        np.linspace(0, 1, attack),
        np.linspace(1, sustainAmp, decay),
        np.exp(-np.linspace(0, fade, sustain)) * sustainAmp,
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


def additiveSynth(freq, dur, vol):
    '''
    returns a synthesized sound by adding several partials
    freq : frequency of fundamental (in Hz)
    dur  : duration in seconds (only controls sustain)
    vol  : volume (linear)
    '''
    harlim   = 40
    harjump  = 5

    attack   = iround(0.003 * FS)
    decay    = iround(0.03  * FS)
    sustain  = iround(dur   * FS)
    release  = iround(0.02  * FS)

    combined   = 0
    for har in range(1, harlim, harjump):
        fhar = freq * har         # frequency for the partial
        if fhar > FS * 0.4:      # respect nyquist
            break
        fade = 2.5 + 0.4 * har      # fade depends on the partial har
        amp  = (har+2) ** -2.5    # amplitude depends on partial har
        env  = adsrFadeEnvelope(attack, decay, sustain, release,
                                sustainAmp=0.8, fade=fade)
        partial = getSinWav(fhar, len(env), amp=amp) * env
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


def keymapEqTemp():
    '''
    Returns a dict that maps (octave, keyname) to its freq in Hz
    (Tuning scheme: equal temperament)
    '''
    f0   = 55 # 55 is the usual default
    # keys = 'a a# b c c# d d# e f f# g g#'.split()
    # NOTE: we are starting with C now on
    keys = 'c c# d d# e f f# g g# a a# b'.split()
    fvec = []
    keymap = {}
    for oc in range(0, 5):
        for idx, key in enumerate(keys):
            # f[k] = α f[k-1] ; α = 2 ** (1/12)
            fkey = f0 * 2 ** (oc + idx/12)
            fvec.append(fkey)
            keymap[(oc, key)] = fkey
            #print(f'{oc:}\t{key:4}\t{fkey:.2f}')
    return keymap


def keyPatten():
    'returns regex to match <oc><key>[<dur>][+/-<vol>]'
    octave = '([0-5])'
    key    = '(a|a#|b|c|c#|d|d#|e|f|f#|g|g#)'
    dur    = '([1-9]+)?' #optional
    vol    = '([+-][0-9]+)?' #optional
    patt   = f'^{octave}{key}{dur}{vol}$'
    return re.compile(patt)


_keymap  = keymapEqTemp()
_keypatt = keyPatten()


def parseKey(key):
    '''
    parse a key of the form 3c#4+2
    return a 4-tuple of octave, key, duration, volume
    '''
    mt  = _keypatt.match(key.strip())
    oc  = int(mt.group(1))
    key = mt.group(2)
    dur = mt.group(3)
    dur = 1 if dur is None else int(dur)
    vol = mt.group(4)
    vol = 0 if vol is None else int(vol)
    return oc, key, dur, vol


def kt4fdv(kt4):
    '4tuple key params to freq, dur, vol'
    f = _keymap[(kt4[0], kt4[1])]
    d = kt4[2]
    v = 10 ** (kt4[3]/10)    # similar to dB
    return f, d, v


def getSampleEnv(dur):
    dur  = int(dur * FS)
    fall = int(0.2 * FS)
    env = np.hstack([ np.ones(dur), np.linspace(1, 0, fall) ])
    return env


def applyEnv(audio, dur, vol):
    vol1 = 10 ** (vol / 10)
    audio = audio / abs(audio).max() * 0.5 * vol1
    env   = getSampleEnv(dur)
    if len(audio) > len(env):
        audio = audio[:len(env)]
    audio *= env
    return F32(audio)


def pianoSample(octave, key, dur, vol):
    key = key.upper()
    fname = f'samples/piano/{octave}{key}.ogg'
    audio, rate = sf.read(fname)
    assert rate == FS
    audio = applyEnv(audio, dur, vol)
    return audio


__dmap = { 'H' : 'samples/home/',
           'K' : 'samples/drumkit/' }

def loadByWavlist(key, dur, vol):
    srcdir = __dmap[key[0]]
    idx = int(key[1:]) # this is the line number
    with open(f'{srcdir}/wavlist.txt') as fi:
        lines = [ line.strip() for line in fi ]
    fname = lines[idx-1]
    audio, rate = sf.read(f'{srcdir}/{fname}')
    assert rate == FS
    audio = applyEnv(audio, dur, vol)
    return F32(audio)


@lru_cache(maxsize=None)
def sampleSynth(octave, key, dur, vol):
    if key[0] == 'P':
        ret = pianoSample(octave, key[1:], dur, vol)
    elif key[0] in __dmap:
        ret = loadByWavlist(key, dur, vol)
    else:
        ret = pianoSample(octave, key, dur, vol)
    return ret


def testSampleSynth():
    #data = sampleSynth(6, 'a', 2, 0)
    data = sampleSynth(6, 'H4', 2, 0)
    plt.plot(data); plt.show()
    #print(rate, data.shape, data.dtype)


def main():
    #justSinWav()
    #seqManySinWavs()
    #seqManySinWavsWithEnv()
    #seqManyMuliHarmonicWav()
    testSampleSynth()


if __name__ == '__main__':
    main()


# DISCLAIMER:
# -> Only very basic ideas are explored here
# -> I am not presenting anything new or original
# -> Consider this as a fairly good starting point
#    (rather than a `gold standard`)



