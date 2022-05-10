#!/usr/bin/env python

# source waveforms used:
# https://archive.org/download/SalamanderGrandPianoV3
# file: SalamanderGrandPianoV3_OggVorbis.tar.bz2
# Audio files belong to: Alexander Holm
# Wavforms (input and output) follows license CC BY 3.0
# License of this code: MIT License


# This script generates the missing keys
# (only 4 are provided per octave, others have to be generated)

import os
import subprocess
import shlex

VEL = 6
SRC = 'ogg'
DST = 'piano'


def shell(cmd):
    print('CMD:', cmd)
    subprocess.check_call(shlex.split(cmd.strip()))


def getResKeyRemap():
    keys  = 'C C# D D# E F F# G G# A A# B'.split()
    allowed = 'C D# F# A'.split()
    octmin = 1
    octmax = 7
    okseq  = [ (oc, k) for oc in range(octmin, octmax+1) for k in keys ]
    resmap = {}
    for idx, (oc, k) in enumerate(okseq):
        if k not in allowed:
            continue
        prv = None
        nxt = None
        if idx > 0:
            prv = okseq[idx-1]
        if idx < len(okseq) - 1:
            nxt = okseq[idx+1]
        resmap[(oc, k)] = ((-1, prv), (1, nxt))
    return resmap


def writeMappedTone(base, mapped, shift=0):
    jump = ''
    if shift != 0:
        jump = f'pitch {100*shift:+d}'
    o1, k1 = base
    o2, k2 = mapped
    shell(f'''
           sox {SRC}/{k1}{o1}v{VEL}.ogg
               -r48k -c1
               {DST}/{o2}{k2}.ogg {jump}
           ''')


def processAllKeys(resmap):
    for key, val in resmap.items():
        writeMappedTone(key, key)
        for shift, mapped in val:
            if mapped is None:
                continue
            writeMappedTone(key, mapped, shift)



def resampleWavs():
    resmap = getResKeyRemap()
    processAllKeys(resmap)


def main():
    resampleWavs()


if __name__ == '__main__':
    main()



