import mock
from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from Agent.policy_and_value_model import PolicyAndValueFunction
from GameImplementation.game_state import MCTSGameState, GameState
import numpy as np
from typing import List


class RandomAgent(DeepNNAndMCTSAgent):
    def __init__(self, config):
        self.config = config

    def getActionWithInfo(self, state: GameState) -> dict:
        possible_moves = state.possible_next_moves
        action_probs = np.zeros(state.cols)
        action_probs[np.random.choice(possible_moves)] = 1

        return dict(empirical_action_probs=action_probs)


class DummyPolicyValueFunction(PolicyAndValueFunction):
    def __init__(self, config):
        self.config = config

    def updateModelIter(self):
        pass

    def _evaluateFunctionBatched(self, states: List[GameState]):
        state_predictions = [self._evaluateFunction(state) for state in states]
        state_values = np.concatenate([sv for sv, sp in state_predictions], axis=0)
        state_priors = np.concatenate([sp for sv, sp in state_predictions], axis=0)

        return state_values, state_priors

    def _evaluateFunction(self, state: GameState):
        possible_moves = state.possible_next_moves
        action_probs = np.zeros(state.cols)
        action_probs[np.array(possible_moves)] = 1 / len(possible_moves)

        return np.array([0]), action_probs

    def _getPolicyAndValueNetwork(self):
        return None


class UniformPriorMCTSAgent(DeepNNAndMCTSAgent):
    def __init__(self, config):
        self.config = config
        self.agent_config = config["AGENT_CONFIG"]
        self.model_config = config["MODEL_CONFIG"]

        self.policy_value_function = DummyPolicyValueFunction({})
        self.uct_c_coeff = self.agent_config["UCT_C_COEFF"]

        # self.use_caching = self.agent_config['USE_CACHING']
        self.state_cache = {}
