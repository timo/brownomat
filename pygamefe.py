#!/usr/bin/env python
from __future__ import print_function
import pygame
import field
from time import sleep
import field_data
from random import choice

pxs = 10

class PyGameSurfaceRenderer(field.RendererBase):
    bgcol = pygame.Color("white")
    fieldcol = pygame.Color("gray")
    signalcol = pygame.Color("black")
    fontcol = pygame.Color("black")
    incol = pygame.Color("red")
    outcol = pygame.Color("blue")

    def __adjust(self, (x, y)):
        return (x - self.bounds.l * pxs, y - self.bounds.u * pxs)

    def __block_to_rect(self, (x, y)):
        return pygame.Rect(*self.__adjust((x * pxs, y * pxs)) + (pxs, pxs))

    def __block_border(self, (x, y), xdiff, ydiff):
        return pygame.Rect(
                x * pxs + (pxs * 0.8 if xdiff > 0 else 0),
                y * pxs + (pxs * 0.8 if ydiff > 0 else 0),
                pxs * (0.2 if xdiff != 0 else 1),
                pxs * (0.2 if ydiff != 0 else 1))

    def __init__(self, parent_surface=None, offset=None):
        self.font = pygame.font.SysFont("bitstreamverasans", pxs)
        self.update_bounds(field.BBox(0, 0, 20, 20))
        self.signals = set()
        self.removals = set()
        self.additions = set()
        self.nice_redraw = False
        self.background_redraw = True
        self.update_labels({})
        self.update_field(frozenset())

        if parent_surface:
            self.surface_factory = lambda rect: parent_surface.subsurface(offset + rect)
        else:
            self.surface_factory = lambda rect: pygame.Surface(rect)

    def update_bounds(self, bounds):
        self.bounds = bounds
        self.background_redraw = True

    def update_field(self, fieldset):
        self.field = fieldset
        self.background_redraw = True

    def update_labels(self, labels):
        self.labels = labels.copy()
        self.background_redraw = True

    def __redraw_background(self):
        rect = ((self.bounds.r - self.bounds.l)*pxs + pxs,
                (self.bounds.d - self.bounds.u)*pxs + pxs)
        self.bgsurf = pygame.Surface(rect)
        self.bgsurf.fill(self.bgcol)

        for field in self.field:
            self.bgsurf.fill(self.fieldcol,
                    self.__block_to_rect(field))

        for (label, (pos, tgtpos, out)) in self.labels.iteritems():
            fontsurf = self.font.render(label, True, self.fontcol)
            self.bgsurf.blit(fontsurf, (pos[0] * pxs, pos[1] * pxs))
            xdiff = pos[0] - tgtpos[0]
            ydiff = pos[1] - tgtpos[1]
            dr = self.__block_border(tgtpos, xdiff, ydiff)
            self.bgsurf.fill(self.outcol if out else self.incol, dr)

        self.resultsurf = self.surface_factory(rect)
        self.resultsurf.blit(self.bgsurf, (0, 0))

        self.background_redraw = False
        self.nice_redraw = True

    def add_actions(self, removals, additions):
        #if len(set(removals) & self.additions) > 0:
        self.nice_redraw = True

        self.removals = self.removals.difference(additions)
        self.additions = self.additions.difference(removals)
        self.additions = self.additions.union(additions)
        self.removals = self.removals.union(removals)

    def is_picture_dirty(self):
        return self.nice_redraw or self.background_redraw

    def refresh_picture(self):
        if self.background_redraw:
            self.__redraw_background()
        for x, y in self.removals:
            rect = pygame.Rect(*self.__adjust((x * 10, y * 10)) + (10, 10))
            self.resultsurf.blit(self.bgsurf, rect, rect)

        self.removals = set()

        for x, y in self.additions:
            self.resultsurf.fill(self.signalcol,
                    pygame.Rect(*self.__adjust((x * 10, y * 10)) + (10, 10)))

        self.additions = set()
        self.nice_redraw = False

class PyGameInteractionPolicy(field.MovementPolicyBase):
    choices = []
    choice = None

    delegate = True

    def __init__(self):
        self._proxy = field.MovementPolicyBase()

    def set_possibilities(self, possibilities):
        l = list(possibilities)
        self.choices = l
        self._proxy.set_possibilities(iter(l))

    def get_choice(self):
        if self.delegate:
            return self._proxy.get_choice()
        return self.choice

    def reset(self):
        self._proxy.reset()
        self.choices = []
        self.choice = None

class PyGameFrontend(object):
    canvas_offset = (20, 20)
    def __init__(self):
        pygame.init()
        self.interactor = PyGameInteractionPolicy()
        self.screen = pygame.display.set_mode((800, 600))
        self.setup_field()

    def setup_field(self):
        self.field = field.Field(data=field_data.xor_drjoin, policy=self.interactor)
        self.renderer = PyGameSurfaceRenderer(self.screen, self.canvas_offset)
        self.field.attach_renderer(self.renderer)
        self.reset_inputs()

    def reset_inputs(self):
        self.field.reset([choice(["a0", "a1"]), choice(["b0", "b1"])])

    def mainloop(self):
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = not pause
                        self.interactor.delegate = not pause
                        if pause:
                            self.field.halfstep()
                            self.renderer.refresh_picture()
                    elif event.key == pygame.K_r:
                        self.reset_inputs()
            if not pause:
                self.field.step()
                if self.renderer.is_picture_dirty():
                    self.renderer.refresh_picture()

            pygame.display.flip()
            sleep(((pygame.mouse.get_pos()[1] + 1) / 600.) ** 2)


if __name__ == "__main__":
    fe = PyGameFrontend()
    fe.mainloop()
