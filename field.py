from __future__ import print_function
from random import choice
from collections import namedtuple, defaultdict
from itertools import permutations
import string

def iterate(iterable):
    num = 0
    for item in iterable:
        yield num, item
        num += 1

def first_true(iterable):
    for item in iterable:
        if item:
            return item
    return None


BBox = namedtuple("BBox", "l, u, r, d")

pos_adder = lambda posx, posy: lambda (x, y): (posx + x, posy + y)

r = pos_adder(1, 0)
d = pos_adder(0, 1)
l = pos_adder(-1, 0)
u = pos_adder(0, -1)

def _field_type(pos, fieldset):
    """ _field_type(position, fieldset)
       => "absorb", "reflect", "rotate", None

    calculate what kinds of action a fieldset can potentially do."""

    same = pos in fieldset
    ud = u(pos) in fieldset and d(pos) in fieldset
    lr = l(pos) in fieldset and r(pos) in fieldset
    uod = u(pos) in fieldset or d(pos) in fieldset
    lor = l(pos) in fieldset or r(pos) in fieldset
    # determine our own type
    if same:
        # line?
        if (ud and not lor) or (lr and not uod):
            # we have a line.
            return "absorb"
        elif ud and lr:
            # we have a fully surrounded fieldset
            return "reflect"
        else:
            # this fieldset is utterly irrelevant
            return None
    else:
        if ud & lr:
            # we have a fully surrounded, but
            # with an emptyness in the middle
            return "rotate"
        else:
            # this fieldset is utterly irrelevant
            return None

def _action_possible(pos, sis, ftype):
    """ _action_possible(position, signals, fieldset)
          => ([(r1x, r1y), ...], [(a1x, a1y), ...])

    determine if this field can do an action and, if it can, return
    a list of tuples (a, b) where a is the signal to replace and b is the
    new signal to set instead."""

    if pos in sis:
        # never operate on the field that a signal is in.
        return None
    elif ftype == None:
        return None

    sig_count = sum([f(pos) in sis for f in [u, d, l, r]])
    signals = [f(pos) for f in [u, d, l, r] if f(pos) in sis]
    reflected = [f(pos) for f, g
                 in [(u, d), (d, u), (l, r), (r, l)]
                 if g(pos) in sis]
    rotated = [f(pos) for f, g
                 in [(u, l), (d, r), (l, d), (r, u)]
                 if g(pos) in sis]

    if ftype == "absorb" and sig_count == 1:
        # remove the found signal and replace it with our current position
        return ([signals[0]], [pos])
    elif ftype == "reflect" and sig_count == 1:
        return ([signals[0]], [reflected[0]])
    elif ftype == "rotate" and sig_count == 2:
        if signals[0] != reflected[0]:
            # the signals must face each other.
            return None
        return ([signals[i] for i in range(2)], [rotated[i] for i in range(2)])

class Field(object):
    fieldset = frozenset()
    fields = defaultdict(lambda: None)
    signals = []
    start_out_signals = []
    labels = {}
    bounds = BBox(0, 0, 1, 1)
    renderers = []
    directions = list(permutations([u, d, l, r]))
    inputs = []

    def __init__(self, data=None, filename=None):
        if filename:
            data = open(filename).read()
        self.read_data(data)

    def __str__(self):
        return "\n".join(field_to_stringlist(self.bounds, self.fieldset, self.signals, self.labels))

    def reset(self, inputs):
        self.inputs = inputs
        signals_to_set = [pos for (label, (lpos, pos, out)) in self.labels.iteritems() if label in inputs]
        for renderer in self.renderers:
            renderer.add_actions(self.signals, self.start_out_signals + signals_to_set)
        self.signals = self.start_out_signals + signals_to_set
        for renderer in self.renderers:
            renderer.reset(inputs)

    def read_data(self, data, offset=(0, 0)):
        xo, yo = offset
        self.field = data.split("\n")

        fieldelems = []

        bound_l, bound_u, bound_r, bound_d = self.bounds

        labels = []
        inside_label = 0

        for py, line in iterate(self.field):
            for px, char in iterate(line):
                if inside_label > 0:
                    inside_label -= 1
                    continue
                x = px + xo
                y = py + yo
                if char == "O":
                    self.signals.append((x, y))
                    char = "#"
                if char == "#":
                    fieldelems.append((x, y))
                    if x < bound_l:
                        bound_l = x
                    elif x > bound_r:
                        bound_r = x
                    if y < bound_u:
                        bound_u = y
                    elif y > bound_d:
                        bound_d = y
                elif char == " ":
                    continue
                elif char in string.lowercase or char in string.uppercase:
                    linerest = line[px:]
                    label = ""
                    out = False
                    for char in linerest:
                        if char in string.lowercase + string.uppercase + string.digits + "'.":
                            label += char
                        else:
                            break
                    inside_label = len(label)
                    if label.endswith("."):
                        label = label[:-1]
                        out = True
                    labels.append(((px, py), label, out))
                    if x + len(label) > bound_r:
                        bound_r = x + len(label)

        self.bounds = BBox(l=bound_l, r=bound_r, u=bound_u, d=bound_d)

        self.fieldset = frozenset(self.fieldset.union(fieldelems))

        for (pos, label, out) in labels:
            # find the nearest piece of wire.
            for direction in [u, l, d]:
                if direction(pos) in self.fieldset:
                    self.labels[label] = (pos, direction(pos), out)
                    break
            npos = r(pos)
            for i in range(len(label)):
                npos = r(npos)
                if npos in self.fieldset:
                    self.labels[label] = (r(pos), npos, out)
                    break

        self.update_fieldtypes()
        self.start_out_signals = self.signals[:]

    def update_fieldtypes(self):
        self.fields = defaultdict(lambda: None)
        for field in self.fieldset:
            self.fields[field] = _field_type(field, self.fieldset)
            
            # also catch empty fields that are surrounded by other fields.
            # we can choose an arbitrary direction for all fields, that we look for
            # empty, surrounded fields in.
            if r(field) not in self.fieldset:
                if _field_type(r(field), self.fieldset) == "rotate":
                    self.fields[r(field)] = "rotate"

    def step(self, steps=1):
        overflow = 0
        while steps > 0 and overflow < 1000:
            direction_order = choice(self.directions)

            signal = choice(self.signals)
            action = first_true(
                _action_possible(f(signal), self.signals, self.fields[f(signal)])
                 for f in direction_order)

            if not action:
                overflow += 1
                continue
            else:
                steps -= 1

            before_count = len(self.signals)

            self.signals = set(self.signals) - frozenset(action[0])
            self.signals = self.signals | frozenset(action[1])
            self.signals = list(self.signals)

            after_count = len(self.signals)

            if after_count != before_count:
                print("\n".join(field_to_stringlist(self.bounds, self.fieldset, self.signals)))
                print()
                print(action)
                raise Exception("this action just changed the number of signals.")


            for renderer in self.renderers:
                renderer.add_actions(*action)

        if steps > 0:
            raise Exception("could not find any actions at all!")

    def attach_renderer(self, renderer):
        self.renderers.append(renderer)
        renderer.update_bounds(self.bounds)
        renderer.update_labels(self.labels)
        renderer.update_field(self.fieldset)
        renderer.add_actions(frozenset(), self.signals)
        renderer.reset(self.inputs)

