#!/usr/bin/env python

"""
Some changes of the basicsequencer by vinaynk that are geared towards more realistically sounding music:
   * random variations in timing
   * slight delay between notes of a chord
   * chords are played louder than single notes
   
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


import random
import re
import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt

import basicsynth_realistic as synth

FS  = synth.FS
F32 = synth.F32
random.seed(0)


def sumVecs(vecList):
    'sum all vecs(potentially of diff len) in a list'
    if not vecList:
        return np.zeros(1, dtype=F32)
    maxSize = max([len(vec) for vec in vecList])
    ret = np.zeros(maxSize, dtype=F32)
    for vec in vecList:
        ret[:len(vec)] += vec
    return ret


def sequenceDirect(llvec, step):
    '''
    naive sequencing of key sounds
    llvec : list of list of f32 vecs
    step  : number of samples for each step
    '''
    pos = 0
    maxSize = 0
    frames = []
    # combine vecs in all frames, find out max size
    for vecList in llvec:
        sv = sumVecs(vecList)
        frames.append(sv)
        pos += step
        if pos + len(sv) > maxSize:
            maxSize = pos + len(sv)
    ret = np.zeros(maxSize, dtype=F32)
    pos = 0
    # sequence all the vectors
    for vec in frames:
        ret[pos:pos+len(vec)] += vec
        pos += step
    return ret


def sequenceApVsGp():
    'How to map keys to frequencies?'
    for jump in 'ap gp'.split():
        freq = 200
        frames = []       # frames[n] -> list of vecs
        frames.append([]) # initial sil
        for idx in range(12):
            vec = synth.additiveSynth(freq, 1, 1) # generate sound
            frames.append([vec])
            if jump == 'ap':
                freq += 20     # for AP
            else:
                freq *= 11/10  # for GP
            if idx == 6:
                freq = 1400    # jump in frequency
        combined = sequenceDirect(frames, 12000)
        wavfile.write(f'output-{jump}.wav', FS, combined)


def keymapEqTemp():
    '''
    Returns a dict that maps (octave, keyname) to its freq in Hz
    (Tuning scheme: equal temperament)
    '''
    f0   = 80 # 55 is the usual default
    keys = 'a a# b c c# d d# e f f# g g#'.split()
    fvec = []
    keymap = {}
    for oc in range(0, 5):
        for idx, key in enumerate(keys):
            # f[k] = α f[k-1] ; α = 2 ** (1/12)
            fkey = f0 * 2 ** (oc + idx/12)
            fvec.append(fkey)
            keymap[(oc, key)] = fkey
            #print(f'{oc:}\t{key:4}\t{fkey:.2f}')
    if 0:
        fvec = np.array(fvec)
        fvec = np.log2(fvec)
        plt.plot(fvec)
        plt.xlabel('Key index')
        plt.ylabel('log2(fkey)')
        plt.show()
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


def testParseKey():
    keys = '2a# 3b+3 1d2 4e2-3 2b 3g4+4'.split()
    for key in keys:
        kt4 = parseKey(key)
        fdv = kt4fdv(kt4)
        fdv = '{:.2f} {} {:.2f}'.format(*fdv)
        print(f'{key} {kt4} {fdv}')


def str2klseq(data):
    'string to list of list keys'
    data = data.split('|')
    data = [ token.split() for token in data ]
    return data


def klseq2music(klseq, kdur=1, step=8000):
    '''
    returns music array from seq of list of keys
    klseq : list of list of keys
    kdur  : base key duration
    step  : step in samples
    '''

    # Strength of the random variation in timing in seconds (set to 0 for no variation)
    rand_timing = 0.005

    # delay between indvidual notes of a chord in seconds
    chord_note_offset = 0.025


    llvec = []
    for frame in klseq: # each frame is a list of keys
        frvecs = []     # vecs for frame

        # Increase volume if there is more than one note at once, as seen in human instrumentalists:
        boost = len(frame) > 1 
        
        for ii, key in enumerate(frame):
            kt4 = parseKey(key)   # key(str) -> (octave, key, dur, vol)
            f, d, v = kt4fdv(kt4) # -> (freq, dur, vol)
            vec = synth.additiveSynth(f, d * kdur, v + 0.25*v*boost) # -> sample vec

            # Add random delay to each onset and a constant delay between notes of chords 
            delay_offset = FS*chord_note_offset
            delay_rand = FS*(abs(random.gauss(0, rand_timing)))
            delay = int(ii*delay_offset + delay_rand)
            vec = np.r_[np.zeros(delay),
                        vec,
                        np.zeros((len(frame)-ii) * delay)]

            frvecs.append(vec)
        llvec.append(frvecs)
    music = sequenceDirect(llvec, step)
    return music


def readStripComments(fi):
    'remove lines starting with # and return combined data'
    ret = []
    for line in fi:
        line = line.strip()
        if line.startswith('#'):
            continue
        ret.append(line)
    ret = ' '.join(ret)
    return ret


def txt2wav(inp, out):
    'load txt from inp and write wav to out'
    with open(inp) as fi:
        data = readStripComments(fi)
    data = str2klseq(data)
    music = klseq2music(data, 1, 12000)
    wavfile.write(out, FS, music)


def generateMusic():
    txt2wav('fur-elise.txt', 'fur-elise.wav')
    #txt2wav('my-music.txt', 'my-music.wav')


def main():
    #sequenceApVsGp()
    #testParseKey()
    generateMusic()


if __name__ == '__main__':
    main()



