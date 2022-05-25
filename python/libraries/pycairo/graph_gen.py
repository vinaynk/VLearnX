#!/usr/bin/env python

import math
import numpy as np
import cairo
import ctxutils as ut
import json
from colorsys import hls_to_rgb

from types import SimpleNamespace as Obj


PI  = math.pi


def H2R(clr):
    return hls_to_rgb(*clr)


class State:

    def __init__(self, state, children, depth):
        self.state = state
        self.depth = depth
        self.children = children
        self.pos   = (0, 0)
        self.mark  = 0

    def __repr__(self):
        space = '  ' * self.depth
        return f'\n{space}{self.state} {self.pos} -> {self.children}'


def _getChildren(env):
    if env.depth >= env.depthlim:
        return []
    ret = []
    lim = env.prob ** (env.depth - 1)
    states = []
    maxch = 3
    if env.depth == 1:
        maxch = 1
    for ii in range(maxch):
        stateid = env.counter
        env.counter += 1
        states.append(stateid)
        if np.random.rand() > lim:
            break
    # print(f'{states=} {env.depth=}')
    for stateid in states:
        children = getChildren(env)
        ret.append(State(stateid, children, env.depth))
    return ret


def getChildren(env):
    env.depth += 1
    ret = _getChildren(env)
    env.depth -= 1
    return ret


def createGraph(depthlim=5):
    env = Obj()
    env.counter = 0
    env.depth = 0
    env.depthlim = depthlim
    env.prob = 0.7
    graph = getChildren(env)[0]
    return graph


def assignPos(env, state, pos):
    shiftx = 300
    shifty = 130
    depthlim = 5
    state.pos = pos
    x, y = pos
    chx = x + shiftx
    for idx, ch in enumerate(state.children):
        env.deptop[ch.depth] += shifty
        chpos = (chx, env.deptop[ch.depth])
        assignPos(env, ch, chpos)


def prepCtx(ctx):
    ctx.set_source_rgb(0.0, 0.05, 0.07)
    ctx.rectangle(0, 0, 1920, 1080)
    ctx.fill()


def drawState(env, state):
    clrx = [ (0.9, 0.9, 0.9), (1, 0.6, 0.2), (0.4, 0.4, 0.4)]
    ctx  = env.ctx
    x, y = state.pos
    for ch in state.children:
        clr  = clrx[ch.mark]
        ctx.set_source_rgb(*clr)
        ctx.move_to(x, y)
        ctx.line_to(ch.pos[0], ch.pos[1])
        ctx.stroke()
        drawState(env, ch)
    clr  = clrx[state.mark]
    ctx.set_source_rgb(*clr)
    ctx.arc(x, y, 45, 0, 2*PI)
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(x-19, y+12)
    ctx.show_text(f'{state.state:02d}')
    ctx.fill()


def saveImage(env):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, env.width, env.height)
    ctx = cairo.Context(surface)
    ctx.set_font_size(30)
    prepCtx(ctx)
    env.ctx = ctx 
    drawState(env, env.head)
    surface.write_to_png(f'frames/frame{env.idx:02d}.png')
    surface.finish()
    env.idx += 1


def bfs(env, state, st):
    state.mark = 1
    saveImage(env)
    if state.state == st:
        return True
    found = False
    for ch in state.children:
        found = bfs(env, ch, st)
        if found:
            break
    if not found:
        state.mark = 2
    return found


def drawGraph(graph):
    env = Obj()
    env.idx    = 0
    env.head   = graph
    env.width  = 1920
    env.height = 1080
    env.deptop = [0] * 10
    assignPos(env, graph, (400, 130))
    bfs(env, graph, 11)
    #drawState(env, graph)
    #surface.write_to_png(f'graph.png')
    #surface.finish()

    #print(graph)


def main():
    #seed = np.random.randint(0, 1000000)
    #seed = 599983
    seed = 117
    print('seed', seed)
    np.random.seed(seed)
    graph = createGraph()
    #print(graph)
    drawGraph(graph)


if __name__ == '__main__':
    main()




