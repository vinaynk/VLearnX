import cairo
import math
import numpy as np
import ctxutils as ut

PI = math.pi
np.random.seed(10)


def drawCircle(ctx, pos, r, lw=None, clr=None):
    ctx.arc(pos[0], pos[1], r, 0, 2*PI)
    ctx.stroke()


def drawHelicalCurves(ctx, mid):
    radius = 300
    amp    = 50
    ncyc   = 8
    nwav   = 2
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for idx in range(nwav):
        for theta in np.linspace(0, 2*PI, 1000):
            rad = math.sin(theta * ncyc + idx * 2 * PI / nwav) * amp + radius
            x   = rad * math.cos(theta) + mid[0]
            y   = rad * math.sin(theta) + mid[1]
            if theta == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.stroke()


def drawVX(ctx):
    ctx.set_line_width(20)
    ctx.move_to(250, 250)
    ctx.line_to(550, 550)
    ctx.stroke()
    ctx.move_to(250, 550)
    ctx.line_to(550, 250)
    ctx.stroke()
    ctx.set_line_width(40)
    ctx.move_to(200, 350)
    ctx.line_to(400, 550)
    ctx.line_to(600, 350)
    ctx.stroke()


def drawIcon():
    clr1 = (0.1, 0.6, 0.9)
    width, height  = 800, 800
    surface = cairo.SVGSurface ('yticon.svg', width, height)
    ctx = cairo.Context (surface)
    ut.prepareCanvas(ctx, width, height, gridSize=-1)
    ut.setColor(ctx, clr1)
    ctx.set_line_width(20)

    drawHelicalCurves(ctx, [width//2, height//2])
    drawVX(ctx)

    surface.finish()


def plotxy(ctx, x, y, lim=500):
    ctx.move_to(x[0], y[0])
    for ii in range(1, len(x)):
        if abs(y[ii]) > lim:
            continue
        ctx.line_to(x[ii], y[ii])
    ctx.stroke()

rndi = np.random.randint
runi = np.random.uniform
rand = np.random.rand


def plotFourier(ctx):
    ctx.save()
    ctx.translate(200, 550)
    xl = 600
    x  = np.arange(0, xl, 2)
    comb = 0
    for f in range(1, 9, 2):
        y = np.sin(4.0 * PI * f / xl * x)
        comb += y * (1/f)
        ut.setColor(ctx, (rand(), rand(), 0.9))
        plotxy(ctx, x, comb * 100)
    ctx.restore()


def plotCentralLimitTheorem(ctx):
    yl = 101
    y = np.zeros(yl)
    y[46:49] = 1
    y[51:54] = 1.5
    y = y / y.max()
    x = np.arange(yl)
    ctx.save()
    ctx.translate(800, 550)
    rand()
    for ii in range(6):
        ut.setColor(ctx, (rand(), rand(), 0.9))
        plotxy(ctx, x*5, -y * 100)
        y = np.convolve(y, y)
        y = y / y.max()
        y = y[yl//2:yl//2+yl]

    ctx.restore()


def powerSeries(ctx):
    x = np.linspace(0, 2*PI)
    c = 1
    sign = 1
    comb = 0
    ctx.translate(1250, 600)
    rand()
    for p in range(1, 20):
        c *= p
        if p % 2 == 1:
            y = sign / c * (x ** p)
            sign = -sign
            comb += y
            clr = p / 20
            ut.setColor(ctx, (clr, rand(), rand()))
            plotxy(ctx, x*100, -comb*100)
    plotxy(ctx, x*100, comb*0)


def drawBanner():
    width, height  = 2048, 1152
    surface = cairo.SVGSurface ('ytbanner.svg', width, height)
    ctx = cairo.Context (surface)
    ut.prepareCanvas(ctx, width, height, bgColor=(0.05, 0.05, 0.05), gridSize=20, 
                     gridTextColor=None)
    ctx.set_line_width(3)
    plotFourier(ctx)
    plotCentralLimitTheorem(ctx)
    powerSeries(ctx)
    surface.finish()




def main():
    #drawIcon()
    drawBanner()


if __name__ == '__main__':
    main()


