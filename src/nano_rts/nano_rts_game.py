
from __future__ import annotations

from enum import IntEnum, auto

"""
Defines a very simple 'rts' game involving control of a number of units,
where we have units of different types and their interactions defined in
some flexible way.  Each unit will also have a unique id.

Coordination of the units gives a combinatorial action space which
provides a challenge, even given the simple rules of the game.
todo: test the minimal game - check that units move and collect resources
todo: implement standard game interfaces so that we can run RHEA etc on this game.

"""
import copy
from dataclasses import dataclass
from typing import List, Dict, Tuple

from agents.game_interfaces import MultiUnitGameModel


# define an enum for the unit types
class UnitType(IntEnum):
    """
    Defines the types of units in the game
    """
    Worker = auto()
    Resource = auto()
    Base = auto()


@dataclass(frozen=False)
class UnitState:
    """
    Defines the state of a single unit.
    """
    x: int
    y: int
    fuel: int
    type: UnitType
    player_id: int
    unit_id: int
    action: int = 0


@dataclass(frozen=False)
class NanoRTSState:
    """
    Defines the state of the game.
    In the simplest case we can just use a list of unit states and a list
    of resources.  The rules of the game can then be applied.
    """
    units: Dict[int, UnitState]

class IdGenerator:
    """
    Generates unique ids for units
    """
    def __init__(self):
        self._id = 0

    def get_id(self) -> int:
        self._id += 1
        return self._id

    def __call__(self, *args, **kwargs):
        return self.get_id()
def generate_sample_state() -> NanoRTSState:
    id_gen = IdGenerator()
    units = [
        UnitState(7, 4, 10, UnitType.Base, 1, id_gen(), 4),
        UnitState(1, 2, 10, UnitType.Worker, 0, id_gen(), 1),
        UnitState(2, 2, 10, UnitType.Worker, 1, id_gen(), 3),
        UnitState(3, 3, 10, UnitType.Resource, 2, id_gen(), 0),
    ]
    unit_dict = {u.unit_id: u for u in units}
    return NanoRTSState(unit_dict)

@dataclass(frozen=False)
class NanoRTSParams:
    """
    Defines all the game parameters
    """
    fuel_per_unit: int = 20
    fuel_per_resource: int = 100
    fuel_per_move: int = 2
    fuel_per_nop: int = 0
    grid_size: int = 10
    fuel_tank_capacity = 150

class NanoRTSModel(MultiUnitGameModel):

    def __init__(self, state: NanoRTSState, params: NanoRTSParams = None) -> None:
        self.state = state
        self.params = params or NanoRTSParams()

    def n_units(self) -> int:
        return len(self.state.units)

    def n_actions(self) -> int:
        return 4

    def copy_state(self) -> NanoRTSModel:
        return copy.deepcopy(self)

    def is_terminal(self) -> bool:
        return False

    def act(self, action: int) -> MultiUnitGameModel:
        pass

    def combo_act(self, action: List[int]) -> MultiUnitGameModel:
        pass
    def unit_act(self, unit_id: int, action: int) -> MultiUnitGameModel:
        # extract the required unit
        unit = self.state.units[unit_id]
        # apply the action: we have two types, move and act (collect, attack, etc)
        if unit:
            unit.action = action
            # compute the effects of the action

        return self

    def score(self) -> float:
        pass

    def n_actions_unit_i(self, i: int) -> int:
        return 4


