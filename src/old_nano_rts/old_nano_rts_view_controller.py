from typing import List, Union

import pygame
import pygame.locals
from pygame import QUIT

from agents.game_interfaces import MultiUnitPlayerInterface, SimplePlayerInterface
from agents.rhea_agent import RHEA
from old_nano_rts.old_nano_rts_game import NanoRTSState, NanoRTSModel, NanoStateGenerator, NanoRTSParams


class NanoRTSView:
    #  todo: consider refactoring this a bit more: it should ideally draw from a state rather from a model
    DEFAULT_SIZE = 25
    BORDER = 3
    WALL_COLOR = (0, 0, 0, 50)
    # BG_COLOR = (50, 50, 50)
    # set a background colour with an alpha value to show a trace of the previous state
    BG_COLOR = (50, 50, 50, 230)
    UNIT_COLOR = (128, 128, 255)
    N_UNIT_COLORS = 5
    UNIT_COLORS = [(255 - i *30, i*30, 0) for i in range(N_UNIT_COLORS)]
    RESOURCE_COLOR = (125, 255, 128)
    START_COLOR = (255, 0, 0, 255)
    COLORS = [BG_COLOR, WALL_COLOR, UNIT_COLOR, RESOURCE_COLOR]

    def __init__(self, model: NanoRTSModel, size: int = DEFAULT_SIZE):
        # todo: add a location and scale to enable multiple views on the same screen
        self.model = model
        self.size = size
        self.width = model.params.grid_size
        self.height = model.params.grid_size

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
        for i, unit in enumerate(self.model.state.units):
            rect = self.xy_to_rect(unit.x, unit.y)
            pygame.draw.rect(screen, self.UNIT_COLORS[i % self.N_UNIT_COLORS], rect)
            # print(self.UNIT_COLORS[i % self.N_UNIT_COLORS])
        for location in self.model.state.resources.keys():
            rect = self.xy_to_rect(location[0], location[1])
            pygame.draw.rect(screen, self.RESOURCE_COLOR, rect)

    def view_size(self) -> List[int]:
        return [self.size * self.width, self.size * self.height]

    def draw_trajectory(self, screen, trajectory: List[NanoRTSState]):
        for state in trajectory:
            for unit in state.units:
                rect = self.xy_to_rect(unit.x, unit.y)
                pygame.draw.rect(screen, self.UNIT_COLOR, rect)
            for location in state.resources.keys():
                rect = self.xy_to_rect(location[0], location[1])
                pygame.draw.rect(screen, self.RESOURCE_COLOR, rect)

class NanoRTSController:
    def __init__(self, model: NanoRTSModel, agent: Union[SimplePlayerInterface, MultiUnitPlayerInterface],
                 frame_rate: int = 10):
        self.model = model
        self.agent = agent
        self.view = NanoRTSView(model)
        pygame.init()
        pygame.display.set_caption('Old Nano RTS')
        # Set up the drawing window
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.view.view_size())
        self.surface = pygame.Surface(self.view.view_size(), pygame.locals.SRCALPHA )
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
            print(self.step, "\t", self.model.score())
            self.step += 1

        # Done! Time to quit.
        pygame.quit()


def ftest_nano_rts_controller(player: Union[SimplePlayerInterface, MultiUnitPlayerInterface]) -> None:
    # state = NanoStateGenerator().generate()
    # state = NanoStateGenerator().generate_hand_designed()
    n_units = 1
    params = NanoRTSParams(n_units=n_units, grid_size=10, fuel_per_resource=50)
    state = NanoStateGenerator(params).generate_hand_designed()

    model = NanoRTSModel(state, params)
    controller = NanoRTSController(model, player, frame_rate=1)
    controller.run()


if __name__ == "__main__":
    # player = MultiUnitRandomPlayer()
    # player = RandomPlayer()
    player = RHEA(l=50, n=100, p_mut=0.25, discount=0.999)

    ftest_nano_rts_controller(player)
