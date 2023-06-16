from __future__ import annotations

"""
Defines a very simple 'rts' game involving control of a number of units.
Coordination of the units gives a combinatorial action space which
provides a challenge, even given the simple rules of the game.
todo: test the minimal game - check that units move and collect resources
todo: implement standard game interfaces so that we can run RHEA etc on this game.

Need to have a variable number of units to control - can remove dead ones
from the list, no problem.  Ok, just randomly spawn some extra ones in
an empty slot.
"""
import copy
from dataclasses import dataclass
from typing import List, Dict, Tuple

from agents.game_interfaces import MultiUnitGameModel
from multi_unit_agents.multi_unit_random_agent import MultiUnitRandomPlayer
from stats.clock_decorator import clock


@dataclass(frozen=False)
class UnitState:
    """
    Defines the state of a single unit.
    """
    x: int
    y: int
    fuel: int

# todo: make a resource class to handle resources of a different type
class Resource:
    pass


@dataclass(frozen=False)
class NanoRTSState:
    """
    Defines the state of the game.
    In the simplest case we can just use a list of unit states and a list
    of resources.  The rules of the game can then be applied.
    """
    units: List[UnitState]
    resources: Dict[Tuple[int, int], int]


@dataclass(frozen=False)
class NanoRTSParams:
    """
    Defines all the game parameters
    """
    n_units: int = 5
    n_resources: int = 10
    fuel_per_unit: int = 20
    fuel_per_resource: int = 100
    fuel_per_move: int = 2
    fuel_per_nop: int = 0
    grid_size: int = 10
    fuel_tank_capacity = 150


class NanoStateGenerator:
    """
    Generates states for the game.
    """

    def __init__(self, params: NanoRTSParams = None):
        self.params = params or NanoRTSParams()

    def generate(self) -> NanoRTSState:
        """
        Generates a state for the game.
        For now set this deterministically but random would be a better option
        """
        p = self.params
        units = [UnitState(i, i, p.fuel_per_unit) for i in range(p.n_units)]
        resources = {(p.grid_size/2, p.grid_size - i): p.fuel_per_resource for i in range(p.n_resources)}
        return NanoRTSState(units, resources)

    def generate_hand_designed(self) -> NanoRTSState:
        """
        Generates a specific state for the game.  This is useful for particular experiments.
        """
        p = self.params
        units = [UnitState(6, 4, p.fuel_per_unit)]
        resources = {
            (1, 2): p.fuel_per_resource,
            (1, 7): p.fuel_per_resource,
        }
        return NanoRTSState(units, resources)


class NanoRTSModel(MultiUnitGameModel):
    """
    Defines the rules of the game.
    """
    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
    actions_per_unit = len(moves)

    def __init__(self, state: NanoRTSState, params: NanoRTSParams = None):
        self.state = state or NanoStateGenerator(params).generate()
        self.params = params or NanoRTSParams()

    def n_actions(self) -> int:
        # number of actions is exponential in the number of units
        return self.actions_per_unit ** len(self.state.units)

    def action_to_move(self, action: int) -> (int, int):
        """
        Converts an action into a move.
        """
        move = self.moves[action % self.actions_per_unit]
        return move

    # todo: finish implementation of the game model

    # todo: introduce the spawning of new units in response to resource collection

    def update_unit(self, unit: UnitState, move: (int, int)) -> UnitState:
        """
        Updates state single unit and checks for collisions with resources
        """
        unit.x = (unit.x + move[0]) % self.params.grid_size
        unit.y = (unit.y + move[1]) % self.params.grid_size
        resource = self.state.resources.get((unit.x, unit.y))
        # this deletes the resource from the state,
        # but we could also just transfer a unit of fuel
        if resource:
            unit.fuel += resource
            if unit.fuel > self.params.fuel_tank_capacity:
                unit.fuel = self.params.fuel_tank_capacity
            del self.state.resources[(unit.x, unit.y)]
        if move == (0, 0):
            unit.fuel -= self.params.fuel_per_nop
        else:
            unit.fuel -= self.params.fuel_per_move
        return unit

    def score(self) -> float:
        """
        Returns the score of the game as the sum of the fuel held by the units.
        """
        return sum([unit.fuel for unit in self.state.units])

    def combo_act(self, action_list: List[int]) -> NanoRTSModel:
        """
        Applies an action_list to the game state.
        """
        if self.is_terminal():
            return self
        for i, unit in enumerate(self.state.units):
            move = self.action_to_move(action_list[i])
            self.update_unit(unit, move)
        return self

    def is_terminal(self) -> bool:
        return not self.state.resources or self.score() <= 0

    # implement: act, copy_state, n_actions_unit_i, n_units

    def act(self, action: int) -> NanoRTSModel:
        # the actions for each unit are combined in this single int
        # so we need to split them up
        action_list = []
        for i in range(self.n_units()):
            action_list.append(action % self.actions_per_unit)
            action = action // self.actions_per_unit
        self.combo_act(action_list)
        return self

    def copy_state(self) -> MultiUnitGameModel:
        return copy.deepcopy(self)

    def n_actions_unit_i(self, i: int) -> int:
        return len(self.moves)

    def n_units(self) -> int:
        return len(self.state.units)


def test():
    state_generator = NanoStateGenerator()
    state = state_generator.generate()
    print(state)
    model = NanoRTSModel(state)
    print(model.n_actions())
    print(f"Score: {model.score()}")


@clock
def speed_test(n_steps: int = 100000):
    state_generator = NanoStateGenerator()
    state = state_generator.generate()
    print(state)
    model = NanoRTSModel(state)
    player = MultiUnitRandomPlayer()
    for i in range(n_steps):
        actions = player.get_actions(model)
        model.combo_act(actions)
    print(state)
    print(model.score())


if __name__ == '__main__':
    test()
    print("Speed test:")
    speed_test()
