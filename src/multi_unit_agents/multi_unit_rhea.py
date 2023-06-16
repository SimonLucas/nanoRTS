"""
 This will provide implementations of core algorithms such as MCTS and RHEA
"""

from __future__ import annotations

import copy
from typing import List, Optional
import random

from agents.game_interfaces import MultiUnitPlayerInterface, StateTransitionListener, \
    MultiUnitGameModel


class MultiUnitRHEA(MultiUnitPlayerInterface):
    def __init__(self, n_units: int, l: int = 5, n: int = 10, p_mut: float = 0.2):
        self.n_units = n_units
        self.l = l
        self.n = n
        self.p_mut = p_mut
        self.current: List[List[float]] = [self.random_action_sequence() for _ in range(n_units)]
        self.listener: Optional[StateTransitionListener] = None

    def get_int_actions(self, state: MultiUnitGameModel, action_floats: List[float]) -> List[int]:
        return [int(action_float * state.n_actions_unit_i(i)) for i, action_float in enumerate(action_floats)]

    def random_action_sequence(self) -> List[float]:
        return [random.random() for _ in range(self.l)]

    def mutate_sequence(self, seq: List[float]) -> List[float]:
        return [random.random() if random.random() < self.p_mut else x for x in seq]

    def mutate_sequence_array(self, seq_array: List[List[float]]) -> List[List[float]]:
        seq_index = random.randint(0, len(seq_array) - 1)
        seq_copy: List[List[float]] = copy.deepcopy(seq_array)
        seq_copy[seq_index] = self.mutate_sequence(seq_copy[seq_index])
        return seq_copy

    def score(self, state: MultiUnitGameModel, seq: List[List[float]]) -> float:
        for action_floats in zip(*seq):
            if state.is_terminal():
                return state.score()
            actions = self.get_int_actions(state, action_floats)
            state.combo_act(actions)
        return state.score()

    def get_actions(self, model: MultiUnitGameModel) -> List[int]:
        for i in range(self.n):
            mutated_copy = self.mutate_sequence_array(self.current)
            current_scored = (self.current, self.score(model.copy_state(), self.current))
            mutated_scored = (mutated_copy, self.score(model.copy_state(), mutated_copy))
            if mutated_scored[1] >= current_scored[1]:
                self.current = mutated_scored[0]
        selected_action_floats = [seq[0] for seq in self.current]
        self.current = [seq[1:] + [random.random()] for seq in self.current]
        selected_action = self.get_int_actions(model, selected_action_floats)
        return selected_action

