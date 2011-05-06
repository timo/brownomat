from random import choice
from collections import namedtuple

def iterate(iterable):
    num = 0
    for item in iterable:
        yield num, item
        num += 1

BBox = namedtuple("BBox", "l, u, r, d")

pos_adder = lambda posx, posy: lambda (x, y): (posx + x, posy + y)

r = pos_adder(1, 0)
d = pos_adder(0, 1)
l = pos_adder(-1, 0)
u = pos_adder(0, -1)

def _action_possible(pos, sis, fs):
    """ _action_possible(position, signals, fieldset)
          => ([(r1x, r1y), ...], [(a1x, a1y), ...])

    determine if this field can do an action and, if it can, return
    a list of tuples (a, b) where a is the signal to replace and b is the
    new signal to set instead."""
    absorb = False
    reflect = False
    rotate = False
    
    if pos in sis:
        # never operate on the field that a signal is in.
        return None

    same = pos in fs
    ud = u(pos) in fs and d(pos) in fs
    lr = l(pos) in fs and r(pos) in fs
    uod = u(pos) in fs or d(pos) in fs
    lor = l(pos) in fs or r(pos) in fs
    # determine our own type
    if same:
        # line?
        if (ud and not lor) or (lr and not uod):
            # we have a line.
            absorb = True
        elif ud and lr:
            # we have a fully surrounded field
            reflect = True
        else:
            # this field is utterly irrelevant
            return None
    else:
        if ud & lr:
            # we have a fully surrounded, but
            # with an emptyness in the middle
            rotate = True
        else:
            # this field is utterly irrelevant
            return None

    signum = sum([f(pos) in sis for f in [u, d, l, r]])
    signals = [f(pos) for f in [u, d, l, r] if f(pos) in sis]
    reflected = [f(pos) for f, g
                 in [(u, d), (d, u), (l, r), (r, l)]
                 if g(pos) in sis]
    rotated = [f(pos) for f, g
                 in [(u, l), (d, r), (l, d), (r, u)]
                 if g(pos) in sis]

    if absorb and signum == 1:
        # remove the found signal and replace it with our current position
        return ([signals[0]], [pos])
    elif reflect and signum == 1:
        return ([signals[0]], [reflected[0]])
    elif rotate and signum == 2:
        if signals[0] != reflected[0]:
            # the signals must face each other.
            return None
        return ([signals[i] for i in range(2)], [rotated[i] for i in range(2)])

class Field(object):
    fieldset = frozenset()
    signals = []
    bounds = BBox(0, 0, 1, 1)
    renderers = []
    def __init__(self, data=None, filename=None):
        if filename:
            data = open(filename).read()
        self.read_data(data)

    def read_data(self, data, offset=(0, 0)):
        xo, yo = offset
        self.field = data.split("\n")

        fieldelems = []

        l, u, r, d = self.bounds

        for py, line in iterate(self.field):
            for px, char in iterate(line):
                x = px + xo
                y = py + yo
                if char == "O":
                    self.signals.append((x, y))
                    char = "#"
                if char == "#":
                    fieldelems.append((x, y))
                    if x < l:
                        l = x
                    elif x > r:
                        r = x
                    if y < u:
                        u = y
                    elif y > d:
                        d = y

        self.bounds = BBox(l=l, r=r, u=u, d=d)

        self.fieldset = frozenset(self.fieldset.union(fieldelems))


    def step(self, steps=1):
        #print "\n".join(field_to_stringlist(self.bounds, self.fieldset, self.signals))
        #print
        #print
        overflow = 0
        while steps > 0 and overflow < 1000:
            signal = choice(self.signals)
            possibilities = sum(
                [[_action_possible(f(signal), self.signals, self.fieldset)]
                 for f in [u, d, l, r]], [])
            possibilities = [p for p in possibilities if p]

            if len(possibilities) == 0:
                overflow += 1
                continue
            else:
                steps -= 1
            action = choice(possibilities)
            
            before_count = len(self.signals)

            self.signals = set(self.signals) - frozenset(action[0])
            self.signals = self.signals | frozenset(action[1])
            self.signals = list(self.signals)
            
            after_count = len(self.signals)

            if after_count != before_count:
                print "\n".join(field_to_stringlist(self.bounds, self.fieldset, self.signals))
                print
                print action
                raise Exception("this action just changed the number of signals.")


            action = action[:2]
            for renderer in self.renderers:
                renderer.add_actions(*action)

        if steps > 0:
            raise Exception("could not find any actions at all!")

    def attach_renderer(self, renderer):
        self.renderers.append(renderer)
        renderer.update_bounds(self.bounds)
        renderer.update_field(self.fieldset)
        renderer.add_actions(frozenset(), self.signals)

def field_to_stringlist(bounds, fields, signals):
    #fields_list = list(fields)
    # sort by x, then by y
    # so we will have fields grouped into rows, sorted by x value
    """fields_list.sort(key=lambda f: f[0])
    fields_list.sort(key=lambda f: f[1])

    signals_list = list(signals)
    signals_list.sort(key=lambda s: s[0])
    signals_list.sort(key=lambda s: s[1])"""

    result = [[" " for x in range(bounds.r - bounds.l + 1)] for y in range(bounds.d - bounds.u + 1)]

    # most naive implementation i can come up with right now.
    """chars = []
    for x in range(0, bounds.r - bounds.l):
        for y in range(0, bounds.d - bounds.u):
            if (x - bounds.l, y - bounds.u) in fields:
                if (x - bounds.l, y - bounds.u) in signals:
                    chars.append("O")
                else:
                    chars.append("_")
            else:
                chars.append(" ")
        chars.append("\n")

    return "".join(chars)"""

    # even more naive.
    for x, y in fields:
        result[y - bounds.u][x - bounds.l] = "_"
    for x, y in signals:
        result[y - bounds.u][x - bounds.l] = "O"
    
    return ["".join(a) for a in result]

class RendererBase(object):
    def __init__(self, *args):
        """initialise the renderer with some state"""

    def update_bounds(self, newbounds):
        """update the size of the canvas"""

    def update_field(self, fieldset):
        """update the set of fields"""

    def add_actions(self, removals, additions):
        """add removals and additions to render in the near future"""

    def is_picture_dirty(self):
        """returns if the image is dirty"""

    def refresh_picture(self):
        """refresh the picture somehow"""
