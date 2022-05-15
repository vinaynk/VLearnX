#!/usr/bin/env python

from moviepy import editor


def imgAudio2Video(imgfile, audfile, outfile):
    audClip = editor.AudioFileClip(audfile)
    dur = audClip.duration
    imgClip = editor.ImageClip(imgfile, duration=dur)
    imgClip = imgClip.set_audio(audClip)
    imgClip.write_videofile(outfile, fps=30, codec="libx264", audio_codec='aac')


def main():
    imgAudio2Video('saved/piano.jpg', 'saved/melody-002.ogg',
                   'saved/melody-002.mp4')


if __name__ == '__main__':
    main()


