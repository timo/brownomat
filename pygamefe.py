#!/usr/bin/env python
from __future__ import print_function
import pygame
import field
from time import sleep
import field_data
from random import choice, sample
from itertools import cycle
from tikz import TikzRenderer

add_col = lambda color, (r, g, b): pygame.Color(color.r + r, color.g + g, color.b + b)
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
            self.draw_block((x, y), self.signalcol)

        self.additions = set()
        self.nice_redraw = False

    def draw_block(self, (x, y), color):
        self.resultsurf.fill(color,
                pygame.Rect(*self.__adjust((x * 10, y * 10)) + (10, 10)))


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
        return self.choice[1]

    def reset(self):
        self._proxy.reset()
        self.choices = []
        self.choice = None

class PyGameFrontend(object):
    canvas_offset = (20, 20)
    def __init__(self, fieldtype="csequencer"):
        self.fieldtype = fieldtype
        pygame.init()
        self.interactor = PyGameInteractionPolicy()
        self.screen = pygame.display.set_mode((800, 600))
        self.setup_field()
        self.choices = cycle([(None, (None, None))])
        self.selected_choice = self.choices.next()
        self.backup_surf = None

    def setup_field(self):
        if self.fieldtype == "xor":
            data = field_data.xor_drjoin
        elif self.fieldtype == "drjoin":
            data = field_data.pathological_drjoin
        elif self.fieldtype == "csequencer":
            data = field_data.csequencer
        else:
            raise ValueError("invalid fieldtype %s" % self.fieltdype)

        self.field = field.Field(data=data, policy=self.interactor)

        self.renderer = PyGameSurfaceRenderer(self.screen, self.canvas_offset)
        self.field.attach_renderer(self.renderer)
        self.reset_inputs()

    def reset_inputs(self):
        if self.fieldtype == "xor":
            signals = [choice(["a0", "a1"]), choice(["b0", "b1"])]
        elif self.fieldtype == "drjoin":
            signals = sample("a0 a1 b0 b1".split(), 2)
        elif self.fieldtype == "csequencer":
            signals = choice((["c"], []))
            signals += sample(["a0", "a1"], choice([1, 2]))
        else:
            raise ValueError("invalid fieldtype %s" % self.fieldtype)

        print("setting inputs to %s" % (signals, ))
        self.field.reset(signals)

    def snapshot(self):
        self.backup_surf = self.renderer.resultsurf.copy()

    def restore_snapshot(self):
        self.renderer.resultsurf.blit(self.backup_surf, (0, 0))

    signal_removal_color = add_col(PyGameSurfaceRenderer.signalcol,
                                   (100, 0, 0))
    signal_addition_color = add_col(PyGameSurfaceRenderer.signalcol,
                                   (0, 0, 100))

    def draw_selected_action(self):
        field, (removals, additions) = self.selected_choice
        for pos in removals:
            self.renderer.draw_block(pos, self.signal_removal_color)
        for pos in additions:
            self.renderer.draw_block(pos, self.signal_addition_color)

    def next_paused_step(self):
        self.field.halfstep()
        self.renderer.refresh_picture()
        self.snapshot()
        self.choices = cycle(self.interactor.choices)
        self.selected_choice = self.choices.next()
        self.draw_selected_action()

    def mainloop(self):
        running = True
        pause = False
        action_blink = False
        recorder = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = not pause
                        self.interactor.delegate = not pause
                        if pause:
                            self.next_paused_step()
                        else:
                            self.restore_snapshot()
                    elif event.key == pygame.K_r:
                        if not pause:
                            self.reset_inputs()
                    elif event.key == pygame.K_n:
                        if pause:
                            self.restore_snapshot()
                            self.selected_choice = self.choices.next()
                            self.draw_selected_action()
                    elif event.key == pygame.K_t:
                        if pause:
                            self.interactor.choice = self.selected_choice
                            self.field.step()
                            self.next_paused_step()
                    elif event.key == pygame.K_1:
                        if recorder:
                            self.field.remove_renderer(recorder)
                            del recorder
                        recorder = TikzRenderer()
                        self.field.attach_renderer(recorder)
                    elif event.key == pygame.K_2:
                        if recorder:
                            self.field.remove_renderer(recorder)
                            del recorder

            if not pause:
                self.field.step()
                if self.renderer.is_picture_dirty():
                    self.renderer.refresh_picture()
            else:
                if action_blink:
                    self.restore_snapshot()
                else:
                    self.draw_selected_action()
                action_blink = not action_blink

            pygame.display.flip()
            sleep(((pygame.mouse.get_pos()[1] + 1) / 600.) ** 2)


if __name__ == "__main__":
    fe = PyGameFrontend()
    fe.mainloop()
