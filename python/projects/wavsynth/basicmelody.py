#!/usr/bin/env python

import numpy as np
from scipy.io import wavfile

from matplotlib import pyplot as plt

import basicsynth as bsynth
from basicsynth import iround, FS, F32
import basicsequencer as bseq
from copy import deepcopy as dcopy


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


def hitFamilyProg(patlen=16, start=6, step=1, count=6):
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
    if incli != 0:
        noise += np.linspace(0, incli, nsize)
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


def curveFamilyProg(patlen=16, wlen=20, incli=1, beta=0.1, count=6):
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
    scale  = len(keys) - 0.1
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


def addBackground(pattern, keys, dur=1, vol=-4):
    keys = keys.split()
    for idx, frame in enumerate(pattern):
        key = keys[idx%len(keys)]
        if key == '-':
            continue
        o, k = oksplt(key)
        frame.append([o, k, dur, vol])
    return pattern


def testSingleMelody():
    np.random.seed(3)
    keys   = '5c 5e 5d 5f'.split()
    hits   = pickHitPoints(16, 6)
    curve  = toneCurve(16, 4, 1)
    melody = assembleMelody(keys, hits, curve)
    melody = expandKeypat(melody)
    melody = repeatPatten(melody, 4)
    melody = attachSilence(melody)
    music  = addBackground(melody, '7c - 2c - - 2c - -', 4)
    music  = pat2wav(melody, 12000)
    wavfile.write('melody.wav', FS, music)



class MultiPartMelodyMusic:

    def __init__(self):
        self.patlen = 16
        self.count  = 10
        self.initKeyset()
        self.initHitSet()
        self.initToneCurves()
        self.initBackground()

    def initKeyset(self):
        keyset = [ '4c 4e 4d 4f 4g', '4c 4f 4g 4a' ]
        self.keyset = [ it.split() for it in keyset ]

    def initHitSet(self):
        self.hitset = []
        for ii in range(self.count):
            hitfam = hitFamilyProg(self.patlen, count=self.count)
            self.hitset.append(hitfam)

    def initToneCurves(self):
        self.curveset = []
        for ii in range(self.count):
            incli = (1 - (ii % 2) * 2) * np.random.rand()
            curvefam = curveFamilyProg(self.patlen, incli=incli, count=self.count)
            self.curveset.append(curvefam)

    def initBackground(self):
        self.backgrounds = [
          '7c - -  - 2c - -  -',
          '6c - 3c - 2e - 2g -',
          '6c - 3c - 3d - 2c 2d',
        ]

    def makePattern(self, li, k, hf, hi, cf, ci, bi, padl=0, padr=0, rpt=1):
        keys = self.keyset[k]
        hits = self.hitset[hf][hi]
        curv = self.curveset[cf][ci]
        bg   = self.backgrounds[bi]

        melody = assembleMelody(keys, hits, curv)
        melody = expandKeypat(melody)
        if rpt > 1:
            melody = repeatPatten(melody, rpt)
        melody = attachSilence(melody, padl, padr)
        addBackground(melody, bg)

        li.extend(melody)

    def save(self, fname, tstep=8000, extradur=1):
        seed = np.random.seed
        P    = self.makePattern

        li = []

        #     k  hf hi cf ci bi
        P(li, 0, 0, 0, 0, 0, 0, 8)
        P(li, 0, 0, 0, 0, 0, 0)
        P(li, 0, 0, 1, 0, 1, 0)
        P(li, 0, 0, 1, 1, 0, 1)
        P(li, 0, 0, 2, 1, 1, 1)

        P(li, 0, 2, 1, 2, 0, 1)
        P(li, 0, 2, 2, 2, 1, 1)
        P(li, 1, 2, 2, 3, 1, 1)
        P(li, 1, 2, 3, 3, 1, 1)

        P(li, 0, 3, 0, 2, 0, 2, 8)
        P(li, 1, 3, 1, 2, 0, 2)
        P(li, 1, 3, 1, 2, 5, 2)
        P(li, 0, 2, 2, 3, 1, 2)
        P(li, 1, 2, 3, 3, 1, 2, 0, 8)

        music  = pat2wav(li, tstep, extradur)
        wavfile.write(fname, FS, music)


def testMultiPartMelody():
    np.random.seed(16)
    mm = MultiPartMelodyMusic()
    mm.save('melody.wav')


def main():
    #testSingleMelody()
    testMultiPartMelody()


if __name__ == '__main__':
    main()



