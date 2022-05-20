#!/usr/bin/env python

import numpy as np
from scipy.io import wavfile

from basicmelody import *


def waltz():
    r0  = '1c - - - 2a,3c,3f - - - 2a,3c,3f - - -'
    r1  = '1c - - - 2g,2b,3d - - - 2g,2b,3d - - -'
    r2  = '1c - - - 2a,3c,3d,3f - - - 2a,3c,3d,3f - - -'
    r3  = '1c - - - 2a,3c,3d,3f# - - - 2a,3c,3d,3f# - - -'


def music001():
    addBackground.bgdur = 4
    addBackground.bgvol = -2

    P = extMelodyPart
    S = onlyBackground

    #k0 = '4a 5c 5f '
    k0 = '4c 4e 4f 4g'
    k1 = '4c 3b 4d 4f'
    k2 = '5c 5e 5f 5g'

    #seeds = [7501496, 2547839, 1218422, 1478992]
    seeds = np.int32(np.random.rand(4) * 100000)
    print(seeds)
    ur = lambda : np.random.uniform(-1, 1)

    np.random.seed(seeds[0])
    h1a = pickHitPoints(16, 8)
    h1b = hitSomeMore(h1a, 1)
    h1c = hitSomeMore(h1a, 1)
    c1u = toneCurve(16, 14, ur())
    c1d = toneCurve(16, 14, ur())
    np.random.seed(seeds[1])
    h2a = pickHitPoints(16, 8)
    h2b = hitSomeMore(h2a, 1)
    h2c = hitSomeMore(h2a, 1)
    c2u = toneCurve(16, 9, ur())
    c2d = toneCurve(16, 9, ur())
    np.random.seed(seeds[2])
    h3a = pickHitPoints(16, 8)
    h3b = hitSomeMore(h3a, 1)
    h3c = hitSomeMore(h3a, 1)
    c3u = toneCurve(16, 9, ur())
    c3d = toneCurve(16, 9, ur())
    np.random.seed(seeds[3])
    h4a = pickHitPoints(16, 8)
    h4b = hitSomeMore(h4a, 1)
    h4c = hitSomeMore(h4a, 1)
    c4u = toneCurve(16, 9, ur())
    #c4d = toneCurve(16, 9, 0)
    c4d = c4u

    r0  = '2a - 3c - 3f - 3c - 2a - 3c - 3f - 3c -'
    r1  = '2g - 2b - 3d - 2b - 2g - 2b - 3d - 2b -'
    r2  = '2a - 3d - 3f - 3d - 2a - 3d - 3f - 3d -'
    r3  = '2a - 3d - 3f# - 3d - 2a - 3d - 3f# - 3d -'

    mus = []

    #-- S(mus, 16, r0)
    #-- S(mus, 16, r1)
    #-- S(mus, 16, r2)
    #-- S(mus, 16, r3)

    for ii in range(2):
        P(mus, k0, h1a, c1u, r0)
        P(mus, k0, h1b, c1u, r1)
        P(mus, k0, h1a, c1d, r2)
        P(mus, k0, h1c, c1d, r3)
        P(mus, k1, h2a, c2u, r0)
        P(mus, k1, h2b, c2d, r1)
        P(mus, k1, h2a, c2u, r2)
        P(mus, k1, h2c, c2d, r3)

    for ii in range(2):
        P(mus, k0, h1a, c1u, r0)
        P(mus, k0, h1b, c1u, r1)
        P(mus, k0, h1a, c1d, r2)
        P(mus, k0, h1c, c1d, r3)
        P(mus, k2, h3a, c3u, r0)
        P(mus, k2, h3b, c3d, r1)
        P(mus, k2, h3a, c3u, r2)
        P(mus, k2, h3c, c3d, r3)

    r0  = '2a - 3c - 3f - 3c - 1c,2a - 3c - 3f - 3c -'
    r1  = '2g - 2b - 3d - 2b - 1b,2g - 2b - 3d - 2b -'
    r2  = '2a - 3d - 3f - 3d - 1d,2a - 3d - 3f - 3d -'
    r3  = '2a - 3d - 3f# - 3d - 1d,2a - 3d - 3f# - 3d -'


    for ii in range(2):
        P(mus, k0, h2a, c2u, r0)
        P(mus, k0, h2b, c2u, r1)
        P(mus, k0, h2a, c2d, r2)
        P(mus, k0, h2c, c2d, r3)
        P(mus, k2, h4a, c4u, r0)
        P(mus, k2, h4b, c4d, r1)
        P(mus, k2, h4a, c4u, r2)
        P(mus, k2, h4c, c4d, r3)

    P(mus, k2, h3a, c3u, r0)
    P(mus, k2, h3b, c3d, r1)
    P(mus, k2, h3a, c3u, r2)
    P(mus, k2, h3c, c3d, r3)

    P(mus, k2, h4a, c4u, r0)
    P(mus, k2, h4b, c4d, r1)
    P(mus, k2, h4a, c4u, r2)
    P(mus, k2, h4c, c4d, r3)

    P(mus, k0, h4a, c1u, r0)
    P(mus, k0, h4c, c1d, r1)

    S(mus, 16, r2)
    S(mus, 16, r3)

    music  = pat2wav(mus, 8000, 0.5)
    wavfile.write('melody.wav', FS, music)


