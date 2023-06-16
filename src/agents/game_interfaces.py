from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import List


class SimpleGameModel(ABC):
    @abstractmethod
    def n_actions(self) -> int:
        pass

    def get_actions(self) -> List[int]:
        return list(range(self.n_actions()))

    @abstractmethod
    def act(self, action: int) -> SimpleGameModel:
        pass

    @abstractmethod
    def score(self) -> float:
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        pass

    @abstractmethod
    def copy_state(self) -> SimpleGameModel:
        pass

    def child(self, action_index: int) -> SimpleGameModel:
        model_copy = copy.deepcopy(self)
        return model_copy.act(action_index)

    def children(self) -> List[SimpleGameModel]:
        return [self.child(i) for i in range(self.n_actions())]


class MultiUnitGameModel(SimpleGameModel):

    @abstractmethod
    def n_units(self) -> int:
        pass

    @abstractmethod
    def n_actions_unit_i(self, i: int) -> int:
        pass

    @abstractmethod
    def combo_act(self, action: List[int]) -> MultiUnitGameModel:
        pass

    def get_action_space(self) -> List[int]:
        return [self.n_actions_unit_i(i) for i in range(self.n_units())]


class SimplePlayerInterface(ABC):
    @abstractmethod
    def get_action(self, state: SimpleGameModel) -> int:
        pass

class MultiUnitPlayerInterface(ABC):
    @abstractmethod
    def get_actions(self, state: MultiUnitGameModel) -> List[int]:
        pass


class StateTransitionListener(ABC):
    @abstractmethod
    def state_transition(self, state: SimpleGameModel, action: int, next_state: SimpleGameModel) -> None:
        pass
