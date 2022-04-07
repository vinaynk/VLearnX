#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt, animation, gridspec


def makeTaylorVecGen(xlim=np.pi*3,
            order=20, numpts=1000, steps=100):
    '''
    func to handle the taylor series expansion
    xlim   : x vector limits will be -xlim and +xlim
    order  : number of power terms (0 to order-1)
    numpts : number of x vector points
    steps  : number of steps in which a new coef is added
    '''
    xvec  = np.linspace(-xlim, xlim, numpts)
    power = np.arange(order).reshape(order, 1)
    xmat  = (xvec ** power).T # kth row is x^k

    coefs = np.empty((order, 1))
    coefs[0] = 1
    prod  = 1
    for n in range(1, order):
        prod *= n
        coefs[n] = prod
    gains  = np.zeros((order, 1))

    def getFrameVecs():
        power = -1
        for cidx in range(1, order, 2):
            power = -power
            for gval in np.linspace(0, 1, steps):
                gains[cidx] = gval * power
                yvec = xmat @ (gains / coefs)
                yield gains, yvec

    numfr = steps * order // 2

    return xvec, gains, numfr, getFrameVecs


def main():
    xvec, gains, numfr, taylorGen = makeTaylorVecGen()
    gidx = np.arange(len(gains))
    # figure
    fig = plt.figure()
    gs  = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
    # top plot
    ax0 = fig.add_subplot(gs[0])
    ax0.set_xlim(xvec[0], xvec[-1])
    ax0.set_ylim(-2, 2)
    ax0.grid()
    ax0.title.set_text('Summation Result')
    xticks = np.arange(xvec[0], xvec[-1], np.pi/2)
    ax0.set_xticks(xticks)
    # bottom plot
    ax1 = fig.add_subplot(gs[1])
    ax1.set_xlim(0, len(gains))
    ax1.set_ylim(-1.2, 1.2)
    ax1.grid()
    ax1.title.set_text(r'$s(n)$ = Scaling for $\frac{x^n}{n!}$')
    # initializing the plot
    yplot, = ax0.plot(xvec, xvec*0)
    gplot, = ax1.plot(gains, 'o', markersize=10)

    # update function for the plot
    def updatePlot(gypair):
        gains, yvec = gypair
        yplot.set_data(xvec, yvec)
        gplot.set_data(gidx, gains)
        return gplot, yplot

    # creating animation
    anim  = animation.FuncAnimation(
                fig, updatePlot, frames=taylorGen,
                interval=25, blit=True, repeat=False,
                save_count=numfr)

    anim.save('sin-wav-taylor.mp4', writer='ffmpeg', fps=30)
    #plt.show()


if __name__ == '__main__':
    main()


