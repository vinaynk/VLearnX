#!/usr/bin/env python

import json


def _createJumpNextSteps():
    'all possible moves for the knight'
    li = [ (1, 2), (2, 1) ]
    # flip wrt to x axis
    li = li + [ (el[0], -el[1]) for el in li ]
    # flip wrt to y axis
    li = li + [ (-el[0], el[1]) for el in li ]
    return li


_jumpNextSteps = _createJumpNextSteps()


def possibleJumps(vec, size):
    'all possible jumps from position vec'
    ret = []
    for jump in _jumpNextSteps:
        vec1 = (vec[0] + jump[0], vec[1] + jump[1])
        if 0 <= vec1[0] < size and \
           0 <= vec1[1] < size:
            ret.append(vec1)
    return ret


class SearchEnvFullBoard:

    def __init__(self, size, flog=None):
        self.size  = size
        # to mark locations reached
        self.marks = [ 0 for ii in range(size * size) ]
        self.path  = []
        self.flog  = flog
        self.found = False
        self.maxsize = 0
        self.njumps  = 0

    def isMarked(self, vec):
        i, j = vec
        return self.marks[i * self.size + j] > 0

    def push(self, vec):
        i, j = vec
        self.path.append(vec)
        self.marks[i * self.size + j] += 1
        if  len(self.path) > self.maxsize:
            self.maxsize = len(self.path)
            # print(self.maxsize)
        self.log()
        self.njumps += 1

    def pop(self):
        last = self.path.pop()
        i, j = last
        self.marks[i * self.size + j] -= 1
        self.log()

    def log(self, collision=None):
        if not self.flog:
            return
        path = self.path.copy()
        if collision:
            path.append(collision)
        print(json.dumps(path), file=self.flog)

    def remaning(self):
        return self.size * self.size - len(self.path)


def prioritizeCloser(point, jumps):
    'puts jumps closer to point first'
    dist = lambda p, q: ((p[0]-q[0])**2 + (p[1]-q[1])**2) ** 0.5
    distvecs = [ (dist(point, jump), jump) for jump in jumps ]
    distvecs.sort(key = lambda el:el[0])
    jumps = [ el[1] for el in distvecs ]
    return jumps


def testPrioritizeCloser():
    point1 = (3, 4)
    jumps  = possibleJumps(point1, 8)
    print(jumps)
    jumps  = prioritizeCloser((7, 0), jumps)
    print(jumps)


def warnsdorff(jumps, env):
    'order jumps based on the number of second order possibilities'
    ctposs = []
    for jump in jumps:
        possibile = possibleJumps(jump, env.size)
        count = 0
        for kumq in possibile:
            if not env.isMarked(kumq):
                count += 1
        ctposs.append((count, jump))
    ctposs.sort()
    return [ el[1] for el in ctposs ]


def knightWalk(vec, env):
    env.push(vec)
    if env.remaning() == 0:
        env.found = True
        return
    jumps = possibleJumps(vec, env.size)
    jumps = warnsdorff(jumps, env)
    for jump in jumps:
        if env.found:
            break
        if env.isMarked(jump):
            env.log(jump)
            continue
        knightWalk(jump, env)
    if not env.found:
        env.pop()


def runFromStart(start, size, log=False):
    flog  = None
    if log:
        flog  = open('knight_moves.txt', 'w')
    env   = SearchEnvFullBoard(size, flog)
    print('Start: ', start)
    knightWalk(start, env)
    if log:
        flog.close()
    print('Total jumps:', env.njumps)
    print('Path:', env.path)
    print(flush=True)


def runForAll():
    size  = 8
    for ii in range(size):
        for jj in range(size):
            runFromStart((ii, jj), size)


def testFunctions():
    candi = [ (0, 0), (2, 4), (5, 7), (6, 6) ]
    for pos in candi:
        possible = possibleJumps(pos, 8)
        print(pos, possible)


def main():
    #testFunctions()
    #runForAll()
    runFromStart((2, 2), 8)


if __name__ == '__main__':
    main()


