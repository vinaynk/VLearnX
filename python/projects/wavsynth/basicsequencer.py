#!/usr/bin/env python

import random
import numpy as np
import sys
from scipy.io import wavfile
from matplotlib import pyplot as plt

import basicsynth as synth

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
    llvec = []
    for frame in klseq: # each frame is a list of keys
        frvecs = []     # vecs for frame
        for key in frame:
            kt4 = synth.parseKey(key)   # key(str) -> (octave, key, dur, vol)
            f, d, v = synth.kt4fdv(kt4) # -> (freq, dur, vol)
            vec = synth.additiveSynth(f, d * kdur, v) # -> sample vec
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



