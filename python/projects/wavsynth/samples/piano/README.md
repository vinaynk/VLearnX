
# Source

source waveforms used:
https://archive.org/download/SalamanderGrandPianoV3

file: SalamanderGrandPianoV3_OggVorbis.tar.bz2

Audio files belong to: Alexander Holm

Wavforms (input and output) follows license CC BY 3.0

This script generates the missing keys
(only 4 are provided per octave, others have to be generated)

command to use:

```
sox key.ogg -r48k -c1 key_next.ogg pitch +100
```

Sox pitch processing shifts waveform 1 semi-tone for 100 (-100 to go down).

