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
    k0 = '4c 4d 4e 4g 4a'
    k1 = '4c 4d 4e 4f 4a'
    k2 = '5c 5e 5f 5g'

    #seed = 21, 24
    seeds = [113, 213, 303, 404]
    for ii, val in enumerate(seeds):
        #-- if ii == 0:
        #--     seeds[ii] = 7501496
        #-- else:
        seeds[ii] += np.random.randint(0, 10000000)
    seeds = [7501496, 2547839, 1218422, 1478992]
    print(seeds)

    np.random.seed(seeds[0])
    h1a = pickHitPoints(16, 8)
    h1b = hitSomeMore(h1a, 1)
    h1c = hitSomeMore(h1a, 1)
    c1u = toneCurve(16, 14, 1)
    c1d = toneCurve(16, 14, -1)
    np.random.seed(seeds[1])
    h2a = pickHitPoints(16, 8)
    h2b = hitSomeMore(h2a, 1)
    h2c = hitSomeMore(h2a, 1)
    c2u = toneCurve(16, 9, 0.5)
    c2d = toneCurve(16, 9, -0.5)
    np.random.seed(seeds[2])
    h3a = pickHitPoints(16, 7)
    h3b = hitSomeMore(h3a, 1)
    h3c = hitSomeMore(h3a, 1)
    c3u = toneCurve(16, 9, 0)
    c3d = toneCurve(16, 9, 0)
    np.random.seed(seeds[3])
    h4a = pickHitPoints(16, 7)
    h4b = hitSomeMore(h4a, 1)
    h4c = hitSomeMore(h4a, 1)
    c4u = toneCurve(16, 9, 0)
    #c4d = toneCurve(16, 9, 0)
    c4d = c4u

    r0  = '2a - 3c - 3f - 3c - 2a - 3c - 3f - 3c -'
    r1  = '2g - 2b - 3d - 2b - 2g - 2b - 3d - 2b -'
    r2  = '2a - 3d - 3f - 3d - 2a - 3d - 3f - 3d -'
    r3  = '2a - 3d - 3f# - 3d - 2a - 3d - 3f# - 3d -'

    mus = []

    S(mus, 16, r0)
    S(mus, 16, r1)
    S(mus, 16, r2)
    S(mus, 16, r3)

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

    r0  = '2a,7c - 3c - 3f - 3c - 1c,2a - 3c - 3f - 3c -'
    r1  = '2g,7c - 2b - 3d - 2b - 1b,2g - 2b - 3d - 2b -'
    r2  = '2a,7c - 3d - 3f - 3d - 1d,2a - 3d - 3f - 3d -'
    r3  = '2a,7c - 3d - 3f# - 3d - 1d,2a - 3d - 3f# - 3d -'


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

    music  = pat2wav(mus, 8000)
    wavfile.write('melody.wav', FS, music)


def main():
    music001()


if __name__ == '__main__':
    main()




