import random
from typing import List

from agents.game_interfaces import MultiUnitPlayerInterface, MultiUnitGameModel


class MultiUnitRandomPlayer(MultiUnitPlayerInterface):
    def get_actions(self, model: MultiUnitGameModel) -> List[int]:
        return [random.randrange(model.n_actions_unit_i(i)) for i in range(model.n_units())]

