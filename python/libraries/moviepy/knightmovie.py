#!/usr/bin/env python

from glob import glob
from moviepy import editor


def combineImagesToMovie(indir, out, dur=0.375, fps=10, lastdur=10):
    files = glob(f'{indir}/*.png')
    files.sort()
    clips = [ editor.ImageClip(img).set_duration(dur)
              for img in files ]
    clips.append(editor.ImageClip(files[-1]).set_duration(lastdur))
    concat = editor.concatenate_videoclips(clips, method="compose")
    audClip = editor.AudioFileClip('bgmusic.ogg')\
                    .set_duration(concat.duration)\
                    .audio_fadeout(5)
    concat = concat.set_audio(audClip)
    concat.write_videofile(out, fps=fps, codec="libx264")


def main():
    combineImagesToMovie('frames/', 'output.mp4')


if __name__ == '__main__':
    main()



