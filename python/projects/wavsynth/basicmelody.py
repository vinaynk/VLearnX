#!/usr/bin/env python

# --
# NOTE: Output melody license follows CC BY 3.0
# (attribution to Vinay, Moritz and others at VLearnX)
# https://creativecommons.org/licenses/by/3.0/
# --
# NOTE: Attribution is also required for samples
# for each melody generated.
# Check the folders under samples dir for more info
# on attribution for respective instrument samples
# --

import numpy as np
from scipy.io import wavfile

import basicsynth as bsynth
from basicsynth import iround, FS, F32
import basicsequencer as bseq
from copy import deepcopy as dcopy

from matplotlib import pyplot as plt

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
    char = '.↓'
    pstr = ' '.join((char[i] for i in hits))
    print(pstr, '\n')


def testHitPatterns():
    # np.random.seed(3)
    print('4 out of 8')
    p1 = pickHitPoints(8, 4)
    printHits(p1)
    print('6 out of 16')
    p2 = pickHitPoints(16, 6)
    printHits(p2)
    print('Variation of the above')
    p3 = hitSomeMore(p2, 2)
    printHits(p3)


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
    if incli != 0:
        noise += np.linspace(0, incli, len(noise))
    if wlen > 1:
        win    = np.hamming(wlen)
        noise = np.convolve(noise, win, 'same')[wlen:-wlen]
    noise = norm01(noise)
    return noise


def combineToneCurves(curv1, curv2, beta=0.3):
    'combine two tone curves. beta decides the weight for curv2'
    ret = curv1 * (1 - beta) + curv2 * beta
    ret = norm01(ret)
    return ret


def curveFamilyProg(patlen=16, wlen=10, incli=0,
                    beta=0.2, count=6):
    'produces a family of curves'
    ret  = []
    curve1 = toneCurve(patlen, wlen, incli)
    curve2 = toneCurve(patlen, wlen, incli)
    ret.append(curve1)
    for ii in range(count):
        mixed = combineToneCurves(curve1, curve2, beta*ii)
        ret.append(mixed)
    return ret


def testToneCurves():
    np.random.seed(1)
    curve1 = toneCurve(16, 0, 0)        # direct
    curve2 = toneCurve(16, 10, 0)       # smoothing
    plt.plot(curve1)
    plt.plot(curve2)
    plt.legend(['raw', 'smoothed' ], fontsize=15)
    plt.title('Raw vs Smooth', fontsize=15)
    plt.show()
    curve3 = toneCurve(16, 20, 1)       # inclination up
    curve4 = toneCurve(16, 20, -1)      # inclination down
    plt.plot(curve3)
    plt.plot(curve4)
    plt.legend(['inclination up', 'inclination down'],
               fontsize=15)
    plt.show()



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
    '''
    convert pattern to wav.
    patten should be list of list of 4-length tone-info
    '''
    dur = tstep / FS
    music = []
    for idx, frame in enumerate(pat):
        vecs = []
        for val in frame:
            vec = bsynth.sampleSynth(
                    val[0], val[1], dur*val[2] + extradur,
                    val[3])
            vecs.append(vec)
        music.append(vecs)
    music = bseq.sequenceDirect(music, tstep) * 0.5
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


def chordKeyseqExpand(keys, dur=4, vol=-3):
    keys = keys.split()
    keys = [ k.split(',') for k in keys ]
    def kmapExp(ok):
        o, k = oksplt(ok)
        return [o, k, dur, vol]
    ret  = []
    for ki in keys:
        fr = [ kmapExp(k) for k in ki if k != '-' ]
        ret.append(fr)
    return ret


def addBackground(pattern, keys, dur=4, vol=-3):
    keys = chordKeyseqExpand(keys)
    for idx, frame in enumerate(pattern):
        keyseq = keys[idx%len(keys)]
        frame.extend(dcopy(keyseq))
    return pattern


def testSingleMelody():
    np.random.seed(11)
    #np.random.seed(9)
    keys   = '5c 5d 5e 5f'.split()
    hits   = pickHitPoints(16, 7)
    curve  = toneCurve(16, 10, -1)
    #plt.plot(curve); plt.show()
    melody = assembleMelody(keys, hits, curve)
    #print('\nassembleMelody output:\n', melody, sep='')
    melody = expandKeypat(melody)
    #print('\nexpandKeypat output:\n', melody, sep='')
    #print('\n4-list: [octave, key, dur, vol(db)]')
    melody = attachSilence(melody, 8, 8)
    music  = addBackground(melody, '7c - 2c - 6c 2c - 6d', 4)
    music  = pat2wav(melody, 8000)
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


def expand(*args):
    return args


def merge(pat1, pat2):
    return [ expand(*x1, *x2) for x1, x2 in zip(pat1, pat2) ]


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

    music  = pat2wav(mus, 8000)
    wavfile.write('melody.wav', FS, music)


def testChordKeyseqExpand():
    keys = '7c,3c - - 7c - 3c 7a - 2c,2d'
    exp  = chordKeyseqExpand(keys)
    print(exp)



def main():
    #testToneCurves()
    #testHitPatterns()
    #generatePlots()
    #testSingleMelody()
    testMultiPartMelody()
    #testChordKeyseqExpand()


if __name__ == '__main__':
    main()



