#!/usr/bin/env/python
import pygame
import field
from time import sleep

class PyGameSurfaceRenderer(field.RendererBase):
    bgcol = pygame.Color("white")
    fieldcol = pygame.Color("gray")
    signalcol = pygame.Color("black")

    def __adjust(self, (x, y)):
        return (x - self.bounds.l * 10, y - self.bounds.u * 10)

    def __init__(self):
        self.update_bounds(field.BBox(0, 0, 20, 20))
        self.signals = set()
        self.removals = set()
        self.additions = set()
        self.nice_redraw = True
        self.update_field(frozenset())

    def update_bounds(self, bounds):
        print "update bounds:", bounds
        self.bounds = bounds
        self.bgsurf = pygame.Surface(
                ((bounds.r - bounds.l)*10 + 10, (bounds.d - bounds.u)*10 + 10))
        self.bgsurf.fill(self.bgcol)
        self.resultsurf = self.bgsurf.copy()

    def update_field(self, fieldset):
        self.field = fieldset
        self.resultsurf = self.bgsurf.copy()
        for x, y in self.field:
            self.resultsurf.fill(self.fieldcol,
                    pygame.Rect(*self.__adjust((x * 10, y * 10)) + (10, 10)))

    def add_actions(self, removals, additions):
        if len(set(removals) & self.additions) > 0:
            self.nice_redraw = True

        self.removals = self.removals.difference(additions)
        self.additions = self.additions.difference(removals)
        self.additions = self.additions.union(additions)
        self.removals = self.removals.union(removals)

    def is_picture_dirty(self):
        return self.nice_redraw

    def refresh_picture(self):
        for x, y in self.removals:
            self.resultsurf.fill(self.fieldcol,
                    pygame.Rect(*self.__adjust((x * 10, y * 10)) + (10, 10)))

        self.removals = set()

        for x, y in self.additions:
            self.resultsurf.fill(self.signalcol,
                    pygame.Rect(*self.__adjust((x * 10, y * 10)) + (10, 10)))

        self.additions = set()
        self.nice_redraw = False

testfielddata = """
          __    __               __
 __O____O______________O______O_____
          _     _                ___
                                  _
                                  _
          _                  __  ___
          _          _______________
         __                   _  __
         ___
          _    _
  _O___O___O______    __
          _    _____________
          _    ___    _
  _O___O__________      __
          _    _________________
          _      _      _
          _
          _
          _
         ___
        _ _ _       __
   O_O____ _____O______
        _ _ _       ___
         ___         _
          _         __
          _         ___
          _          _
         ___        ___
         ______________
          __        __
"""

class PyGameFrontend(object):
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.field = field.Field(data=testfielddata)
        self.renderer = PyGameSurfaceRenderer()
        self.field.attach_renderer(self.renderer)

    def mainloop(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.field.step()
            if self.renderer.is_picture_dirty():
                self.renderer.refresh_picture()
                self.screen.blit(self.renderer.resultsurf, (20, 20))

            pygame.display.flip()
            #sleep(0.001)


if __name__ == "__main__":
    fe = PyGameFrontend()
    fe.mainloop()