def music002():
    addBackground.bgdur = 6
    addBackground.bgvol = -4

    _seeds = [17, 11, 7, 0, 0, 0, 0, 0, 0, 0, 0]
    def seeder(idx):
        np.random.seed(idx * 10000 + _seeds[idx])

    P = extMelodyPart
    S = onlyBackground
    Q = extMelodySeqPart
    B = addBackground


    mus = []

    r1a = '1b - 2c,6c - 6e  - 7c - '
    r2a = '1b - 2e,6c - 6f  - 6c - '
    r3a = '1b - 2c,6c - 6f  - 7c - '
    r4a = '1b - 2e,6c - 6f# - 6c - '
    ra  = r1a + r2a + r3a + r4a

    r1b = 'K33,1b - 2c,6c - K31,6e - 2f,7c - '
    r2b = 'K33,1b - 2e,6c - K25,6f  - 2f#,6c - '
    r3b = 'K33,1b - 2c,6c - K31,6f  - 2f,7c - '
    r4b = 'K33,1b - 2e,6c - K30,6f# - 2f#,6c - '
    rb  = r1b + r2b + r3b + r4b

    r1c = 'K33,1b - 2c,6c - K52,6e  - 2f,7c - '
    r2c = 'K33,1b - 2e,6c - K30,6f  - 2f#,6c - '
    r3c = 'K33,1b - 2c,6c - K58,6f  - 2f,7c - '
    r4c = 'K33,1b - 2e,6c - K50,6f# - 2f#,6c - '
    rc  = r1c + r2c + r3c + r4c

    k0 = '5c 5d 5f# 5g'
    k1 = '4c 4d 4f# 4g'
    k2 = '5c 5e 5f# 5g'
    k3 = '4c 4e 4f# 4g'

    seeder(0)
    h1a = pickHitPoints(8, 4)
    h1b = hitSomeMore(h1a, 1)
    h1c = hitSomeMore(h1a, 1)
    c1u = toneCurve(8, 4, 0.6)
    c1d = toneCurve(8, 8, -0.4)

    seeder(1)
    h2a = pickHitPoints(8, 5)
    h2b = hitSomeMore(h2a, 1)
    h2c = hitSomeMore(h2a, 1)
    c2u = toneCurve(8, 2, 0.9)
    c2d = toneCurve(8, 2, -0.9)
    c2u1 = toneCurve(8, 4, 0.9)
    c2d1 = toneCurve(8, 4, -0.9)

    seeder(2)
    h3a = pickHitPoints(8, 4)
    h3b = hitSomeMore(h3a, 1)
    h3c = hitSomeMore(h3a, 1)
    c3u = toneCurve(8, 5, 0.8)
    c3d = toneCurve(8, 5, -0.8)
    c3u1 = toneCurve(8, 4, 0.7)
    c3d1 = toneCurve(8, 4, -0.7)

    S(mus, 32, ra)
    # part 1
    P(mus, k0, h1a, c1u, r1b)
    P(mus, k0, h1b, c1u, r2b)
    S(mus, 16, r1c+r2c)
    P(mus, k0, h1a, c1u, r1b)
    P(mus, k0, h1b, c1u, r2b)
    S(mus, 16, r3c+r4c)
    P(mus, k1, h1a, c1u, r3b)
    P(mus, k1, h1b, c1u, r4b)
    P(mus, k1, h1b, c1d, r1b)
    P(mus, k0, h1b, c1d, r2b)
    S(mus, 32, rc)

    P(mus, k2, h2a, c2d, r1b)
    P(mus, k2, h2a, c2d1, r2b)
    P(mus, k2, h2a, c2d, r3b)
    P(mus, k2, h2a, c2d1, r4b)
    P(mus, k1, h1a, c1u, r1b)
    P(mus, k1, h1b, c1u, r2b)
    P(mus, k2, h2a, c2d, r3b)
    P(mus, k2, h2a, c2d1, r4b)
    S(mus, 16, r1c+r2c)
    P(mus, k3, h2a, c2u, r1b)
    P(mus, k3, h2a, c2u1, r2b)
    P(mus, k3, h2b, c2u, r3b)
    P(mus, k3, h2a, c2u1, r4b)
    S(mus, 16, r3c+r4c)
    P(mus, k0, h1a, c1u, r1b)
    P(mus, k0, h1b, c1u, r2b)
    P(mus, k3, h2b, c2u, r3b)
    P(mus, k3, h2a, c2u1, r4b)

    addBackground.bgvol = -3
    S(mus, 32, rc)

    P(mus, k1, h3b, c3u, r1b)
    P(mus, k1, h3c, c3u, r2b)
    P(mus, k1, h3a, c3d, r3b)
    P(mus, k1, h3c, c3d, r4b)
    S(mus, 16, r1c+r2c)
    P(mus, k0, h3b, c3u, r1b)
    P(mus, k0, h3c, c3u, r2b)
    P(mus, k0, h3a, c3d, r3b)
    P(mus, k0, h3c, c3d, r4b)
    S(mus, 16, r3c+r4c)
    P(mus, k2, h2b, c3u, r1b)
    P(mus, k2, h2c, c3u, r2b)
    P(mus, k2, h2c, c3d, r3b)
    P(mus, k2, h2a, c3d, r4b)
    S(mus, 16, r1c+r2c)
    P(mus, k1, h3b, c3u, r1b)
    P(mus, k1, h3c, c3u, r2b)
    P(mus, k1, h3a, c3d, r3b)
    P(mus, k1, h3c, c3d, r4b)
    S(mus, 16, r1c+r2c)
    P(mus, k1, h1a, c1u, r3b)
    P(mus, k1, h1b, c1u, r4b)
    P(mus, k1, h1b, c1d, r1b)
    P(mus, k0, h1b, c1d, r2b)
    S(mus, 16, r3c+r4c)

    music  = pat2wav(mus, 14000, 0.5) * 0.5
    wavfile.write('melody.wav', FS, music)


