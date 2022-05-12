#!/usr/bin/env python

import numpy as np
from scipy.io import wavfile

import basicsynth as bsynth
from basicsynth import iround, FS, F32
import basicsequencer as bseq
from copy import deepcopy as dcopy

import plotutils


RI = np.random.randint


#== hit patterns


def pickHitPoints(patlen=16, nhit=8):
    'randomly pick nhit points from patlen'
    vec = np.zeros(patlen, dtype=np.int32)
    vec[:nhit] = 1
    np.random.shuffle(vec)
    return vec


def hitSomeMore(hits, nhit=1):
    'randomly add nhit more hits'
    hits = hits.copy()
    pos  = np.arange(len(hits))
    np.random.shuffle(pos)
    rem  = nhit
    for idx in range(len(hits)):
        idx = pos[idx]
        if hits[idx] != 0:
            continue
        hits[idx] = 1
        rem -= 1
        if rem < 1:
            break
    return hits


def hitFamilyProg(patlen=16, start=7, step=1, count=6):
    'create a family for progressively increasing number of hits'
    ret  = []
    hits = pickHitPoints(patlen, start)
    ret.append(hits)
    for ii in range(count):
        hits = hitSomeMore(hits, step)
        ret.append(hits)
    return ret


def printHits(hits):
    'print hit pattern'
    char = '.x'
    pstr = ' '.join((char[i] for i in hits))
    print(pstr)


#== tone curve

def norm01(vec):
    'normalize vec between 0 and 1'
    vec -= vec.min()
    vec /= vec.max()
    return vec


def toneCurve(patlen=16, wlen=8, incli=0):
    'generate curve for picking tones'
    nsize  = patlen
    if wlen > 1:
        nsize += 2 * wlen
    noise  = np.random.rand(nsize)
    if wlen > 1:
        win    = np.hamming(wlen)
        noise = np.convolve(noise, win, 'same')[wlen:-wlen]
    if incli != 0:
        noise += np.linspace(0, incli, len(noise))
    noise = norm01(noise)
    return noise


def combineToneCurves(curv1, curv2, beta=0.3):
    'combine two tone curves. beta decides the weight for curv2'
    ret = curv1 * (1 - beta) + curv2 * beta
    ret = norm01(ret)
    return ret


def curveFamilyProg(patlen=16, wlen=10, incli=0, beta=0.2, count=6):
    'produces a family of curves'
    ret  = []
    curve1 = toneCurve(patlen, wlen, incli)
    curve2 = toneCurve(patlen, wlen, incli)
    ret.append(curve1)
    for ii in range(count):
        mixed = combineToneCurves(curve1, curve2, beta*ii)
        ret.append(mixed)
    return ret


#== keys


def assembleMelody(keys, hits, curve):
    'assemble melody from keys, hits and curve'
    scale  = len(keys) - 0.01
    curve  = curve * scale
    toneidx = np.int32(curve)
    ret    = []
    for ht, idx in zip(hits, toneidx):
        key = None
        if ht == 1:
            key = keys[idx]
        ret.append(key)
    return ret


def elongate(pat, dist=2):
    'add dur to fill the silence'
    rpat = [ fr.copy() if fr else None for fr in pat[::-1] ]
    ctr  = 0
    for fr in rpat:
        if ctr >= dist and fr is not None:
            fr[2] += ctr
        if fr is None:
            ctr += 1
        else:
            ctr = 0
    rpat = rpat[::-1]
    return rpat


def oksplt(key):
    return int(key[0]), key[1:]


def expandKeypat(keypat, dur=1, vol=0):
    'expand key pattern with each frame containing list of tones'
    ret = []
    for frame in keypat:
        cur = None
        if frame is not None:
            oc, key = oksplt(frame)
            cur = [ oc, key, dur, vol ]
        ret.append(cur)
    ret = elongate(ret)
    ret = [ [el] if el else [] for el in ret ]
    return ret


def pat2wav(pat, tstep=12000, extradur=0.25):
    'convert pattern to wav. patten should be list of list of 4-length tone-info'
    dur = tstep / FS
    music = []
    for idx, frame in enumerate(pat):
        vecs = []
        for val in frame:
            vec = bsynth.sampleSynth(val[0], val[1], dur*val[2] + extradur, val[3])
            vecs.append(vec)
        music.append(vecs)
    music = bseq.sequenceDirect(music, tstep)
    return music


def attachSilence(pattern, nl=8, nr=8):
    'attach silence to both ends of the pattern'
    left  = [ [] for ii in range(nl) ]
    right = [ [] for ii in range(nr) ]
    ret   = []
    ret.extend(left)
    ret.extend(pattern)
    ret.extend(right)
    return ret


def repeatPatten(pat, count):
    'repeat patten pat count times'
    ret = []
    for idx in range(count):
        ret.extend(dcopy(pat))
    return ret


