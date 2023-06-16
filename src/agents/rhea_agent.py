"""
 This will provide implementations of core algorithms such as MCTS and RHEA
"""

from typing import List, Optional
import random

from agents.game_interfaces import SimplePlayerInterface, SimpleGameModel, StateTransitionListener


class RHEA(SimplePlayerInterface):
    def __init__(self, l: int = 5, n: int = 10, p_mut: float = 0.2, use_buffer: bool = True, discount: float = None):
        self.l = l
        self.n = n
        self.p_mut = p_mut
        self.use_buffer = use_buffer
        self.discount = discount
        self.current: List[float] = []
        self.listener: Optional[StateTransitionListener] = None

    def get_int_action(self, state: SimpleGameModel, action_float: float):
        return int(action_float * state.n_actions())

    def random_action_sequence(self) -> List[float]:
        return [random.random() for _ in range(self.l)]

    def mutate_sequence(self, seq: List[float]) -> List[float]:
        return [random.random() if random.random() < self.p_mut else x for x in seq]

    def score_state(self, state: SimpleGameModel, step: int) -> float:
        if self.discount is None:
            return state.score()
        else:
            discount = self.discount ** step
            return state.score() * discount

    def score(self, state: SimpleGameModel, seq: List[float]) -> float:
        noted_events = 0
        for step, action_float in enumerate(seq):
            if state.is_terminal():
                return self.score_state(state, step)
            action = self.get_int_action(state, action_float)
            # could delete this if listener not needed - it's a hook to better understand the algorithm or for learning
            if self.listener:
                next_state = state.child(action)
                self.listener.state_transition(state, action, next_state)
                state = next_state
                noted_events += 1
            else:
                state.act(action)
        # print(f"{noted_events=}, {state.score()=}")
        return self.score_state(state, len(seq))

    def get_action(self, model: SimpleGameModel) -> int:
        if self.use_buffer:
            self.current = self.current or self.random_action_sequence()
        else:
            self.current = self.random_action_sequence()

        for i in range(self.n):
            mutated_copy = self.mutate_sequence(self.current)
            current_scored = (self.current, self.score(model.copy_state(), self.current))
            mutated_scored = (mutated_copy, self.score(model.copy_state(), mutated_copy))
            if mutated_scored[1] >= current_scored[1]:
                self.current = mutated_scored[0]
        selected_action_float = self.current[0]
        self.current = self.current[1:]
        self.current.append(random.random())
        selected_action = self.get_int_action(model, selected_action_float)
        return selected_action
