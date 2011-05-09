#!/usr/bin/env python
from __future__ import print_function
import pygame
import field
from time import sleep
from math import log
import field_data

pxs = 10

class PyGameSurfaceRenderer(field.RendererBase):
    bgcol = pygame.Color("white")
    fieldcol = pygame.Color("gray")
    signalcol = pygame.Color("black")
    fontcol = pygame.Color("black")
    indicatorcol = pygame.Color("red")

    def __adjust(self, (x, y)):
        return (x - self.bounds.l * pxs, y - self.bounds.u * pxs)

    def __init__(self):
        self.font = pygame.font.SysFont("bitstreamverasans", pxs)
        self.update_bounds(field.BBox(0, 0, 20, 20))
        self.signals = set()
        self.removals = set()
        self.additions = set()
        self.nice_redraw = False
        self.background_redraw = True
        self.update_labels({})
        self.update_field(frozenset())

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
        self.bgsurf = pygame.Surface(
                ((self.bounds.r - self.bounds.l)*pxs + pxs,
                 (self.bounds.d - self.bounds.u)*pxs + pxs))
        self.bgsurf.fill(self.bgcol)

        for x, y in self.field:
            self.bgsurf.fill(self.fieldcol,
                    pygame.Rect(*self.__adjust((x * pxs, y * pxs)) + (pxs, pxs)))

        for (label, (pos, tgtpos)) in self.labels.iteritems():
            fontsurf = self.font.render(label, True, self.fontcol)
            self.bgsurf.blit(fontsurf, (pos[0] * pxs, pos[1] * pxs))
            xdiff = pos[0] - tgtpos[0]
            ydiff = pos[1] - tgtpos[1]
            dr = pygame.Rect(
                tgtpos[0] * pxs + (pxs * 0.8 if xdiff > 0 else 0),
                tgtpos[1] * pxs + (pxs * 0.8 if ydiff > 0 else 0),
                pxs * (0.2 if xdiff != 0 else 1),
                pxs * (0.2 if ydiff != 0 else 1))
            self.bgsurf.fill(self.indicatorcol, dr)

        self.resultsurf = self.bgsurf.copy()

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

class PyGameFrontend(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.setup_field()

    def setup_field(self):
        self.field = field.Field(data=field_data.xor_drjoin)
        self.renderer = PyGameSurfaceRenderer()
        self.field.attach_renderer(self.renderer)

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
            if not pause:
                self.field.step()
            if self.renderer.is_picture_dirty():
                self.renderer.refresh_picture()
                self.screen.blit(self.renderer.resultsurf, (20, 20))

            pygame.display.flip()
            sleep(log(pygame.mouse.get_pos()[1] / 300. + 1))


if __name__ == "__main__":
    fe = PyGameFrontend()
    fe.mainloop()
