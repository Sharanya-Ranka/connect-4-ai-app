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

        # self.use_caching = self.agent_config['USE_CACHING']
        self.state_cache = {}

    def getNetworkOnlyStateValueAndActionProbabilities(self, state):
        """
        Returns the state value and action probability estimates from the Neural Network only.
        """
        state_value, action_probabilities = (
            self.policy_value_function._evaluateFunction(state)
        )
        return state_value, action_probabilities

    def getNetworkOnlyStateValueAndActionProbabilitiesBatchedMode(self, states):
        """
        Returns the state value and action probability estimates from the Neural Network only.
        """
        # print(f"Batched evaluation with {len(states)} examples")

        state_value, action_probabilities = (
            self.policy_value_function._evaluateFunctionBatched(states)
        )

        return state_value, action_probabilities

    def performMCTSBatchedMode(self, state: GameState):
        to_evaluate_lazily = []
        to_backprop_lazily = []

        root_state = MCTSGameState.createMCTSState(state)

        if root_state.state in self.state_cache:
            value, prior = self.state_cache[root_state.state]
            root_state.prior = prior
            root_state.v = value
        else:
            to_evaluate_lazily.append(root_state)

        # breakpoint()
        num_playouts = self.agent_config["NUM_PLAYOUTS"]
        for playout_ind in range(num_playouts):
            # if playout_ind == 1:
            #     breakpoint()
            # print(f"On playout {playout_ind}")
            leaf_state = self._MCTSSelection(root_state)

            children = self._MCTSExpansionBatchedMode(leaf_state)

            for child in children:
                if child.state in self.state_cache:
                    value, prior = self.state_cache[child.state]
                    child.prior = prior
                    child.v = value
                else:
                    to_evaluate_lazily.append(child)

            if leaf_state in self.state_cache:
                leaf_state_value = self.getStateValue(leaf_state)
                # result = self._MCTSSimulation(leaf_state)
                self._MCTSBackpropagation(leaf_state, leaf_state_value)
            else:
                self._registerVirtualLoss(leaf_state)
                to_backprop_lazily.append(leaf_state)

            evaluated = self._checkLazyEvaluations(
                to_evaluate_lazily, to_backprop_lazily
            )
            if evaluated:
                to_evaluate_lazily.clear()
                to_backprop_lazily.clear()
            # debugObj.updateSim()
        self._checkLazyEvaluations(to_evaluate_lazily, to_backprop_lazily, force=True)

        # Calculate empirical probabilities using uct scores
        final_empirical_probabilities = self.convertVisitsToEmpiricalProbabilities(
            root_state
        )

        return final_empirical_probabilities

    def _checkLazyEvaluations(
        self, to_evaluate_lazily, to_backprop_lazily, force=False
    ):
        # breakpoint()
        if len(to_evaluate_lazily) >= self.agent_config["INFERENCE_MIN_BATCH_SIZE"] or (
            force == True and len(to_evaluate_lazily) > 0
        ):
            state_values, action_probabilities = (
                self.getNetworkOnlyStateValueAndActionProbabilitiesBatchedMode(
                    [mcts_state.state for mcts_state in to_evaluate_lazily]
                )
            )
            # breakpoint()

            for mcts_state, sv, ap in zip(
                to_evaluate_lazily, state_values, action_probabilities
            ):
                mcts_state: MCTSGameState
                mcts_state.prior = ap
                mcts_state.v =  sv

                self.state_cache[mcts_state.state] = (sv, ap)

            for leaf in to_backprop_lazily:
                self._reverseVirtualLoss(leaf_state=leaf)
                leaf_state_value = self.getStateValue(leaf)
                self._MCTSBackpropagation(leaf, leaf_state_value)

            # breakpoint()

            return True
        else:
            return False

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
            leaf_state_value = self.getStateValue(leaf_state)
            # result = self._MCTSSimulation(leaf_state)
            self._MCTSBackpropagation(leaf_state, leaf_state_value)
            # debugObj.updateSim()

        # Calculate empirical probabilities using uct scores
        final_empirical_probabilities = self.convertVisitsToEmpiricalProbabilities(
            root_state
        )

        # DEBUGGING
        # child_visits = np.array(
        #         [
        #             child.visits if child != None else 0
        #             for ind, child in enumerate(root_state.children)
        #         ]
        #     )

        # child_qvals = np.array(
        #         [
        #             child.q if child != None else -np.inf
        #             for ind, child in enumerate(root_state.children)
        #         ]
        #     )

        # print(f"Visits={child_visits}")
        # print(f"QVals={child_qvals}")
        # print(f"Biased UCT={self.getBiasedUCTScore(root_state)}")

        return final_empirical_probabilities

    def getStateValue(self, state):
        winner = state.getWinner()
        state_value = 0
        if winner == None:
            state_value = state.v
        elif winner == GameState.RED or winner == GameState.YELLOW:
            state_value = -1 if state.next_player == winner else 1

        # if state_value in [-1, 0, 1]:
        #     print(f"State=\n{state.state}\nIsTerminal?={state.isTerminal()}\nStateValue={state_value}")

        return state_value

    def convertVisitsToEmpiricalProbabilities(self, state):
        child_visits = np.array(
            [
                child.visits if child != None else 0
                for ind, child in enumerate(state.children)
            ]
        )
        # breakpoint()

        empirical_probs = child_visits / child_visits.sum()

        # child_visits[illegal_moves] = -np.inf
        # empirical_probs = softmax(child_visits)
        # if np.any(np.isnan(empirical_probs)):
        #     breakpoint()

        return empirical_probs

    def getBiasedUCTScore(self, state: MCTSGameState):
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
            state.prior * np.sqrt(child_visits.sum()) / (0.01 + child_visits)
        )
        move_uct_scores = child_qvals + self.uct_c_coeff * uncertainty_based_prior

        return move_uct_scores

    def _MCTSSelection(self, root_state: MCTSGameState) -> MCTSGameState:
        """
        Performs the selection step in MCTS.
        Until you get to a leaf, choose an action based on its 'goodness' score
        Goodness score depends on the NN bias, and outcomes from previous playouts with an 'uncertainty benefit of doubt'
        """
        state = root_state

        while state.is_leaf != True and state.isTerminal() != True:
            # scores = getBiasedUCTScore(state) * (
            #     -1 if state.next_player == GameState.RED else 1
            # )
            scores = self.getBiasedUCTScore(state)
            best_action = np.argmax(np.array(scores, dtype=np.float32))

            state = state.children[best_action]

        return state

    def _MCTSExpansionBatchedMode(self, state: MCTSGameState):
        """
        Performs the expansion step in MCTS.
        We are at a leaf state, and need to add its children to the tree.
        Children are initialized with the bias provided by the NN.
        Note that in this game (s, a) implies a unique s' TODO complete
        """
        valid_children = []
        if state.isTerminal() == False:
            children_created = state.createChildrenStates()
            assert children_created == True
            valid_children = [child for child in state.children if child is not None]

        return valid_children

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

    def _registerVirtualLoss(self, leaf_state):
        state = leaf_state
        while state != None:
            state.visits += 1
            # Modification from Backpropagation. All perspectives will register losses
            state.w += -1
            state.q = state.w / state.visits
            state = state.parent

    def _reverseVirtualLoss(self, leaf_state):
        state = leaf_state
        while state != None:
            # Remove the added visit when we registered a Virtual Loss
            state.visits -= 1
            # Correct the Virtual loss
            state.w += +1
            state.q = 0 if state.visits == 0 else state.w / state.visits
            state = state.parent

    # def _reverseVirtualLoss(self, leaf_state):

    def _MCTSBackpropagationMany(self, leaf_states, results):
        for leaf_state, result in zip(leaf_states, results):
            self._MCTSBackpropagation(leaf_state, result)

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
        if self.agent_config["USE_BATCHED_INFERENCE"] == True:
            return self.getActionWithInfoBatchedMode(state)
        else:
            return self.getActionWithInfoIndividualMode(state)

    def getActionWithInfoBatchedMode(self, state: GameState) -> dict:
        empirical_action_probs = self.performMCTSBatchedMode(state)
        # print(state)
        # print(empirical_action_probs)
        # print()
        action_info = dict(empirical_action_probs=empirical_action_probs)
        return action_info

    def getActionWithInfoIndividualMode(self, state: GameState) -> dict:
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