def music003():
    addBackground.bgdur = 4
    addBackground.bgvol = -2

    P = extMelodyPart
    S = onlyBackground

    #k0 = '4a 5c 5f '
    k0 = [ '4c 4d 4e 4g 4a', '3c 3d 3e 3g' ]
    k2 = '5c 5e 5f 5g'

    cyc = 8

    # np.random.seed(3)
    mset = []
    for tr in range(2):
        hitset = []
        for ii in range(2):
            h1 = pickHitPoints(cyc, 4)
            h2 = hitSomeMore(h1, 1)
            hitset.append((h1, h2))
        hits = []
        nh   = 32
        for ii in range(nh):
            h1, h2 = choice(hitset)
            hits.extend(h1)
            hits.extend(h2)
        curvs = []
        for ii in range(nh*2):
            curv = toneCurve(cyc, 4 + tr*4, 0)
            curvs.append(curv)
        curv = np.hstack(curvs)
        #plt.plot(curv); plt.show()

        mus = []
        P(mus, k0[tr], hits, curv)
        mset.append(mus)

    for m in mset[1]:
        if m:
            m[0][-1] = -4
    mus = merge(*mset)

    music  = pat2wav(mus, 8000, 2)
    wavfile.write('melody.wav', FS, music)


def main():
    music002()


if __name__ == '__main__':
    main()




