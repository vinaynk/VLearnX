#!/usr/bin/env python


class CtxUtilsError(Exception):
    pass


def setColor(ctx, clr):
    if len(clr) == 3:
        ctx.set_source_rgb(*clr)
    elif len(clr) == 4:
        crx.set_source_rgba(*clr)
    else:
        raise CtxUtilsError(f'unknown color {clr}')


def drawLine(ctx, p1, p2):
    ctx.move_to(*p1)
    ctx.line_to(*p2)
    ctx.stroke()


def showText(ctx, p1, text):
    ctx.move_to(*p1)
    ctx.show_text(text)
    ctx.stroke()


def prepareCanvas(ctx,
                  width=200, height=200,
                  bgColor=(0, 0, 0),
                  gridSize=10,
                  gridColor=(.2, .2, .2), gridTextColor=(.4, .4, .4),
                  gridMainInterval=50):
    if bgColor:
        setColor(ctx, bgColor)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
    if gridSize <= 0 or gridColor is None:
        return
    # drawing vertical lines
    setColor(ctx, gridColor)
    textList = []
    left = 0
    while left < width:
        lw = 1 if left % gridMainInterval == 0 else 0.3
        ctx.set_line_width(lw)
        drawLine(ctx, [left, 0], [left, height])
        if left % gridMainInterval == 0:
            textList.append(((left+2, 10), str(left)))
        left += gridSize
    top = 0
    while top < height:
        lw = 1 if top % gridMainInterval == 0 else 0.3
        ctx.set_line_width(lw)
        drawLine(ctx, [0, top], [width, top])
        if top % gridMainInterval == 0:
            textList.append(((2, top+10), str(top)))
        top += gridSize
    if gridTextColor is None:
        return
    setColor(ctx, gridTextColor)
    for pos, text in textList:
        showText(ctx, pos, text)





