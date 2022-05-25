
import math
import numpy as np
import cairo
import ctxutils as ut
import json
from colorsys import hls_to_rgb

PI  = math.pi

def H2R(clr):
    return hls_to_rgb(*clr)


class ChessBoardDrawer:

    def __init__(self, size, rows=8):
        self.size    = size
        self.boxsize = size / rows
        self.colors  = [ (0.26, 0.23, 0.20), (0.10, 0.12, 0.14) ]
        self.rows    = rows
        self.cols    = rows
        self.marked  = set()

    def _drawRow(self, ctx, row):
        top = row * self.boxsize
        for col in range(self.cols):
            left   = col * self.boxsize
            clridx = (row + col) % 2
            clr = self.colors[clridx]
            ctx.set_source_rgb(*clr)
            ctx.rectangle(left, top, self.boxsize, self.boxsize)
            ctx.fill()

    def draw(self, ctx):
        ctx.save()
        for row in range(self.rows):
            self._drawRow(ctx, row)
        ctx.restore()

    def getCenter(self, box):
        left, top = box
        left = (left+0.5) * self.boxsize
        top  = (top+0.5)  * self.boxsize
        return left, top

    def collision(self, ctx, left, top):
        rad = 15
        ctx.move_to(left+rad, top+0)
        steps = 16
        for ii in range(steps):
            r = rad + (ii % 2) * 40
            x = r * np.cos(2 * PI / steps * ii)
            y = r * np.sin(2 * PI / steps * ii)
            ctx.line_to(left+x, top+y)
        ctx.close_path()


    def markBox(self, ctx, point, clr, idx):
        point = tuple(point)
        marked = point in self.marked
        left, top = point
        left, top = self.getCenter(point)
        if marked:
            ctx.set_source_rgb(*H2R((0, 0.5, 1)))
            self.collision(ctx, left, top)
        else:
            ctx.set_source_rgb(*H2R(clr))
            ctx.arc(left, top, self.boxsize/5, 0, 2*PI)
        ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        ctx.move_to(left-13, top+7)
        ctx.show_text(f'{idx:02d}')
        ctx.fill()
        self.marked.add(point)


    def drawLine(self, ctx, p1, p2, clr):
        ctx.set_source_rgb(*H2R(clr))
        ctx.set_line_width(2)
        ctx.move_to(*self.getCenter(p1))
        ctx.line_to(*self.getCenter(p2))
        ctx.stroke()


    def drawPath(self, ctx, points):
        ctx.save()
        ctx.set_font_size(20)
        hue = 0
        uphue = lambda h : h + 0.157777
        for idx, point in enumerate(points):
            if idx != 0:
                self.drawLine(ctx, points[idx-1], point, clr)
            clr = (hue, 0.5, 0.4)
            hue = uphue(hue)
        hue = 0
        for idx, point in enumerate(points):
            clr  = (hue, 0.5, 0.5)
            hue = uphue(hue)
            self.markBox(ctx, point, clr, idx)
            prev = point, clr
        ctx.restore()


def prepCtx(ctx):
    ctx.set_source_rgb(0.0, 0.05, 0.07)
    ctx.rectangle(0, 0, 1920, 1080)
    ctx.fill()
    ctx.translate(420, 0)


def drawPath(idx, path):
    size = 1080
    rows = 8
    #surface = cairo.SVGSurface(f'frames/knight-{idx:08d}.svg', size, size)
    #surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, size)
    ctx  = cairo.Context (surface)
    prepCtx(ctx)
    brd  = ChessBoardDrawer(size, rows)
    brd.draw(ctx)
    brd.drawPath(ctx, path)
    surface.write_to_png(f'frames/knight-{idx:08d}.png')
    surface.finish()


def testChessBoard():
    fi   = open('knight_moves.txt')
    for idx, line in enumerate(fi):
        path = json.loads(line)
        drawPath(idx, path)
        print('Completed:', idx, flush=True)


def drawPathProg():
    with open('path.json') as fi:
        path = json.load(fi)
    for pl in range(1, len(path)+1):
        drawPath(pl, path[:pl])
        print('Completed:', pl, flush=True)


def main():
    # testChessBoard()
    drawPathProg()


if __name__ == '__main__':
    main()



