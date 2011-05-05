#!/usr/bin/env/python
import pygame
import field

class PyGameSurfaceRenderer(field.RendererBase):
    bgcol = pygame.Color("white")
    fieldcol = pygame.Color("gray")
    signalcol = pygame.Color("black")

    def __adjust(self, (x, y)):
        return (x - self.bounds.l, y - self.bounds.u)

    def __init__(self):
        self.update_bounds(field.BBox(0, 0, 20, 20))
        self.signals = set()
        self.removals = set()
        self.additions = set()
        self.nice_redraw = True
        self.update_field(frozenset())

    def update_bounds(self, bounds):
        self.bounds = bounds
        self.bgsurf = pygame.Surface(
                ((bounds.r - bounds.l)*10, (bounds.d - bounds.u)*10))
        self.resultsurf = self.bgsurf.copy()
        self.surf.fill(pygame.Color("black"))

    def update_field(self, fieldset):
        self.field = fieldset

    def add_actions(self, removals, additions):
        if len(removals & self.removals) > 0:
            self.nice_redraw = True

        self.removals -= additions
        self.additions -= removals
        self.additions |= additions
        self.removals |= removals

    def is_picture_dirty(self):
        return self.nice_redraw

    def refresh_picture(self):
        for x, y in self.removals:
            self.resultsurf.fill(self.fieldcol,
                    pygame.Rect(*self.__adjust((x, y)) + (10, 10)))

        self.removals = set()
            
        for x, y in self.additions:
            self.resultsurf.fill(self.signalcol,
                    pygame.Rect(*self.__adjust((x, y)) + (10, 10)))

        self.additions = set()
        self.nice_redraw = False

testfielddata = """\
          __    __
 __O____O______________O______O__
          _      _
"""

class PyGameFrontend(object):
    def __init__(self):
        self.screen = pygame.display.display.set_mode((800, 600))
        self.field = field.Field(data=testfielddata)
        self.renderer = PyGameSurfaceRenderer()
        self.field.attach_renderer(self.renderer)

    def mainloop(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.event.QUIT:
                    running = False
            self.field.step()
            if self.renderer.is_picture_dirty():
                self.renderer.refresh_picture()
                self.screen.blit(self.renderer.resultsurf, (20, 20))
            
            pygame.display.flip()