def field_to_stringlist(bounds, fields, signals, labels={}):
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
        result[y - bounds.u][x - bounds.l] = "#"
    for x, y in signals:
        result[y - bounds.u][x - bounds.l] = "O"
    for (label, (pos, tgt, out)) in labels.iteritems():
        for cp in range(len(label)):
            result[pos[1]][pos[0] + cp] = label[cp]

    return ["".join(a) for a in result]

class RendererBase(object):
    def __init__(self, *args):
        """initialise the renderer with some state"""

    def update_bounds(self, newbounds):
        """update the size of the canvas"""

    def update_labels(self, labels):
        """update the labels"""

    def update_field(self, fieldset):
        """update the set of fields"""

    def add_actions(self, removals, additions):
        """add removals and additions to render in the near future"""

    def is_picture_dirty(self):
        """returns if the image is dirty"""

    def refresh_picture(self):
        """refresh the picture somehow"""

    def reset(self, inputs):
        """the field has been reset

        this will be called after add_action has been called with all old
        and new signal positions."""

if __name__ == "__main__":
    import field_data

    class OutputSignalNotifier(RendererBase):
        activation = lambda: None
        labels = {}
        triggered = []
        inputs = []
        results = []
        def __init__(self):
            self.step = 0
            self.signals = 0

        def reset(self, inputs):
            self.inputs = inputs
            self.step = 0
            self.signals = len(inputs)
            self.update_labels(self.all_labels)

        def update_labels(self, labels):
            self.labels = {}
            for (name, (pos, tgtpos, out)) in labels.iteritems():
                if out:
                    self.labels[tgtpos] = name
            self.all_labels = labels.copy()
            self.triggered = []

        def add_actions(self, removals, additions):
            self.step += 1
            for pos in additions:
                if pos in self.labels:
                    self.triggered.append(self.labels[pos])
                    del self.labels[pos]
                    self.signals -= 1
                    if self.signals == 0:
                        self.results.append((self.step, self.inputs, self.triggered))
                        self.activation()

    testfield = Field(data=field_data.xor_drjoin)
    notifier = OutputSignalNotifier()
    def activation():
        testfield.reset([choice(["a0", "a1"]), choice(["b0", "b1"])])
    notifier.activation = activation
    activation()
    testfield.attach_renderer(notifier)
    try:
        for step in range(1000000):
            testfield.step()
    except KeyboardInterrupt:
        print(testfield)
        raise
    finally:
        times = {}
        rounds = {}
        results = {}
        for (time, inputs, outputs) in notifier.results:
            inputs = tuple(inputs)
            times[inputs] = times.get(inputs, 0) + time * 1.0
            rounds[inputs] = rounds.get(inputs, 0) + 1

        rounds_sum = 0
        for key in times.iterkeys():
            results[key] = times[key] / rounds[key]
            rounds_sum += rounds[key]

        print(results, " - ", rounds_sum, "rounds.")
