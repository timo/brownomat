from field import RendererBase
from random import sample
from string import letters
from os import mkdir, path

block = r"""    \filldraw[%(filltype)s=%(fill)s, draw=%(draw)s] (%(x1)d, %(y1)d) rectangle (%(x2)d, %(y2)d);"""
def makeblock((x, y), fill="gray", draw="black", pattern=False):
    return block % dict(fill=fill,
            draw=draw,
            filltype="pattern" if pattern else "fill",
            x1 = x,
            y1 = y,
            x2 = x + 1,
            y2 = y + 1) + "\n"

class TikzRenderer(RendererBase):
    def __init__(self, name=None):
        self.frameno = 0
        self.name = name or "".join(sample(letters, 6))
        mkdir(self.name)
        self.collection_file = open(self.name + ".tex", "w")

        self._init_frame()

        self.field = set()
        self.labels = []
        self.signals = set()
        self.dirty = False

    def _next_frame(self):
        self._close_frame()
        self.frameno += 1
        self._init_frame()

    def _init_frame(self):
        self.frame = open(path.join(self.name, "%03d.tex" % self.frameno), "w")
        self.collection_file.write(r"\input{%s/%03d.tex}" % (self.name, self.frameno) + "\n")

        self.frame.write(r"""\begin{figure}[h]
  \centering
  \begin{tikzpicture}[scale=0.3]""")

    def _close_frame(self):
        self.frame.write(r"""  \end{tikzpicture}
\end{figure}""")
        self.frame.close()

    def update_field(self, fieldset):
        self.field = fieldset
        self.dirty = True

    def add_actions(self, removals, additions):
        if self.dirty:
            self._render_out()
        self.signals = self.signals.difference(removals).union(additions)
        self.dirty = True

    def is_picture_dirty(self):
        return self.dirty

    def _render_out(self):
        for field in self.field:
            self.frame.write(makeblock(field, fill="black" if field in self.signals else "gray"))

        self._next_frame()
        self.dirty = False

    def __del__(self):
        self._close_frame()
        self.collection_file.close()
