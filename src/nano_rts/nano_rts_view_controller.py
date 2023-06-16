from __future__ import annotations

from typing import List, Union

import pygame
import pygame.locals
from pygame import QUIT

from agents.game_interfaces import MultiUnitPlayerInterface, SimplePlayerInterface
from multi_unit_agents.multi_unit_random_agent import MultiUnitRandomPlayer
from nano_rts.nano_rts_game import NanoRTSModel, generate_sample_state, UnitType, UnitState


class NanoUnitView:
    """
    implement drawing methods for each type of unit
    the unit state is passed in as a parameter
    drawing will depend on the player id as well as the unit type
    """
    PLAYER_COLORS = [(255, 0, 0), (0, 0, 255), (128, 128, 128)]
    UNIT_TYPE_COLORS = {
        UnitType.Base: (128, 255, 0),
        UnitType.Worker: (255, 255, 255),
        UnitType.Resource: (255, 255, 0),
    }
    RECT_UNITS = {UnitType.Base, UnitType.Resource}
    CIRCLE_UNITS = {UnitType.Worker}
    LEN = 0.8
    ACTION_OFFSETS = [(0, 0), (LEN, 0), (0, LEN), (-LEN, 0), (0, -LEN)]

    def __init__(self, size: int) -> None:
        self.size = size
        self.border = size // 8
        self.line_width = size // 10

    def xy_to_rect(self, x: int, y: int, border: int):
        rect_x = self.size * x + border
        rect_y = self.size * y + border
        size = self.size - 2 * border
        return (rect_x, rect_y, size, size)

    def draw(self, screen: pygame.Surface, unit: UnitState) -> None:
        """
        draw a unit on the screen
        :param screen: the screen to draw on
        :param unit: the unit to draw
        :return: None
        We draw each unit with two rectangles or circles
        The first is the background, which is the player colour.
        The second is the foreground, which is the unit type colour.
        """
        bg_rect = self.xy_to_rect(unit.x, unit.y, 0)
        fg_rect = self.xy_to_rect(unit.x, unit.y, self.border)
        # center is used in drawing action lines and for circles
        center = (self.size * unit.x + self.size // 2, self.size * unit.y + self.size // 2)

        if unit.type in self.RECT_UNITS:
            pygame.draw.rect(screen, self.PLAYER_COLORS[unit.player_id], bg_rect)
            pygame.draw.rect(screen, self.UNIT_TYPE_COLORS[unit.type], fg_rect)

        elif unit.type in self.CIRCLE_UNITS:
            bg_radius = self.size // 2
            fg_radius = self.size // 2 - self.border
            pygame.draw.circle(screen, self.PLAYER_COLORS[unit.player_id], center, bg_radius)
            pygame.draw.circle(screen, self.UNIT_TYPE_COLORS[unit.type], center, fg_radius)

        # draw the action as a straight line in the player's color connecting the unit
        # center to the action destination centre
        if unit.action > 0:
            action_offset = self.ACTION_OFFSETS[unit.action]
            action_x = self.size * (unit.x + action_offset[0]) + self.size // 2
            action_y = self.size * (unit.y + action_offset[1]) + self.size // 2
            pygame.draw.line(screen, self.PLAYER_COLORS[unit.player_id],
                             center, (action_x, action_y), self.line_width)


class NanoRTSView:
    #  todo: consider refactoring this a bit more: it should ideally draw from a state rather from a model
    DEFAULT_SIZE = 50
    BORDER = 3
    WALL_COLOR = (0, 0, 0, 50)
    # BG_COLOR = (50, 50, 50)
    # set a background colour with an alpha value to show a trace of the previous state
    BG_COLOR = (50, 50, 50, 230)
    UNIT_COLOR = (128, 128, 255)
    N_UNIT_COLORS = 5
    UNIT_COLORS = [(255 - i * 30, i * 30, 0) for i in range(N_UNIT_COLORS)]
    RESOURCE_COLOR = (125, 255, 128)
    START_COLOR = (255, 0, 0, 255)
    COLORS = [BG_COLOR, WALL_COLOR, UNIT_COLOR, RESOURCE_COLOR]

    def __init__(self, model: NanoRTSModel, size: int = DEFAULT_SIZE):
        # todo: add a location and scale to enable multiple views on the same screen
        self.model = model
        self.size = size
        self.width = model.params.grid_size
        self.height = model.params.grid_size
        self.unit_view = NanoUnitView(size)

    def ix_to_x(self, ix: int) -> int:
        return ix % self.width

    def ix_to_y(self, ix: int) -> int:
        return ix // self.width

    def xy_to_rect(self, x: int, y: int):
        rect_x = self.size * x + self.BORDER
        rect_y = self.size * y + self.BORDER
        size = self.size - 2 * self.BORDER
        return (rect_x, rect_y, size, size)

    def ix_to_rect(self, ix: int):
        return self.xy_to_rect(self.ix_to_x(ix), self.ix_to_y(ix))

    def draw_grid(self, screen):
        # fill the background, then draw the grid, then the state items individually
        # screen.set_alpha(20)
        screen.fill(self.BG_COLOR)
        for x in range(self.width):
            for y in range(self.height):
                rect = self.xy_to_rect(x, y)
                pygame.draw.rect(screen, self.WALL_COLOR, rect, self.BORDER)
        for id, unit in self.model.state.units.items():
            self.unit_view.draw(screen, unit)

    def view_size(self) -> List[int]:
        return [self.size * self.width, self.size * self.height]


class NanoRTSController:
    def __init__(self, model: NanoRTSModel, agent: Union[SimplePlayerInterface, MultiUnitPlayerInterface],
                 frame_rate: int = 10):
        self.model = model
        self.agent = agent
        self.view = NanoRTSView(model)
        pygame.init()
        pygame.display.set_caption("Nano RTS")
        # Set up the drawing window
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.view.view_size())
        self.surface = pygame.Surface(self.view.view_size(), pygame.locals.SRCALPHA)
        self.frame_rate = frame_rate
        self.step = 0

    def run(self):
        running: bool = True

        while not self.model.is_terminal() and running:
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.view.draw_grid(self.surface)

            if isinstance(self.agent, MultiUnitPlayerInterface):
                actions = self.agent.get_actions(self.model)
                self.model.combo_act(actions)
            else:
                action = self.agent.get_action(self.model)
                self.model.act(action)

            # Flip the display
            self.screen.blit(self.surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(self.frame_rate)
            # print(self.step, "\t", self.model.score())
            self.step += 1

        # Done! Time to quit.
        pygame.quit()


if __name__ == "__main__":
    player = MultiUnitRandomPlayer()
    # player = RHEA(l=50, n=100, p_mut=0.25, discount=0.999)
    state = generate_sample_state()
    model = NanoRTSModel(state)
    controller = NanoRTSController(model, player)
    controller.run()
