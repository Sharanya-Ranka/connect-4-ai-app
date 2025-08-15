import torch
import numpy as np
from scipy.special import softmax

from GameImplementation.game_state import MCTSGameState, GameState
from Agent.policy_and_value_model import (
    PolicyAndValueTrainer,
    PolicyAndValueFunction,
)
from config import debugObj


class DeepNNAndMCTSAgent:
    """
    Represents the "AlphaZero" like agent
    Consists of :
    Deep Neural Network: Evaluating states to provide estimated state value and policy (action) probabilities (proportional to how good the action is)
    An MCTS System: Monte Carlo Tree Search uses the policy of the NN as a 'bias' to inform its search, and then further refines the "goodness" values of actions.
                    MCTS uses the state value suggested by the NN as a shortcut to figure out what the result of a complete simulation from that state might be.

    Data generated from the NN + MCTS system is used to train the next iteration of the NN,
    this loop leads to the NN giving better estimates, and MCTS being better informed, so its search is in turn more effective
    """

    def __init__(self, config):
        """
        Initializes the NN used, keeps track of training data generated during self play
        """
        self.config = config
        self.agent_config = config["AGENT_CONFIG"]
        self.model_config = config["MODEL_CONFIG"]

        self.policy_value_function = PolicyAndValueFunction(self.model_config)
        self.uct_c_coeff = self.agent_config["UCT_C_COEFF"]

    def getNetworkOnlyStateValueAndActionProbabilities(self, state):
        """
        Returns the state value and action probability estimates from the Neural Network only.
        """
        state_value, action_probabilities = self.policy_value_function.evaluateFunction(
            state
        )

        # if debugObj.requireNetworkActualOp():
        #     print(f"Network Only output")
        #     print(
        #         f"State:\n{state}\nState value={state_value}\nAction Probabilities={action_probabilities}\n",
        #         flush=True,
        #     )

        return state_value, action_probabilities

    def getMCTSEmpiricalStateValueAndActionProbabilties(self, state, action_bias):
        """
        Returns the action probabilties estimates from the NN + MCTS system. MCTS uses action_bias (estimates from the NN only)
        to inform its search.
        Generates a Tree each time this is called, starting from the state it is given
        Conducts playouts (selection + expansion + simulation + backpropagation) NUM_PLAYOUTS times
        to accumulate 'refined' action probabilities and state values, and returns them
        """
        root_state = MCTSGameState.createMCTSState(state)
        root_state.prior = action_bias
        # breakpoint()

        num_playouts = self.agent_config["NUM_PLAYOUTS"]
        for playout_ind in range(num_playouts):
            # print(f"On playout {playout_ind}")
            leaf_state = self._MCTSSelection(root_state)
            self._MCTSExpansion(leaf_state)
            # result = self._MCTSSimulation(leaf_state)
            self._MCTSBackpropagation(leaf_state, leaf_state.v)
            # debugObj.updateSim()

        # Calculate empirical probabilities using uct scores
        final_empirical_probabilities = self.convertVisitsToEmpiricalProbabilities(
            root_state
        )

        return final_empirical_probabilities

    def convertVisitsToEmpiricalProbabilities(self, state):
        child_visits = np.array(
            [
                child.visits if child != None else 0
                for ind, child in enumerate(state.children)
            ]
        )

        empirical_probs = child_visits / child_visits.sum()

        # child_visits[illegal_moves] = -np.inf
        # empirical_probs = softmax(child_visits)
        if np.any(np.isnan(empirical_probs)):
            breakpoint()

        return empirical_probs

    def _MCTSSelection(self, root_state: MCTSGameState) -> MCTSGameState:
        """
        Performs the selection step in MCTS.
        Until you get to a leaf, choose an action based on its 'goodness' score
        Goodness score depends on the NN bias, and outcomes from previous playouts with an 'uncertainty benefit of doubt'
        """

        def getBiasedUCTScore(state: MCTSGameState):
            child_visits = np.array(
                [
                    child.visits if child != None else 0
                    for ind, child in enumerate(state.children)
                ]
            )
            child_qvals = np.array(
                [
                    child.q if child != None else -np.inf
                    for ind, child in enumerate(state.children)
                ]
            )

            uncertainty_based_prior = (
                state.prior * np.sqrt(child_visits.sum()) / (1 + child_visits)
            )
            move_uct_scores = child_qvals + self.uct_c_coeff * uncertainty_based_prior

            return move_uct_scores

        state = root_state

        while state.is_leaf != True and state.isTerminal() != True:
            # scores = getBiasedUCTScore(state) * (
            #     -1 if state.next_player == GameState.RED else 1
            # )
            scores = getBiasedUCTScore(state)
            best_action = np.argmax(np.array(scores, dtype=np.float32))

            state = state.children[best_action]

        return state

    def _MCTSExpansion(self, state: MCTSGameState):
        """
        Performs the expansion step in MCTS.
        We are at a leaf state, and need to add its children to the tree.
        Children are initialized with the bias provided by the NN.
        Note that in this game (s, a) implies a unique s' TODO complete
        """
        if state.isTerminal() == False:
            children_created = state.createChildrenStates()
            assert children_created == True

            for child in state.children:
                if child != None:
                    state_value, action_probabilities = (
                        self.getNetworkOnlyStateValueAndActionProbabilities(child.state)
                    )
                    child.prior = action_probabilities
                    child.v = state_value

    # def _MCTSSimulation(self, state: MCTSGameState) -> int:
    #     """
    #     Performs the simulation step in MCTS.
    #     Randomly chooses next actions (uninformed) until a terminal state is reached
    #     Returns the winner in the simulation
    #     """
    #     temp_state = state.state
    #     while temp_state.isTerminal() == False:
    #         available_moves = temp_state.possible_next_moves
    #         random_move = np.random.choice(available_moves)
    #         temp_state = temp_state.applyMove(random_move)

    #     return temp_state.getWinner()

    def _MCTSBackpropagation(self, leaf_state: MCTSGameState, result: float):
        state = leaf_state
        while state != None:
            state.visits += 1
            state.w += result * (
                1 if state.next_player == leaf_state.next_player else -1
            )
            state.q = state.w / state.visits
            state = state.parent

    def getActionWithInfo(self, state: GameState) -> dict:
        """
        Performs the backpropagation step in MCTS.
        Goes up the current branch, updating every state in the tree based on the outcome
        """
        state_value, action_bias = self.getNetworkOnlyStateValueAndActionProbabilities(
            state
        )
        empirical_action_probs = self.getMCTSEmpiricalStateValueAndActionProbabilties(
            state, action_bias
        )
        action = np.random.choice(state.cols, p=empirical_action_probs)
        # breakpoint()
        # print(f"Empirical action probs={empirical_action_probs}")
        action_info = dict(action=action, empirical_action_probs=empirical_action_probs)
        return action_info
