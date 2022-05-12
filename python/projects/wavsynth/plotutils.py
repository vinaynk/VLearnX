

import numpy as np
from matplotlib import pyplot as plt

plt.style.use('dark_background')


def highlightRegions(ax):
    points = [ (-1, 0), (-0.5, 0.15), (0, 0.01), (15, 0.01),
               (16, 0.99), (0, 0.99) ]
    arr = np.array(points)
    x, y = arr[:, 0], arr[:, 1]
    for ii in range(4):
        ax.fill(x, y+ii, alpha=0.2)


def norm01(vec):
    'normalize vec between 0 and 1'
    vec -= vec.min()
    vec /= vec.max()
    return vec


def plotMelodyGen(step, k, h, c):
    kvec = np.int32(c)
    incli = np.linspace(0, 1, len(h))
    c1    = c
    c     = norm01(c1 + incli)
    if 6 <= step : c *= (len(k) - 0.01)
    #fontsize = 55
    fontsize = 20
    if step > 8:
        fontsize=60
    keys = ' '.join(k)
    xx   = np.arange(len(h))
    active = xx[h==1]
    fig = plt.figure(figsize=(16,9))
    fig.tight_layout()
    ax  = fig.add_subplot(111)
    ax.grid(True, color='#666')
    if 0 <= step <= 2: ax.plot(c1, '-o', color='#0ff', linewidth=1, markersize=1)
    if 1 <= step <= 2: ax.plot(incli, '--', color='#a0a', linewidth=2)
    if 2 <= step : ax.plot(c, '-o', color='#44f', linewidth=5, markersize=10)
    if 4 <= step : ax.plot(active, active*0, 'o', color='#fa0', markersize=10)
    if 5 <= step : ax.plot(active, c[active], 'o', color='#f44', markersize=20)
    #-- #ax.plot(active, kvec[active], 'o', color='#0a0', markersize=10)
    if step >= 0 : ax.set_xticks(xx)
    if 6 <= step :
        ax.set_yticks(np.arange(len(k)+1))
        ax.set_yticklabels(k+['--'], fontsize=fontsize, color='#aaa')
    if 8 < step:
        #ax.set_xlabel('Time steps', fontsize=fontsize)
        #ax.xaxis.label.set_color('#aaa')
        ax.set_title(f'Melody generation', fontsize=fontsize)
        ax.yaxis.label.set_color('#aaa')
        ax.title.set_color('#aaa')
    if 0 <= step:
        ax.set_xlim(-1, 16)
        ax.set_xticklabels(np.arange(16), fontsize=20, color='#aaa')
    if 7 <= step:
        highlightRegions(ax)
    def legend(at, li):
        if at == step: ax.legend(li, fontsize=15, loc='upper left')
    legend(0, ['Normalized noise', 'Inclination'])
    legend(1, ['Normalized noise', 'Inclination'])
    legend(2, ['Normalized noise', 'Inclination', 'After inclination'])
    legend(3, ['Inclined noise'])
    legend(4, ['Inclined noise', 'Hit points'])
    legend(5, ['Inclined noise', 'Hit points', 'Key selector'])
    legend(6, ['Inclined noise', 'Hit points', 'Key selector'])
    legend(7, ['Inclined noise', 'Hit points', 'Key selector'])
    legend(8, ['Inclined, smoothed noise', 'Hit points', 'Key selector'])
    legend(9, ['Inclined, smoothed noise', 'Hit points', 'Key selector'])
    for spine in ax.spines.values():
        spine.set_edgecolor('#666')
    fig.savefig(f'step-{step}.png')
    #plt.show()


if __name__ == '__main__':
    main()



