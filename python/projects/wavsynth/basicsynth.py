#!/usr/bin/env python

import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt


FS  = 48000         # project sampling rate
F32 = np.float32    # useful alias


def iround(x):
    return int(round(x))


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
    decay    = iround(0.10  * FS)
    sustain  = iround(dur   * FS)
    release  = iround(0.04  * FS)

    combined   = 0
    for har in range(1, harlim, harjump):
        fhar = freq * har           # frequency for the partial
        if fhar > FS * 0.4:         # respect nyquist (0.4 being safe)
            break
        fade = 4 + 0.3 * har        # fade depends on the partial har
        amp  = (har+0) ** -2.5      # amplitude depends on partial har
        env  = adsrFadeEnvelope(attack, decay, sustain, release,
                                sustainAmp=0.4, fade=fade)
        partial = getSinWav(fhar, len(env), amp=amp) * env
        combined = combined + partial

    ret = combined / abs(combined).max() * 0.5 * vol
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