def addBackground(pattern, keys, dur=4, vol=-3):
    keys = keys.split()
    for idx, frame in enumerate(pattern):
        key = keys[idx%len(keys)]
        if key == '-':
            continue
        o, k = oksplt(key)
        frame.append([o, k, dur, vol])
    return pattern


def testSingleMelody():
    np.random.seed(12)
    keys   = '5c 5d 5e 5f'.split()
    for step in range(7):
        hits   = pickHitPoints(16, 7)
        curve  = toneCurve(16, 0, 0)
        plotutils.plotMelodyGen(step, keys, hits, curve)
    return
    melody = assembleMelody(keys, hits, curve)
    melody = expandKeypat(melody)
    melody = repeatPatten(melody)
    melody = attachSilence(melody)
    music  = addBackground(melody, '7c - 2c - - 2c - -', 4)
    music  = pat2wav(melody, 12000)
    wavfile.write('melody.wav', FS, music)


def generatePlots():
    keys   = '5c 5d 5e 5f'.split()
    for step in range(10):
        wsize = 0
        if step >= 8:
            wsize = 4
        np.random.seed(12)
        hits   = pickHitPoints(16, 7)
        curve  = toneCurve(16, wsize, 0)
        plotutils.plotMelodyGen(step, keys, hits, curve)


def extMelodyPart(li, k, h, c, b):
    k   = k.split()
    mel = assembleMelody(k, h, c)
    mel = expandKeypat(mel)
    mel = addBackground(mel, b)
    li.extend(mel)


def onlyBackground(li, nf, b):
    mel = [ [] for f in range(nf) ]
    mel = addBackground(mel, b)
    li.extend(mel)


def testMultiPartMelody():
    #seed = 11
    np.random.seed(11)
    P = extMelodyPart
    S = onlyBackground

    k1a = '5c 5d 5f 5e'
    k1b = '4c 4d 4f 4e'
    k1c = '5c 5f 5d 5e'

    h1a = pickHitPoints(8, 4)
    h1b = hitSomeMore(h1a, 1)
    h1c = hitSomeMore(h1a, 2)
    c1u = toneCurve(8, 10, 0.5)
    c1d = toneCurve(8, 10, -0.5)

    b1a = '7c - - - 2c - - -'
    b1b = '7c - 3c - 6c - 2c -'
    b1c = '6e - 3c - 2g - 2c -'

    mus = []

    S(mus, 16, b1a)
    P(mus, k1a, h1a, c1u, b1a)
    P(mus, k1a, h1a, c1d, b1a)
    P(mus, k1a, h1a, c1u, b1a)
    P(mus, k1a, h1b, c1d, b1a)

    S(mus, 16, b1b)
    P(mus, k1a, h1a, c1u, b1b)
    P(mus, k1a, h1a, c1d, b1b)
    P(mus, k1a, h1a, c1u, b1b)
    P(mus, k1a, h1b, c1d, b1b)

    np.random.rand(52)
    h2a = pickHitPoints(8, 4)
    h2b = hitSomeMore(h2a, 1)
    h2c = hitSomeMore(h2a, 2)
    c2u = toneCurve(8, 10, 1)
    c2d = toneCurve(8, 10, -1)

    S(mus, 8, b1a)
    P(mus, k1b, h2a, c2u, b1a)
    P(mus, k1b, h2a, c2d, b1a)
    P(mus, k1b, h2a, c2u, b1a)
    P(mus, k1b, h2b, c2d, b1a)

    S(mus, 8, b1b)
    P(mus, k1b, h2a, c2u, b1b)
    P(mus, k1b, h2a, c2d, b1b)
    P(mus, k1b, h2a, c2u, b1b)
    P(mus, k1b, h2b, c2d, b1b)

    S(mus, 8, b1b)
    P(mus, k1b, h1a, c1u, b1b)
    P(mus, k1b, h1a, c1d, b1b)
    P(mus, k1b, h1a, c1u, b1b)
    P(mus, k1b, h1b, c1d, b1b)
    S(mus, 8, b1b)

    S(mus, 8, b1c)
    for _ in range(2):
        S(mus, 8, b1c)
        P(mus, k1c, h2a, c2u, b1c)
        P(mus, k1c, h2a, c2d, b1c)
        P(mus, k1c, h2a, c2u, b1c)
        P(mus, k1c, h2b, c2d, b1c)

    S(mus, 8, b1c)
    P(mus, k1b, h1a, c1u, b1c)
    P(mus, k1b, h1a, c1d, b1c)
    P(mus, k1b, h1a, c1u, b1c)
    P(mus, k1b, h1b, c1d, b1c)
    S(mus, 16, b1c)

    music  = pat2wav(mus, 8000) * 0.5
    wavfile.write('melody.wav', FS, music)


def main():
    generatePlots()
    #testSingleMelody()
    #testMultiPartMelody()


if __name__ == '__main__':
    main()



