from random import choice

def iterate(iterable):
    num = 0
    for item in iterable:
        yield num, item

pos_adder = lambda posx, posy: lambda (x, y): (posx + x, posy + y)

r = pos_adder(1, 0)
d = pos_adder(0, 1)
l = pos_adder(-1, 0)
u = pos_adder(0, -1)

def action_possible(pos, sis, fs):
    """ action_possible(position, signals, fieldset)
          => ([(r1x, r1y), ...], [(a1x, a1y), ...])

    determine if this field can do an action and, if it can, return
    a list of tuples (a, b) where a is the signal to replace and b is the
    new signal to set instead."""
    absorb = False
    reflect = False
    rotate = False

    same = pos in fs
    ud = u(pos) in fs and d(pos) in fs
    lr = l(pos) in fs and r(pos) in fs
    # determine our own type
    if pos in fs:
        # line?
        if ud ^ lr:
            # we have a line.
            absorb = True
        elif ud and lr:
            # we have a fully surrounded field
            reflect = True
        else:
            # this field is utterly irrelevant
            return False
    else:
        if ud & lr:
            # we have a fully surrounded, but
            # with an emptyness in the middle
            rotate = True
        else:
            # this field is utterly irrelevant
            return False

    signum = sum([f(pos) in sis for f in [u, d, l, r]])
    signals = [f(pos) for f in [u, d, l, r] if f(pos) in sis]
    reflected = [f(pos) for f, g
                 in [(u, d), (d, u), (l, r), (r, l)]
                 if g(pos) in sis]

    if absorb and signum == 1:
        # remove the found signal and replace it with our current position
        return [(signals[0], pos)]
    elif reflect and signum == 1:
        return [(signals[0], reflected[0])]
    elif rotate and signum == 2:
        return ([signals[i] for i in range(2)], [reflected[i] for i in range(2)])

class Field(object):
    fieldset = frozenset()
    signals = []
    def __init__(self, data=None, filename=None):
        if filename:
            data = open(filename).read()
        self.field = data.split("\n")

        fieldelems = []

        for y, line in iterate(self.field):
            for x, char in iterate(line):
                if char == "O":
                    self.signals |= (x, y)
                    char = "_"
                if char == "_":
                    fieldelems.append(x, y)

        self.fieldset = frozenset(fieldelems)
        
    def step(self, steps=1):
        for step in range(steps):
            signal = choice(self.signals)
            possibilities = sum(
                [action_possible(f(signal), self.signals, self.fieldset)
                 for f in [u, d, l, r]], [])

            action = choice(possibilities)

            self.signals -= frozenset(action[0])
            self.signals += frozenset(action[1])
